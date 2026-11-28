#!/usr/bin/env python3
"""Protected single-host runner. No production installation or credentials included."""
import argparse
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import socket
import sqlite3
import stat
import threading
import urllib.request
import urllib.parse
import uuid
from editorial_run_guard import slot_for, now_utc, WARNING_AFTER

POLICY = Path('/etc/future-pulse/runner.json')


def protected(path, owner, directory=False, owned_parent=None):
    path = Path(path)
    if not path.is_absolute() or path.resolve(strict=True) != path:
        raise PermissionError('absolute canonical path required')
    for p in [path, *path.parents]:
        s = p.lstat()
        expected = owner if p == path or (owned_parent is not None and p == Path(owned_parent)) else 0
        if stat.S_ISLNK(s.st_mode) or s.st_uid != expected or s.st_mode & 0o022:
            raise PermissionError('unsafe ownership/permissions: ' + str(p))
    if directory and not path.is_dir():
        raise PermissionError('directory required')


def authorize():
    protected(POLICY, 0)
    p = json.loads(POLICY.read_text())
    if (p.get('enabled') is not True or p.get('recovery_verified') is not True
            or os.geteuid() == 0 or p['runner_uid'] != os.geteuid()
            or p['editorial_uid'] in (0, os.geteuid())
            or p['machine_id'] != Path('/etc/machine-id').read_text().strip()):
        raise PermissionError('production gate closed / identity / recovery')
    protected(p['directory'], os.geteuid(), True)
    # Root-owned parent prevents replacing the socket. Dedicated broker must
    # validate SO_PEERCRED; runner ownership permits connecting without a shared group.
    protected(p['broker'], os.geteuid())
    if not stat.S_ISSOCK(Path(p['broker']).stat().st_mode):
        raise PermissionError('broker socket required')
    protected(p['code_directory'], 0, True)
    if Path(__file__).resolve().parent != Path(p['code_directory']):
        raise PermissionError('untrusted runner code location')
    for name in ('editorial_runner.py', 'editorial_run_guard.py', 'editorial_workflow.py'):
        protected(Path(p['code_directory']) / name, 0)
    protected(Path(p['directory']) / 'journal.sqlite', os.geteuid(), owned_parent=p['directory'])
    from editorial_workflow import protected_socket
    for endpoint in p['workflow_sockets'].values():
        protected_socket(endpoint)
    return p


def initialize(directory):
    """OFFLINE provisioning only; runtime never recreates a missing journal."""
    db = sqlite3.connect(Path(directory) / 'journal.sqlite')
    db.executescript('''PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL;
      CREATE TABLE runs(id TEXT PRIMARY KEY,slot TEXT UNIQUE,started TEXT,head TEXT,
                        phase TEXT,pr INTEGER,merge_sha TEXT);
      CREATE TABLE active(singleton INTEGER PRIMARY KEY CHECK(singleton=1),run TEXT UNIQUE);
      CREATE TABLE intents(run TEXT,op TEXT,status TEXT,PRIMARY KEY(run,op));
      CREATE TABLE workflow(run TEXT PRIMARY KEY, head TEXT, digest TEXT);
      CREATE TABLE notices(run TEXT,kind TEXT,PRIMARY KEY(run,kind));''')
    db.close()


