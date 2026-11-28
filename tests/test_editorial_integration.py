"""Ephemeral deployment fixture, not a host installation; no external network/effects."""
import datetime as dt
import json
import os
from pathlib import Path
import shutil
import socket
import sqlite3
import subprocess
import sys
import tempfile
import unittest

SOURCE=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SOURCE))
import editorial_runner as runner
import editorial_broker as broker
import editorial_workflow as workflow
HEAD='a'*40
UIDS=dict(runner_uid=61001,broker_uid=61002,research_uid=61003,writer_uid=61004,review_uid=61005)

SERVER='''import os,sys,json,time
sys.path.insert(0,sys.argv[1])
role=sys.argv[2]; policy=sys.argv[3]; fd=int(sys.argv[4]); delay=float(sys.argv[5])
os.dup2(fd,3);os.environ['LISTEN_PID']=str(os.getpid());os.environ['LISTEN_FDS']='1'
if role=='broker':
 import editorial_broker as b
 b.POLICY=__import__('pathlib').Path(policy)
 class FakeRemote:
  def __init__(self,p,token): self.path=__import__('pathlib').Path(p['directory'])/'remote.json'
  def inspect(self,r):
   if not r.get('pr'): return None
   return json.loads(self.path.read_text()) if self.path.exists() else None
  def create(self,r):
   self.path.write_text(json.dumps({'pr':7,'creator':99,'head':r['head'],'merged':False}))
   return {'pr':7,'creator':99}
  def evidence(self,r,proof): pass
  def merge(self,r,proof):
   self.path.write_text(json.dumps({'pr':7,'creator':99,'head':r['head'],'merged':True,'merge_sha':'b'*40,'deployed':True}))
 b.GitHubWriteAdapter=FakeRemote
 b.serve(b.authorize())
else:
 import editorial_workflow as w
 w.POLICY=__import__('pathlib').Path(policy)
 class FakeBackend:
  def __init__(self,p): self.p=p
  def sources(self):
   time.sleep(delay)
   return [{'url':'https://source.invalid','text':'offline source'}]
  def candidate(self,r): return 'verified article'
  def model(self,role,payload):
   return {'research':{'facts':['offline fact']},'writer':{'article':'verified article'},'review':{'approved':True,'reasons':['source matches']}}[role]
 w.Backend=FakeBackend
 old=w.Worker.request
 def traced(self,*a):
  try:return old(self,*a)
  except Exception:
   __import__('traceback').print_exc();raise
 w.Worker.request=traced
 w.serve(w.authorize())
'''
CLIENT='''import sys,json,os,datetime
sys.path.insert(0,sys.argv[1])
import editorial_runner as r
r.POLICY=__import__('pathlib').Path(sys.argv[2])
offset=int(sys.argv[4]);clock=[0]
def now():
 clock[0]+=1
 return datetime.datetime.fromisoformat('2026-11-27T08:00:00+00:00')+datetime.timedelta(minutes=offset if clock[0]>2 else 0)
r.now_utc=now
sys.argv=['editorial_runner',*json.loads(sys.argv[3])]
raise SystemExit(r.main())
'''

