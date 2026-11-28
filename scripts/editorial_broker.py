#!/usr/bin/env python3
"""Offline-delivered privileged publisher service; no installation or credentials bundled."""
import fcntl
import json
import os
from pathlib import Path
import socket
import sqlite3
import stat
import struct
import urllib.request

from editorial_runner import GitHubReadAdapter, protected

POLICY = Path('/etc/future-pulse/broker.json')


def authorize():
    protected(POLICY, 0)
    p = json.loads(POLICY.read_text())
    uid = os.geteuid()
    if (not uid or p.get('enabled') is not True or p.get('recovery_verified') is not True
            or p['broker_uid'] != uid or len({uid, p['runner_uid'], p['editorial_uid'], 0}) != 4
            or p['machine_id'] != Path('/etc/machine-id').read_text().strip()):
        raise PermissionError('broker gate closed')
    protected(p['directory'], uid, True)
    protected(Path(p['directory']) / 'broker.sqlite', uid, owned_parent=p['directory'])
    protected(p['code_directory'], 0, True)
    if Path(__file__).resolve().parent != Path(p['code_directory']):
        raise PermissionError('untrusted broker code')
    for name in ('editorial_broker.py', 'editorial_runner.py', 'editorial_run_guard.py', 'editorial_workflow.py'):
        protected(Path(p['code_directory']) / name, 0)
    protected(p['credential_file'], uid)
    if Path(p['credential_file']).stat().st_mode & 0o077:
        raise PermissionError('credential readable by other identities')
    # Socket parent belongs to root, never the connecting runner.
    protected(Path(p['socket']).parent, 0, True)
    protected(p['socket'], p['runner_uid'])
    if not stat.S_ISSOCK(Path(p['socket']).stat().st_mode):
        raise PermissionError('operator-provisioned socket required')
    if not p.get('reviewers') or not p.get('required_checks') or not p.get('ruleset_ids'):
        raise PermissionError('missing independent evidence policy')
    from editorial_workflow import protected_socket
    protected_socket(p['review_socket'])
    if p['review_uid'] in (0,p['runner_uid'],p['broker_uid'],p['editorial_uid']):
        raise PermissionError('independent workflow reviewer required')
    return p


def initialize(directory):
    """Operator-only offline provisioning. Runtime never initializes missing state."""
    db = sqlite3.connect(Path(directory) / 'broker.sqlite')
    db.executescript('''PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL;
      CREATE TABLE claims(run TEXT PRIMARY KEY, slot TEXT UNIQUE, head TEXT, payload TEXT);
      CREATE TABLE receipts(run TEXT PRIMARY KEY, pr INTEGER UNIQUE, creator INTEGER);
      CREATE TABLE active(id INTEGER PRIMARY KEY CHECK(id=1), run TEXT);
      CREATE TABLE operations(run TEXT, op TEXT, status TEXT, PRIMARY KEY(run,op));''')
    db.close()