class Runner:
    """Library seam for offline doubles. Production entry point always authorizes first.

    Runner identity/code/state must be inaccessible to editorial identities; this
    Python seam is NOT a security boundary against the same UID or root.
    """
    def __init__(self, directory, remote, notify=print, hook=lambda point: None):
        self.lock = open(Path(directory) / 'process.lock', 'a')
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.db = sqlite3.connect('file:' + str(Path(directory) / 'journal.sqlite') + '?mode=rw', uri=True)
            self.db.execute('PRAGMA synchronous=FULL')
            self.db.execute('PRAGMA integrity_check').fetchone() == ('ok',) or self.fail('corrupt journal')
            self.remote, self.notify, self.hook = remote, notify, hook
        except BaseException:
            self.lock.close()
            raise

    def fail(self, message):
        raise RuntimeError(message)

    def close(self):
        self.db.close()
        self.lock.close()

    def start(self, head, moment=None):
        if len(head) != 40 or any(c not in '0123456789abcdef' for c in head):
            self.fail('exact head required')
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            if self.db.execute('SELECT run FROM active').fetchone():
                self.fail('active run requires reconciliation; no expiry')
            rid = str(uuid.uuid4())
            self.db.execute('INSERT INTO runs VALUES(?,?,?,?,?,?,?)',
                            (rid, slot_for(moment or now_utc()), (moment or now_utc()).isoformat(), head, 'claimed', None, None))
            self.db.execute('INSERT INTO active VALUES(1,?)', (rid,))
        self.hook('claimed')
        return rid

    def row(self, rid):
        row = self.db.execute('SELECT * FROM runs WHERE id=?', (rid,)).fetchone()
        if not row or self.db.execute('SELECT run FROM active').fetchone() != (rid,):
            self.fail('not active')
        return dict(zip(('id','slot','started','head','phase','pr','merge_sha'), row))

    def notice(self, rid, moment=None):
        r = self.row(rid)
        if (moment or now_utc()) - dt.datetime.fromisoformat(r['started']) >= WARNING_AFTER:
            with self.db:
                first = self.db.execute('INSERT OR IGNORE INTO notices VALUES(?,?)', (rid,'90m')).rowcount
            if first:
                try:
                    self.notify({'run':rid,'warning':'90m','blocking':False})
                except Exception:
                    print(json.dumps({'run':rid,'warning':'90m','notification_failed':True}), flush=True)

    def operation(self, rid, op, action):
        with self.db:
            if self.db.execute('SELECT 1 FROM intents WHERE run=? AND op=?', (rid,op)).fetchone():
                self.fail('ambiguous or completed intent: reconcile only')
            self.db.execute('INSERT INTO intents VALUES(?,?,?)', (rid,op,'pending'))
        self.hook('before_' + op)
        action()  # response is not evidence: always independently re-read
        self.hook('after_' + op)
        with self.db:
            self.db.execute('UPDATE intents SET status=? WHERE run=? AND op=?', ('sent',rid,op))

    def reconcile(self, rid):
        r = self.row(rid)
        if r['phase'] == 'workflow_running':
            self.fail('workflow completion uncertain; operator fencing/recovery required')
        proof = self.remote.inspect(r)  # network/errors/ambiguous results leave active untouched
        if proof is None:
            if r['phase'] != 'claimed' or r['pr'] is not None:
                self.fail('previously recorded PR disappeared')
            return r
        if proof['head'] != r['head'] or (r['pr'] and proof['pr'] != r['pr']):
            self.fail('PR/head identity mismatch')
        if r['merge_sha'] and proof.get('merge_sha') != r['merge_sha']:
            self.fail('merge identity changed')
        phase = 'pr_open'
        merge = proof.get('merge_sha')
        if proof.get('merged'):
            if not merge:
                self.fail('missing merge commit evidence')
            phase = 'deployed' if proof.get('deployed') else 'merged'
        elif r['phase'] in ('merged','deployed'):
            self.fail('remote regression')
        with self.db:
            self.db.execute('UPDATE runs SET phase=?,pr=?,merge_sha=? WHERE id=?', (phase,proof['pr'],merge,rid))
            if phase == 'deployed':
                self.db.execute('DELETE FROM active WHERE run=?', (rid,))
        return dict(r, phase=phase, pr=proof['pr'], merge_sha=merge)

    def complete_workflow(self, rid, result):
        r=self.row(rid)
        if (result.get('head')!=r['head'] or result.get('role')!='review'
                or result.get('artifact',{}).get('approved') is not True):
            self.fail('invalid workflow completion')
        with self.db:
            self.db.execute('INSERT INTO workflow VALUES(?,?,?)',(rid,r['head'],result['digest']))
            self.db.execute("UPDATE runs SET phase='claimed' WHERE id=?",(rid,))

    def advance(self, rid):
        r=self.row(rid)
        if not self.db.execute('SELECT 1 FROM workflow WHERE run=? AND head=?',(rid,r['head'])).fetchone():
            self.fail('publication requires completed isolated workflow')
        self.notice(rid)
        r = self.reconcile(rid)
        if r['phase'] == 'claimed':
            self.operation(rid, 'pr', lambda: self.remote.create(r))
            r = self.reconcile(rid)
        if r['phase'] == 'pr_open':
            if not self.remote.ready(r):
                self.fail('review / checks / draft / mergeability gate closed')
            self.operation(rid, 'merge', lambda: self.remote.merge(r))
            r = self.reconcile(rid)
        if r['phase'] == 'deployed':
            try:
                self.notify({'run':rid, 'published':r['merge_sha']})
            except Exception:
                print(json.dumps({'run':rid,'published':r['merge_sha'],'notification_failed':True}), flush=True)
        return r


