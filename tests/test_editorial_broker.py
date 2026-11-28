import json
import os
from pathlib import Path
import signal
import socket
import struct
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import editorial_broker as b
import editorial_runner as runner

HEAD = 'a'*40
R = {'id':'run-1','slot':'2026-11-27','head':HEAD}

class Remote:
    def __init__(self, directory): self.path = Path(directory)/'remote'
    def inspect(self, r): return json.loads(self.path.read_text()) if self.path.exists() else None
    def create(self, r):
        self.path.write_text(json.dumps({'pr':1,'creator':11,'head':r['head'],'merged':False}))
        return {'pr':1,'creator':11}
    def evidence(self, r, proof): pass
    def merge(self, r, proof): self.path.write_text(json.dumps({'pr':1,'creator':11,'head':r['head'],'merged':True,'deployed':True}))

class FixtureBroker(b.Broker):
    """Publication unit seam; complete isolated worker path is tested separately."""
    def workflow_evidence(self,r): pass

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.d = Path(self.tmp.name)
        b.initialize(self.d)
        self.p = {'directory':str(self.d), 'runner_uid':os.getuid(),'publisher_id':11}
        self.remote = Remote(self.d)
    def tearDown(self): self.tmp.cleanup()
    def request(self, broker, op, r=None, uid=None):
        return broker.request(os.getuid() if uid is None else uid, {'operation':op,'run':r or R})
    def test_peer_credentials_and_second_environment(self):
        broker = FixtureBroker(self.p,self.remote)
        try:
            a,c = socket.socketpair()
            with a,c:
                _,uid,_ = struct.unpack('3i', a.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
                self.request(broker,'create_pr',uid=uid)
            with self.assertRaises(PermissionError): self.request(broker,'merge',uid=os.getuid()+1)
            with self.assertRaises(RuntimeError): self.request(broker,'create_pr',dict(R,id='other',slot='later'))
            with self.assertRaises(RuntimeError): self.request(broker,'merge',dict(R,head='b'*40))
            with self.assertRaises(BlockingIOError): FixtureBroker(self.p,self.remote)
        finally: broker.close()
    def test_crash_and_timeout_intents(self):
        # Persistent fake remote in another file, actual process death, never normal close.
        script = '''import sys,os,signal,time
sys.path.insert(0,sys.argv[1]);sys.path.insert(0,sys.argv[2])
import editorial_broker as b
from test_editorial_broker import Remote,R,FixtureBroker
p={'directory':sys.argv[3],'runner_uid':os.getuid(),'publisher_id':11}
def hook(point):
 if point==sys.argv[4]:
  if sys.argv[5]=='kill': os.kill(os.getpid(),signal.SIGKILL)
  time.sleep(60)
x=FixtureBroker(p,Remote(sys.argv[3]),hook)
x.request(os.getuid(),{'operation':sys.argv[6],'run':R})
'''
        for op in ('create_pr','merge'):
            for when in ('before_','after_'):
                for mode in ('kill','timeout'):
                    with self.subTest(op=op,when=when,mode=mode), tempfile.TemporaryDirectory() as d:
                        b.initialize(d); remote=Remote(d)
                        if op=='merge':
                            setup=FixtureBroker(dict(self.p,directory=d),remote)
                            self.request(setup,'create_pr'); setup.close()
                        cmd=[sys.executable,'-c',script,str(Path(b.__file__).parent),str(Path(__file__).parent),d,when+op,mode,op]
                        if mode=='timeout':
                            with self.assertRaises(subprocess.TimeoutExpired): subprocess.run(cmd,timeout=.5,capture_output=True)
                        else: self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,-signal.SIGKILL)
                        broker=FixtureBroker(dict(self.p,directory=d),remote)
                        try:
                            if when=='before_':
                                with self.assertRaises(RuntimeError): self.request(broker,op)
                            else: self.assertTrue(self.request(broker,op)['allowed'])
                            count=broker.db.execute('SELECT count(*) FROM operations').fetchone()[0]
                            self.assertEqual(count,1 if op=='create_pr' else 2)
                        finally: broker.close()
    @unittest.skipUnless(os.geteuid() == 0, 'requires ability to drop test subprocess identity')
    def test_real_other_identity_socket_denied(self):
        # No new account or permissions granted: child drops to numeric unprivileged UID.
        socket_tmp=tempfile.TemporaryDirectory(dir='/tmp')
        Path(socket_tmp.name).chmod(0o755)
        path=str(Path(socket_tmp.name)/'socket')
        broker=FixtureBroker(self.p,self.remote)
        with socket.socket(socket.AF_UNIX) as server:
            server.bind(path); os.chmod(path,0o666); server.listen(1)
            code="import os,socket,sys;os.setgid(65534);os.setuid(65534);s=socket.socket(socket.AF_UNIX);s.connect(sys.argv[1]);s.sendall(b'x');s.close()"
            child=subprocess.Popen([sys.executable,'-c',code,path])
            try:
                server.settimeout(5)
                with server.accept()[0] as client:
                    _,uid,_=struct.unpack('3i',client.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
                    self.assertEqual(uid,65534)
                    with self.assertRaises(PermissionError): self.request(broker,'create_pr',uid=uid)
                self.assertEqual(child.wait(timeout=5),0)
                self.assertEqual(broker.db.execute('SELECT count(*) FROM claims').fetchone()[0],0)
                self.assertFalse(self.remote.path.exists())
            finally:
                if child.poll() is None: child.kill(); child.wait()
                broker.close()
                socket_tmp.cleanup()
    def test_uncertain_editorial_workflow_cannot_be_reconciled(self):
        runner.initialize(self.d)
        import datetime as dt
        r=runner.Runner(self.d,self.remote)
        try:
            rid=r.start(HEAD,dt.datetime.fromisoformat('2026-11-27T08:00:00+00:00'))
            with r.db: r.db.execute("UPDATE runs SET phase='workflow_running' WHERE id=?",(rid,))
            with self.assertRaises(RuntimeError): r.reconcile(rid)
            self.assertFalse(self.remote.path.exists())
        finally: r.close()
    def test_unreceipted_pr_and_changed_creator_denied(self):
        self.remote.create(R) # Marker/head/PR alone are not proof of broker creation.
        broker=FixtureBroker(self.p,self.remote)
        try:
            for op in ('inspect','verify','create_pr','merge'):
                with self.assertRaises(RuntimeError): self.request(broker,op)
            self.assertEqual(broker.db.execute('SELECT count(*) FROM operations').fetchone()[0],0)
        finally:broker.close()
        self.remote.path.unlink()
        broker=FixtureBroker(self.p,self.remote)
        try:
            self.request(broker,'create_pr')
            data=json.loads(self.remote.path.read_text()); data['creator']=12
            self.remote.path.write_text(json.dumps(data))
            with self.assertRaises(RuntimeError): self.request(broker,'merge')
        finally:broker.close()
    def test_crash_after_effect_before_receipt_never_adopts_marker(self):
        script="""import sys,os,signal
sys.path[:0]=[sys.argv[1],sys.argv[2]]
from test_editorial_broker import Remote,R,FixtureBroker
def hook(point):
 if point=='after_effect_create_pr': os.kill(os.getpid(),signal.SIGKILL)
x=FixtureBroker({'directory':sys.argv[3],'runner_uid':os.getuid(),'publisher_id':11},Remote(sys.argv[3]),hook)
x.request(os.getuid(),{'operation':'create_pr','run':R})
"""
        child=subprocess.run([sys.executable,'-c',script,str(Path(b.__file__).parent),
            str(Path(__file__).parent),str(self.d)],capture_output=True)
        self.assertEqual(child.returncode,-signal.SIGKILL,child.stderr)
        broker=FixtureBroker(self.p,self.remote)
        try:
            self.assertTrue(self.remote.path.exists())
            self.assertEqual(broker.db.execute('SELECT count(*) FROM receipts').fetchone()[0],0)
            with self.assertRaises(RuntimeError):self.request(broker,'create_pr')
            with self.assertRaises(RuntimeError):self.request(broker,'merge')
        finally:broker.close()
    def test_missing_journal_closed(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(Exception): FixtureBroker(dict(self.p,directory=d),self.remote)
            self.assertFalse((Path(d)/'broker.sqlite').exists())
    def adapter(self):
        p={'repository':'org/repo','base':'main','source_branch':'candidate',
           'reviewers':['human'],'required_checks':[{'name':'pr-validation','app_id':7}], 'ruleset_ids':[9]}
        x=b.GitHubWriteAdapter(p,'fake-not-a-token')
        pr={'number':1,'body':'future-pulse-run:run-1','head':{'sha':HEAD,'repo':{'full_name':'org/repo'}},
            'base':{'ref':'main','repo':{'full_name':'org/repo'}},'draft':False,'state':'open','merged':False,
            'mergeable':True,'mergeable_state':'clean','user':{'id':11,'login':'author'}}
        data={'/pulls/1':pr,'/commits/'+HEAD+'/check-runs?per_page=100':{'total_count':1,'check_runs':[
            {'name':'pr-validation','app':{'id':7},'head_sha':HEAD,'status':'completed','conclusion':'success'}]},
            '/rules/branches/main':[{'ruleset_id':9}],'/rulesets/9':{'enforcement':'active','bypass_actors':[],
                'rules':[{'type':'pull_request','parameters':{'required_approving_review_count':1,
                    'dismiss_stale_reviews_on_push':True,'require_last_push_approval':True}},
                    {'type':'required_status_checks','parameters':{'strict_required_status_checks_policy':True,
                    'required_status_checks':[{'context':'pr-validation','integration_id':7}]}}]}}
        reviews=[{'id':1,'user':{'login':'human'},'state':'APPROVED','commit_id':HEAD}]
        x.get=lambda path:data[path]
        x.pages=lambda path:reviews
        return x,data,reviews
    def test_independent_review_checks_draft_rulesets(self):
        x,data,reviews=self.adapter(); x.evidence(R,{'pr':1,'creator':11})
        mutations=[lambda d,r:d['/pulls/1'].update(body='changed'),
            lambda d,r:d['/pulls/1'].update(draft=True),
            lambda d,r:r[0].update(commit_id='b'*40),lambda d,r:r[0]['user'].update(login='author'),
            lambda d,r:d['/rulesets/9'].update(enforcement='evaluate'),
            lambda d,r:d['/rulesets/9'].update(bypass_actors=[{'actor_id':1}]),
            lambda d,r:d['/commits/'+HEAD+'/check-runs?per_page=100']['check_runs'][0].update(conclusion='failure'),
            lambda d,r:d['/rules/branches/main'].clear()]
        for mutate in mutations:
            x,data,reviews=self.adapter(); mutate(data,reviews)
            with self.assertRaises(RuntimeError): x.evidence(R,{'pr':1,'creator':11})
    def test_exact_head_write_precondition(self):
        x,_,_=self.adapter(); calls=[]
        x.write=lambda *args:(calls.append(args) or {'merged':True})
        x.merge(R,{'pr':3})
        self.assertEqual(calls[0],('PUT','/pulls/3/merge',{'sha':HEAD,'merge_method':'squash'}))
    def test_marker_substring_and_changed_detail(self):
        x=runner.GitHubReadAdapter('org/repo','main')
        x.pages=lambda path:[{'number':1,'body':'future-pulse-run:run-1-extra'}]
        self.assertIsNone(x.inspect(R))
        x.pages=lambda path:[{'number':1,'body':'future-pulse-run:run-1'}]
        x.get=lambda path:{'number':1,'user':{'id':11},'body':'changed'}
        with self.assertRaises(RuntimeError): x.inspect(dict(R,pr=1,creator=11))

if __name__=='__main__': unittest.main()