class GitHubWriteAdapter(GitHubReadAdapter):
    """Only the broker holds this adapter/token; tests use a fake instead."""
    def __init__(self, policy, token):
        super().__init__(policy['repository'], policy['base'], token)
        self.policy = policy

    def write(self, method, path, payload):
        req = urllib.request.Request('https://api.github.com/repos/' + self.repository + path,
            data=json.dumps(payload).encode(), method=method,
            headers={'Authorization': 'Bearer ' + self.token, 'Accept': 'application/vnd.github+json',
                     'Content-Type': 'application/json', 'User-Agent': 'future-pulse-broker'})
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)

    def create(self, r):
        branch = self.policy['source_branch']
        if self.get('/git/ref/heads/' + branch)['object']['sha'] != r['head']:
            raise RuntimeError('source head changed')
        created = self.write('POST', '/pulls', {'head':branch, 'base':self.branch,
            'title':'Future Pulse editorial run', 'body':'future-pulse-run:' + r['id'], 'draft':True})
        if created['user']['id'] != self.policy['publisher_id']:
            raise RuntimeError('unexpected PR creator')
        return {'pr':created['number'], 'creator':created['user']['id']}

    def evidence(self, r, proof):
        p = self.get('/pulls/' + str(proof['pr']))
        head = r['head']
        if (p['number'] != proof['pr'] or p['user']['id'] != proof['creator']
                or (p.get('body') or '').splitlines().count('future-pulse-run:' + r['id']) != 1
                or p['head']['sha'] != head or p['draft'] is not False or p['state'] != 'open'
                or p['merged'] is not False or p['mergeable'] is not True
                or p['mergeable_state'] != 'clean' or p['base']['ref'] != self.branch
                or p['head']['repo']['full_name'] != self.repository
                or p['base']['repo']['full_name'] != self.repository):
            raise RuntimeError('PR not eligible')
        reviews = self.pages('/pulls/' + str(proof['pr']) + '/reviews')
        latest = {}
        for review in sorted(reviews, key=lambda x: x['id']):
            if review['state'] != 'COMMENTED':
                latest[review['user']['login']] = review
        approved = [v for k,v in latest.items() if k in self.policy['reviewers']
                    and k != p['user']['login'] and v['state'] == 'APPROVED'
                    and v['commit_id'] == head]
        if not approved or any(v['state'] == 'CHANGES_REQUESTED' for v in latest.values()):
            raise RuntimeError('independent head-bound review missing')
        checks = self.get('/commits/' + head + '/check-runs?per_page=100')
        if checks['total_count'] > 100:
            raise RuntimeError('incomplete check evidence')
        for required in self.policy['required_checks']:
            matches = [c for c in checks['check_runs'] if c['name'] == required['name']
                       and c['app']['id'] == required['app_id']]
            if (len(matches) != 1 or matches[0]['head_sha'] != head
                    or matches[0]['status'] != 'completed' or matches[0]['conclusion'] != 'success'):
                raise RuntimeError('required check missing/ambiguous/failing')
        rules = self.get('/rules/branches/' + self.branch)
        ids = set()
        for rule in rules:
            ids.add(rule['ruleset_id'])
        if not set(self.policy['ruleset_ids']).issubset(ids):
            raise RuntimeError('required branch rules absent')
        for rid in self.policy['ruleset_ids']:
            rs = self.get('/rulesets/' + str(rid))
            types = {x['type'] for x in rs['rules']}
            if (rs['enforcement'] != 'active' or rs.get('bypass_actors')
                    or not {'pull_request','required_status_checks'}.issubset(types)):
                raise RuntimeError('ruleset inactive/bypassable/incomplete')
            for rule in rs['rules']:
                params = rule.get('parameters', {})
                if rule['type'] == 'pull_request' and (
                        params.get('required_approving_review_count', 0) < 1
                        or params.get('dismiss_stale_reviews_on_push') is not True
                        or params.get('require_last_push_approval') is not True):
                    raise RuntimeError('server review race protection absent')
                if rule['type'] == 'required_status_checks':
                    bound = {(c['context'], c.get('integration_id')) for c in params.get('required_status_checks', [])}
                    expected = {(c['name'], c['app_id']) for c in self.policy['required_checks']}
                    if params.get('strict_required_status_checks_policy') is not True or not expected.issubset(bound):
                        raise RuntimeError('server required checks incomplete')
        # Final read catches ordinary concurrent movement; atomic merge SHA is authoritative.
        if self.get('/pulls/' + str(proof['pr']))['head']['sha'] != head:
            raise RuntimeError('head moved')

    def merge(self, r, proof):
        result = self.write('PUT', '/pulls/' + str(proof['pr']) + '/merge',
                            {'sha':r['head'], 'merge_method':'squash'})
        if result.get('merged') is not True:
            raise RuntimeError('merge refused or ambiguous')