class GitHubReadAdapter:
    """Actual read-only GitHub REST evidence; effects belong to isolated broker."""
    def __init__(self, repository, branch, token=None):
        if len(repository.split('/')) != 2:
            raise ValueError('owner/repo required')
        self.repository, self.branch, self.token = repository, branch, token

    def get(self, path):
        req = urllib.request.Request('https://api.github.com/repos/' + self.repository + path,
                                     headers={'Accept':'application/vnd.github+json','User-Agent':'future-pulse-runner'})
        if self.token:
            req.add_header('Authorization', 'Bearer ' + self.token)
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)

    def pages(self, path):
        result = []
        for page in range(1, 101):
            data = self.get(path + ('&' if '?' in path else '?') + f'per_page=100&page={page}')
            result.extend(data)
            if len(data) < 100:
                return result
        raise RuntimeError('incomplete GitHub pagination')

    def inspect(self, r):
        # A marker is metadata, never evidence of creation. No receipt means no PR.
        if not r.get('pr') or not r.get('creator'):
            return None
        marker = 'future-pulse-run:' + r['id']
        p = self.get('/pulls/' + str(r['pr']))
        if (p['number'] != r['pr'] or p['user']['id'] != r['creator']
                or (p.get('body') or '').splitlines().count(marker) != 1
                or p['head']['repo']['full_name'] != self.repository or p['base']['repo']['full_name'] != self.repository
                or p['base']['ref'] != self.branch or p['head']['sha'] != r['head']):
            raise RuntimeError('foreign PR/head/base')
        if p['state'] == 'closed' and p['merged'] is not True:
            raise RuntimeError('PR closed without merge')
        merged = p['merged'] is True
        sha = p.get('merge_commit_sha') if merged else None
        deployed = False
        if merged:
            for deployment in self.pages('/deployments?sha=' + urllib.parse.quote(sha)):
                if deployment['sha'] == sha and deployment['environment'] == 'github-pages':
                    statuses = self.pages('/deployments/' + str(deployment['id']) + '/statuses')
                    if statuses and statuses[0]['state'] == 'success':
                        deployed = True
        return {'pr':p['number'],'creator':p['user']['id'],'head':p['head']['sha'],'merged':merged,'merge_sha':sha,'deployed':deployed}

    def ready(self, r):
        # Broker independently enforces required checks, hash-bound independent review,
        # exact SHA and server rules; no client-side boolean can grant permission.
        return False


class BrokerAdapter(GitHubReadAdapter):
    def __init__(self, policy):
        super().__init__(policy['repository'], policy['base'])
        self.broker = policy['broker']

    def request(self, op, r):
        with socket.socket(socket.AF_UNIX) as s:
            s.settimeout(30)
            s.connect(self.broker)
            s.sendall((json.dumps({'operation':op,'run':r}) + '\n').encode())
            with s.makefile('rb') as f:
                reply = json.loads(f.readline(65537))
        if reply.get('allowed') is not True:
            raise RuntimeError('broker denied')
        return reply

    def inspect(self, r):
        return self.request('inspect', r)['proof']

    def ready(self, r):
        return self.request('verify', r).get('head') == r['head']

    def create(self, r):
        self.request('create_pr', r)

    def merge(self, r):
        self.request('merge', r)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['run','start','advance','reconcile'])
    parser.add_argument('--head')
    parser.add_argument('--run')
    args = parser.parse_args()
    runner = None
    try:
        p = authorize()  # no db override, env switch, test mode or timestamp override
        runner = Runner(p['directory'], BrokerAdapter(p))
        if args.action == 'start':
            result = {'run':runner.start(args.head or '')}
        elif args.action == 'reconcile':
            result = runner.reconcile(args.run)
        else:
            if args.action == 'run':
                args.run = runner.start(args.head or '')
                with runner.db:
                    runner.db.execute("UPDATE runs SET phase='workflow_running' WHERE id=?", (args.run,))
            stop = threading.Event()
            def heartbeat():
                # Separate read-only connection: warning remains active during slow I/O.
                warned = False
                while not stop.wait(1):
                    try:
                        with sqlite3.connect('file:' + str(Path(p['directory']) / 'journal.sqlite') + '?mode=ro', uri=True) as db:
                            row = db.execute('SELECT started FROM runs WHERE id=?', (args.run,)).fetchone()
                        if row and not warned and now_utc() - dt.datetime.fromisoformat(row[0]) >= WARNING_AFTER:
                            print(json.dumps({'run':args.run,'warning':'90m','blocking':False}), flush=True)
                            warned = True
                    except Exception as e:
                        print(json.dumps({'monitor_error':str(e)}), flush=True)
                        return
            thread = threading.Thread(target=heartbeat, daemon=True)
            thread.start()
            try:
                if args.action == 'run':
                    from editorial_workflow import execute
                    result = execute(p,runner.row(args.run))
                    runner.complete_workflow(args.run,result)
                result = runner.advance(args.run)
            finally:
                stop.set()
                thread.join()

        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({'allowed':False,'error':str(e)}))
        return 2
    finally:
        if runner:
            runner.close()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