@unittest.skipUnless(os.geteuid()==0,'root required solely to drop ephemeral child identities')
class Integration(unittest.TestCase):
    def setUp(self):
        # /tmp is intentionally not accepted by production protected() traversal.
        # Private root-owned fixture has no .git or checkout; only deployed test scripts.
        self.tmp=tempfile.TemporaryDirectory(prefix='.neo-offline-test-',dir='/')
        self.root=Path(self.tmp.name); self.root.chmod(0o755)
        self.code=self.root/'code'; self.code.mkdir()
        for name in ('editorial_runner.py','editorial_run_guard.py','editorial_broker.py','editorial_workflow.py'):
            shutil.copyfile(SOURCE/name,self.code/name)
        self.children=[]; self.listeners=[]; self.listener_map={}
        self.sockets={role:str(self.root/(role+'.sock')) for role in ('research','writer','review')}
        self.states={}
        for role,uid in [('runner',61001),('broker',61002),('research',61003),('writer',61004),('review',61005)]:
            d=self.root/role; d.mkdir(); self.states[role]=d
            (runner.initialize if role=='runner' else broker.initialize if role=='broker' else workflow.initialize)(d)
            db=d/('journal.sqlite' if role=='runner' else 'broker.sqlite' if role=='broker' else 'workflow.sqlite')
            os.chown(db,uid,-1); db.chmod(0o600); os.chown(d,uid,-1); d.chmod(0o700)
        self.machine=Path('/etc/machine-id').read_text().strip()
        self.base=dict(UIDS,enabled=True,recovery_verified=True,machine_id=self.machine,
            editorial_uid=61004,code_directory=str(self.code),repository='org/repo',base='main')
        self.runner_policy=dict(self.base,directory=str(self.states['runner']),broker=str(self.root/'broker.sock'),
            workflow_sockets=self.sockets)
        self.write_policy('runner',self.runner_policy)
    def tearDown(self):
        for child in self.children:
            if child.poll() is None: child.kill()
            child.communicate(timeout=5)
        for listener in self.listeners: listener.close()
        self.tmp.cleanup()
    def write_policy(self,role,p):
        path=self.root/(role+'.json');path.write_text(json.dumps(p));path.chmod(0o644)
        return path
    def drop(self,uid):
        def f(): os.setgroups([]);os.setgid(uid);os.setuid(uid)
        return f
    def launch(self,role,p,uid,delay=0):
        path=self.runner_policy['broker'] if role=='broker' else self.sockets[role]
        listener=self.listener_map[role]
        policy=self.write_policy(role,p)
        child=subprocess.Popen([sys.executable,'-c',SERVER,str(self.code),role,str(policy),str(listener.fileno()),str(delay)],
            pass_fds=(listener.fileno(),),cwd='/',preexec_fn=self.drop(uid),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        self.children.append(child)
    def services(self,delay=0):
        # All activation sockets exist before any service validates peer endpoints.
        for role in ('research','writer','review','broker'):
            path=self.runner_policy['broker'] if role=='broker' else self.sockets[role]
            listener=socket.socket(socket.AF_UNIX);listener.bind(path);listener.listen(8)
            if role=='broker': os.chown(path,61001,-1);os.chmod(path,0o600)
            else: os.chmod(path,0o666)
            self.listeners.append(listener);self.listener_map[role]=listener
        for role in ('research','writer','review'):
            uid=UIDS[role+'_uid']; key=self.root/(role+'.key');key.write_text('offline-placeholder');os.chown(key,uid,-1);key.chmod(0o600)
            p=dict(self.base,role=role,directory=str(self.states[role]),credential_file=str(key),sockets=self.sockets)
            self.launch(role,p,uid,delay if role=='research' else 0)
        key=self.root/'broker.key';key.write_text('offline-placeholder');os.chown(key,61002,-1);key.chmod(0o600)
        p=dict(self.base,directory=str(self.states['broker']),socket=self.runner_policy['broker'],
            credential_file=str(key),review_socket=self.sockets['review'],publisher_id=99,
            reviewers=['human'],required_checks=[{'name':'pr-validation','app_id':7}],ruleset_ids=[9])
        self.launch('broker',p,61002)
    def client(self,args,uid=61001,offset=90):
        return subprocess.Popen([sys.executable,'-c',CLIENT,str(self.code),str(self.root/'runner.json'),json.dumps(args),str(offset)],
            cwd='/',preexec_fn=self.drop(uid),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    def result(self,args,uid=61001,offset=90):
        p=self.client(args,uid,offset);out,err=p.communicate(timeout=12)
        # Show service failures rather than hanging silently on a queued activation socket.
        for child in self.children:
            if child.poll() is not None:
                self.fail('service failed: '+child.communicate()[1].decode())
        return p.returncode,out.decode(),err.decode()
    def test_full_policy_activation_workflow_publication(self):
        self.services(delay=1.2)
        code,out,err=self.result(['run','--head',HEAD])
        
        if code!=0:
            errors=[]
            for child in self.children:
                child.kill();errors.append(child.communicate()[1].decode())
            self.fail((out,err,errors))
        self.assertIn('"warning": "90m"',out)
        self.assertIn('"phase": "deployed"',out)
        with sqlite3.connect(self.states['broker']/'broker.sqlite') as db:
            self.assertEqual(db.execute('SELECT pr,creator FROM receipts').fetchone(),(7,99))
        for role in ('research','writer','review'):
            with sqlite3.connect(self.states[role]/'workflow.sqlite') as db:
                self.assertEqual(db.execute('SELECT status FROM tasks').fetchone(),('complete',))
    def test_heartbeat_before_threshold_no_warning(self):
        self.services(delay=1.2)
        code,out,err=self.result(['run','--head',HEAD],offset=89)
        self.assertEqual(code,0,(out,err))
        self.assertNotIn('"warning"',out)
    def test_A02_A10_A11_gate_bypass_and_second_identity(self):
        self.services()
        self.assertNotEqual(self.result(['run','--head',HEAD],uid=61004)[0],0)
        # Same immutable policy, but another cwd/environment: no separate journal override.
        # Editorial identity cannot alter the operator gate or either service journal.
        probe="import sys;from pathlib import Path; failures=0\nfor p in sys.argv[1:]:\n try:Path(p).write_text('bypass')\n except PermissionError:failures+=1\nassert failures==len(sys.argv)-1"
        child=subprocess.run([sys.executable,'-c',probe,str(self.root/'runner.json'),
            str(self.states['runner']/'journal.sqlite'),str(self.states['broker']/'broker.sqlite')],
            cwd='/',preexec_fn=self.drop(61004),capture_output=True,timeout=5)
        self.assertEqual(child.returncode,0,child.stderr)

        # The caller cannot choose a different DB/code/identity via CLI.
        self.assertNotEqual(self.result(['run','--db','/tmp/elsewhere','--head',HEAD])[0],0)
        code,out,_=self.result(['start','--head',HEAD]);self.assertEqual(code,0,out)
        rid=json.loads(out.splitlines()[-1])['run']
        code,out,_=self.result(['advance','--run',rid]);self.assertNotEqual(code,0)
        self.assertIn('completed isolated workflow',out)
        # Even the admitted runner socket client cannot bypass independent workflow proof.
        request={'operation':'create_pr','run':{'id':rid,'slot':'2026-11-27','head':HEAD}}
        probe="import sys,json;sys.path.insert(0,sys.argv[1]);from editorial_runner import BrokerAdapter;p=json.load(open(sys.argv[2]));print(BrokerAdapter(p).request('create_pr',json.loads(sys.argv[3])))"
        child=subprocess.run([sys.executable,'-c',probe,str(self.code),str(self.root/'runner.json'),json.dumps(request['run'])],
            cwd='/',preexec_fn=self.drop(61001),capture_output=True,timeout=10)
        self.assertNotEqual(child.returncode,0)
        with sqlite3.connect(self.states['broker']/'broker.sqlite') as db:
            self.assertEqual(db.execute('SELECT count(*) FROM operations').fetchone()[0],0)
        for field,bad in [('enabled',False),('machine_id','other-host'),('recovery_verified',False)]:
            p=dict(self.runner_policy);p[field]=bad;self.write_policy('runner',p)
            self.assertNotEqual(self.result(['run','--head',HEAD])[0],0)
        self.write_policy('runner',self.runner_policy)
        self.assertNotEqual(self.result(['run','--head',HEAD])[0],0) # permanent active claim
    def test_A08_A09_real_runner_timeout_during_workflow(self):
        self.services(delay=60)
        child=self.client(['run','--head',HEAD]);self.children.append(child)
        try:
            with self.assertRaises(subprocess.TimeoutExpired):
                child.communicate(timeout=2.5)
        finally:
            child.kill();out,err=child.communicate(timeout=5)
            self.children.remove(child)
        self.assertIn(b'"warning": "90m"',out,(out,err))
        with sqlite3.connect(self.states['runner']/'journal.sqlite') as db:
            rid,phase=db.execute('SELECT id,phase FROM runs').fetchone()
            self.assertEqual(phase,'workflow_running')
            self.assertEqual(db.execute('SELECT run FROM active').fetchone(),(rid,))
            self.assertEqual(db.execute('SELECT count(*) FROM intents').fetchone()[0],0)
        self.assertNotEqual(self.result(['advance','--run',rid])[0],0)
        with sqlite3.connect(self.states['broker']/'broker.sqlite') as db:
            self.assertEqual(db.execute('SELECT count(*) FROM operations').fetchone()[0],0)

if __name__=='__main__':unittest.main()