class Broker:
    def __init__(self, policy, remote, hook=lambda point: None):
        self.p, self.remote, self.hook = policy, remote, hook
        self.lock = open(Path(policy['directory']) / 'broker.lock', 'a')
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.db = sqlite3.connect('file:' + str(Path(policy['directory']) / 'broker.sqlite') + '?mode=rw', uri=True)
            self.db.execute('PRAGMA synchronous=FULL')
            if self.db.execute('PRAGMA integrity_check').fetchone() != ('ok',):
                raise RuntimeError('corrupt broker journal')
        except BaseException:
            self.lock.close()
            raise

    def close(self):
        self.db.close()
        self.lock.close()

    def workflow_evidence(self,r):
        from editorial_workflow import rpc,digest
        result=rpc(self.p['review_socket'],{'operation':'inspect','run':r})
        identity=digest({'id':r['id'],'slot':r['slot'],'head':r['head']})
        if (result['identity']!=identity or result['head']!=r['head']
                or result['role']!='review' or result['artifact'].get('approved') is not True
                or result['digest']!=digest(result['artifact'])):
            raise RuntimeError('missing independent workflow evidence')

    def request(self, uid, request):
        if uid != self.p['runner_uid']:
            raise PermissionError('unauthorized peer')
        r, op = request['run'], request['operation']
        if op not in ('inspect','verify','create_pr','merge'):
            raise ValueError('unknown operation')
        if (not isinstance(r['id'], str) or not r['id'] or len(r['id']) > 128
                or len(r['head']) != 40 or any(c not in '0123456789abcdef' for c in r['head'])):
            raise ValueError('invalid identity')
        # Broker does not trust runner's PR number, phase or merge SHA.
        canonical = {'id':r['id'], 'head':r['head'], 'slot':r['slot']}
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            old = self.db.execute('SELECT payload FROM claims WHERE run=?', (r['id'],)).fetchone()
            payload = json.dumps(canonical, sort_keys=True)
            if old and old[0] != payload:
                raise RuntimeError('run identity changed')
            active = self.db.execute('SELECT run FROM active').fetchone()
            if active and active != (r['id'],):
                raise RuntimeError('another active run; no expiry')
            if not old:
                self.db.execute('INSERT INTO claims VALUES(?,?,?,?)', (r['id'],r['slot'],r['head'],payload))
            self.db.execute('INSERT OR IGNORE INTO active VALUES(1,?)', (r['id'],))
        receipt = self.db.execute('SELECT pr,creator FROM receipts WHERE run=?', (r['id'],)).fetchone()
        if receipt:
            canonical.update(pr=receipt[0], creator=receipt[1])
        proof = self.remote.inspect(canonical)
        if proof and (not receipt or proof['pr'] != receipt[0] or proof['creator'] != receipt[1]):
            raise RuntimeError('PR without broker creation receipt / identity changed')
        if op == 'inspect':
            return {'allowed':True, 'proof':proof, 'head':r['head']}
        if proof and proof['head'] != r['head']:
            raise RuntimeError('remote identity mismatch')
        if proof and proof.get('merged') and proof.get('deployed'):
            with self.db:
                self.db.execute('DELETE FROM active WHERE run=?', (r['id'],))
            return {'allowed':True, 'head':r['head']}
        if op in ('verify','create_pr','merge'):
            self.workflow_evidence(canonical)
        if op == 'verify':
            if not proof or proof.get('merged'):
                raise RuntimeError('no open PR')
            self.remote.evidence(canonical, proof)
            return {'allowed':True, 'head':r['head']}
        existing = self.db.execute('SELECT status FROM operations WHERE run=? AND op=?', (r['id'],op)).fetchone()
        if existing:
            # Positive remote observation is the only permitted retry result, never re-send.
            if (op == 'create_pr' and proof) or (op == 'merge' and proof and proof.get('merged')):
                return {'allowed':True, 'head':r['head']}
            raise RuntimeError('ambiguous operation; operator reconciliation required')
        if op == 'create_pr' and proof:
            raise RuntimeError('unexpected existing PR')
        if op == 'merge':
            if not proof or proof.get('merged'):
                raise RuntimeError('no eligible PR')
            self.remote.evidence(canonical, proof)
        with self.db:
            self.db.execute('INSERT INTO operations VALUES(?,?,?)', (r['id'],op,'pending'))
        self.hook('before_' + op)
        if op == 'create_pr':
            created = self.remote.create(canonical)
            self.hook('after_effect_create_pr')
            if (not created or not isinstance(created['pr'], int)
                    or created['creator'] != self.p['publisher_id']):
                raise RuntimeError('missing trusted creation receipt')
            with self.db:
                self.db.execute('INSERT INTO receipts VALUES(?,?,?)',
                    (r['id'],created['pr'],created['creator']))
        else:
            self.remote.merge(canonical, proof)
        self.hook('after_' + op)
        with self.db:
            self.db.execute('UPDATE operations SET status=? WHERE run=? AND op=?', ('sent',r['id'],op))
        return {'allowed':True, 'head':r['head']}


def serve(policy):
    remote = GitHubWriteAdapter(policy, Path(policy['credential_file']).read_text().strip())
    broker = Broker(policy, remote)
    # Operator socket activation: nonroot broker cannot write root-owned parent.
    if (os.environ.get('LISTEN_PID') != str(os.getpid())
            or os.environ.get('LISTEN_FDS') != '1'):
        broker.close()
        raise PermissionError('operator socket activation required')
    with socket.fromfd(3, socket.AF_UNIX, socket.SOCK_STREAM) as server:
        try:
            if server.getsockname() != policy['socket'] or not server.getsockopt(socket.SOL_SOCKET, socket.SO_ACCEPTCONN):
                raise PermissionError('wrong activation socket')
            while True:
                with server.accept()[0] as client:
                    client.settimeout(30)
                    try:
                        _, uid, _ = struct.unpack('3i', client.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
                        if uid != policy['runner_uid']:
                            raise PermissionError('unauthorized peer')
                        with client.makefile('rb') as stream:
                            line = stream.readline(65537)
                        if len(line) > 65536 or not line.endswith(b'\n'):
                            raise ValueError('invalid frame')
                        reply = broker.request(uid, json.loads(line))
                    except Exception:
                        reply = {'allowed':False, 'error':'broker denied; inspect operator journal'}
                    try:
                        client.sendall((json.dumps(reply) + '\n').encode())
                    except OSError:
                        pass  # persistent intent survives disconnected client
        finally:
            broker.close()


if __name__ == '__main__':
    serve(authorize())
