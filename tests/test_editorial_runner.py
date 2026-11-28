import datetime as dt
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import editorial_runner as m
HEAD = 'a' * 40
TIME = dt.datetime.fromisoformat('2026-11-27T08:00:00+00:00')


class Remote:
    def __init__(self, directory):
        self.file = Path(directory) / 'remote.json'
    def inspect(self, r):
        return json.loads(self.file.read_text()) if self.file.exists() else None
    def ready(self, r):
        return True
    def create(self, r):
        self.file.write_text(json.dumps(dict(pr=1, head=r['head'], merged=False)))
    def merge(self, r):
        self.file.write_text(json.dumps(dict(pr=1, head=r['head'], merged=True, merge_sha='b'*40, deployed=True)))


class ApprovedRunner(m.Runner):
    """Fixture: completed independent workflow for publication-only unit tests."""
    def start(self,*args,**kw):
        rid=super().start(*args,**kw)
        self.complete_workflow(rid,{'role':'review','head':HEAD,'artifact':{'approved':True},'digest':'fixture'})
        return rid


class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)
        m.initialize(self.path)
        self.remote = Remote(self.path)
    def tearDown(self):
        self.tmp.cleanup()
    def runner(self, **kw):
        return ApprovedRunner(self.path, self.remote, **kw)
    def test_A01_parallel_manual_and_different_slot(self):
        r = self.runner()
        rid = r.start(HEAD, TIME)
        with self.assertRaises(BlockingIOError): self.runner()
        code = 'import sys;sys.path.insert(0,sys.argv[1]);import editorial_runner as m;m.Runner(sys.argv[2],None)'
        p = subprocess.run([sys.executable,'-c',code,str(SCRIPTS),str(self.path)], capture_output=True)
        self.assertNotEqual(p.returncode,0)
        r.close()
        r = self.runner()
        with self.assertRaises(RuntimeError): r.start(HEAD,TIME+dt.timedelta(days=4))
        r.close()
    def test_A02_A10_A11_gate_bypass(self):
        # Independent environment/journal cannot select itself via CLI/env.
        other = self.path / 'other'; other.mkdir(); m.initialize(other)
        for args in (['start','--head',HEAD], ['start','--db',str(other/'journal.sqlite')]):
            p = subprocess.run([sys.executable,str(SCRIPTS/'editorial_runner.py'),*args],
                env=dict(os.environ,FUTURE_PULSE_RUN_DB=str(other/'journal.sqlite')),capture_output=True)
            self.assertNotEqual(p.returncode,0)
        with patch.object(m,'POLICY',self.path/'missing'):
            with self.assertRaises(FileNotFoundError): m.authorize()
        policy = self.path/'policy'; policy.write_text('{}'); policy.chmod(0o666)
        with patch.object(m,'POLICY',policy):
            with self.assertRaises(PermissionError): m.authorize()
    def test_policy_identity_host_recovery_and_code_location(self):
        # Deterministic unit probes of enforcement; not an installed identity boundary.
        policy = dict(enabled=True,recovery_verified=True,runner_uid=1001,editorial_uid=1002,
            machine_id='authorized-host',directory=str(self.path),broker=str(self.path/'broker'),
            code_directory=str(SCRIPTS),repository='owner/repo',base='main',workflow_sockets={})
        (self.path/'broker').touch()
        def read(path, *args, **kw):
            return 'authorized-host' if str(path)=='/etc/machine-id' else json.dumps(policy)
        with patch.object(m,'protected'), patch.object(m.os,'geteuid',return_value=1001), \
             patch.object(m.Path,'read_text',read), patch.object(m.stat,'S_ISSOCK',return_value=True):
            self.assertEqual(m.authorize()['runner_uid'],1001)
            for field, bad in [('enabled',False),('recovery_verified',False),('machine_id','other-host'),
                               ('runner_uid',1003),('editorial_uid',1001),('editorial_uid',0)]:
                old=policy[field]; policy[field]=bad
                with self.assertRaises(PermissionError): m.authorize()
                policy[field]=old
            policy['code_directory']='/untrusted'
            with self.assertRaises(PermissionError): m.authorize()
    def test_recorded_pr_disappears_no_merge(self):
        r=self.runner();rid=r.start(HEAD,TIME);self.remote.create(r.row(rid));r.reconcile(rid)
        self.remote.file.unlink()
        with self.assertRaises(RuntimeError):r.advance(rid)
        self.assertEqual(r.db.execute('SELECT count(*) FROM intents').fetchone()[0],0)
        r.close()
    def crash(self, point):
        # Real SIGKILL, remote file survives process death, journal committed first.
        code = '''import sys,os,signal
sys.path[:0]=[sys.argv[1],sys.argv[2]]
import editorial_runner as m
from test_editorial_runner import Remote,HEAD,TIME,ApprovedRunner
p=sys.argv[3]
def hook(point):
 if point==sys.argv[4]: os.kill(os.getpid(),signal.SIGKILL)
r=ApprovedRunner(p,Remote(p),hook=hook)
rid=r.start(HEAD,TIME)
r.advance(rid)
'''
        p = subprocess.run([sys.executable,'-c',code,str(SCRIPTS),str(Path(__file__).parent),str(self.path),point],capture_output=True)
        self.assertEqual(p.returncode,-signal.SIGKILL,p.stderr)
        r = self.runner()
        rid = r.db.execute('SELECT run FROM active').fetchone()[0]
        return r,rid
    def test_A03_A09_kill_after_claim_and_timeout(self):
        r,rid = self.crash('claimed')
        with self.assertRaises(RuntimeError): r.start(HEAD,TIME+dt.timedelta(days=4))
        r.notice(rid,TIME+dt.timedelta(seconds=14400))
        self.assertEqual(r.row(rid)['phase'],'claimed'); r.close()
    def test_A04_before_pr(self):
        r,rid = self.crash('before_pr')
        with self.assertRaises(RuntimeError): r.advance(rid)
        self.assertFalse(self.remote.file.exists()); r.close()
    def test_A04_after_pr(self):
        r,rid = self.crash('after_pr')
        self.assertEqual(r.reconcile(rid)['phase'],'pr_open')
        self.assertEqual(r.db.execute('SELECT count(*) FROM intents WHERE op="pr"').fetchone()[0],1)
        r.close()
    def test_A05_before_merge(self):
        r,rid = self.crash('before_merge')
        with self.assertRaises(RuntimeError): r.advance(rid)
        self.assertFalse(self.remote.inspect({})['merged']); r.close()
    def test_A05_A06_after_merge_reconciliation(self):
        r,rid = self.crash('after_merge')
        self.assertEqual(r.reconcile(rid)['phase'],'deployed')
        self.assertIsNone(r.db.execute('SELECT * FROM active').fetchone()); r.close()
    def test_A07_ambiguous_remote(self):
        r = self.runner(); rid=r.start(HEAD,TIME)
        with patch.object(self.remote,'inspect',side_effect=OSError('offline')):
            with self.assertRaises(OSError): r.advance(rid)
        self.assertEqual(r.row(rid)['phase'],'claimed')
        self.assertEqual(r.db.execute('SELECT count(*) FROM intents').fetchone()[0],0); r.close()
    def test_A08_warning_no_abort(self):
        notices=[]; r=self.runner(notify=notices.append); rid=r.start(HEAD,TIME)
        r.notice(rid,TIME+dt.timedelta(minutes=89)); self.assertEqual(notices,[])
        r.notice(rid,TIME+dt.timedelta(minutes=90)); self.assertEqual(len(notices),1)
        r.notice(rid,TIME+dt.timedelta(days=7)); self.assertEqual(len(notices),1)
        self.assertEqual(r.row(rid)['phase'],'claimed');r.close()
    def test_A12_notice_failure_no_republish(self):
        r=self.runner(notify=lambda x: (_ for _ in ()).throw(OSError()))
        rid=r.start(HEAD,TIME); self.assertEqual(r.advance(rid)['phase'],'deployed')
        with self.assertRaises(RuntimeError): r.advance(rid)
        self.assertEqual(r.db.execute('SELECT count(*) FROM intents').fetchone()[0],2);r.close()
    def test_missing_db_not_recreated(self):
        (self.path/'journal.sqlite').unlink()
        with self.assertRaises(Exception): self.runner()
    def test_read_adapter_evidence(self):
        a=m.GitHubReadAdapter('owner/repo','main'); r={'id':'run','head':HEAD,'pr':7,'creator':11}
        pr=dict(user={'id':11},state='closed',number=7,body='future-pulse-run:run',head={'sha':HEAD,'repo':{'full_name':'owner/repo'}},
            base={'ref':'main','repo':{'full_name':'owner/repo'}},merged=True,merge_commit_sha='b'*40)
        def get(path):
            if path.startswith('/pulls?'): return [pr]
            if path=='/pulls/7': return pr
            if path.startswith('/deployments?'): return [dict(id=3,sha='b'*40,environment='github-pages')]
            return [dict(state='success')]
        with patch.object(a,'get',side_effect=get):
            proof=a.inspect(r);self.assertTrue(proof['deployed']);self.assertEqual(proof['pr'],7)
            pr['head']['sha']='c'*40
            with self.assertRaises(RuntimeError):a.inspect(r)

if __name__=='__main__': unittest.main()
