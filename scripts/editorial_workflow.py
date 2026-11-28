#!/usr/bin/env python3
"""Isolated candidate-bound research, writer and independent review workers.

Each role runs as a separate identity with its own protected journal and model key.
No role has publication credentials. Tests inject backends; production has no test switch.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import socket
import sqlite3
import struct
import urllib.request

from editorial_runner import protected, GitHubReadAdapter

POLICY = Path('/etc/future-pulse/workflow-' + str(os.geteuid()) + '.json')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',',':')).encode()).hexdigest()


def rpc(path, request):
    with socket.socket(socket.AF_UNIX) as client:
        client.connect(path)
        # No workflow deadline; a slow writer/reviewer does not release admission.
        client.sendall((json.dumps(request)+'\n').encode())
        with client.makefile('rb') as f:
            line = f.readline(4*1024*1024+1)
        if len(line)>4*1024*1024:
            raise RuntimeError('oversize workflow response')
        reply=json.loads(line)
        if reply.get('allowed') is not True:
            raise RuntimeError('workflow denied')
        return reply['result']


def protected_socket(path):
    protected(Path(path).parent,0,True)
    st=Path(path).lstat()
    import stat
    if st.st_uid!=0 or not stat.S_ISSOCK(st.st_mode):
        raise PermissionError('untrusted workflow socket')


def authorize():
    protected(POLICY,0)
    p=json.loads(POLICY.read_text())
    identities=[p[k] for k in ('research_uid','writer_uid','review_uid','runner_uid','broker_uid')]
    if (p.get('enabled') is not True or p.get('recovery_verified') is not True
            or len(set(identities+[0])) != 6 or os.geteuid()!=p[p['role']+'_uid']
            or p['machine_id'] != Path('/etc/machine-id').read_text().strip()):
        raise PermissionError('workflow gate closed')
    protected(p['directory'],os.geteuid(),True)
    protected(Path(p['directory'])/'workflow.sqlite',os.geteuid(),owned_parent=p['directory'])
    protected(p['code_directory'],0,True)
    if Path(__file__).resolve().parent != Path(p['code_directory']):
        raise PermissionError('workflow code location')
    for name in ('editorial_workflow.py','editorial_runner.py','editorial_run_guard.py'):
        protected(Path(p['code_directory'])/name,0)
    protected(p['credential_file'],os.geteuid())
    if Path(p['credential_file']).stat().st_mode & 0o077:
        raise PermissionError('workflow credential permissions')
    for endpoint in p['sockets'].values():
        protected_socket(endpoint)
    peers={'research':('runner_uid','writer_uid','review_uid'),
           'writer':('runner_uid','review_uid'),'review':('runner_uid','broker_uid')}
    p['peer_uids']=[p[k] for k in peers[p['role']]]
    return p


def initialize(directory):
    with sqlite3.connect(Path(directory)/'workflow.sqlite') as db:
        db.executescript('PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL; '
            'CREATE TABLE tasks(run TEXT PRIMARY KEY, identity TEXT, status TEXT, result TEXT);')
    db.close()


class Backend:
    def __init__(self,p): self.p=p
    def model(self,role,payload):
        endpoint=self.p['model_endpoint']
        if not endpoint.startswith('https://'):
            raise PermissionError('HTTPS model endpoint required')
        prompt={
            'research':'Extract evidence-backed facts and source URLs. Return JSON with facts list; never invent sources.',
            'writer':'Write the final German article from the provided evidence and candidate. Return JSON with article string. Preserve the exact candidate if it is already suitable.',
            'review':'Independently fact-check and review the candidate against sources and research. Return JSON approved boolean and reasons list. Approve only if publication-ready.'}[role]
        req=urllib.request.Request(endpoint,data=json.dumps({'model':self.p['model'],
            'response_format':{'type':'json_object'},'messages':[{'role':'system','content':prompt},
            {'role':'user','content':json.dumps(payload)}]}).encode(),headers={
            'Authorization':'Bearer '+Path(self.p['credential_file']).read_text().strip(),
            'Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=120) as response:
            return json.loads(json.load(response)['choices'][0]['message']['content'])
    def sources(self):
        result=[]
        for url in self.p['sources']:
            if not url.startswith('https://'): raise PermissionError('HTTPS source required')
            with urllib.request.urlopen(url,timeout=60) as response:
                data=response.read(1024*1024+1)
                if len(data)>1024*1024: raise RuntimeError('source too large')
                result.append({'url':url,'text':data.decode(), 'sha256':hashlib.sha256(data).hexdigest()})
        if not result: raise RuntimeError('no sources')
        return result
    def candidate(self,r):
        gh=GitHubReadAdapter(self.p['repository'],self.p['base'])
        result=gh.get('/contents/'+self.p['article_path']+'?ref='+r['head'])
        if result['encoding']!='base64': raise RuntimeError('candidate encoding')
        return base64.b64decode(result['content']).decode()


class Worker:
    def __init__(self,p,backend):
        self.p,self.backend=p,backend
        self.db=sqlite3.connect('file:'+str(Path(p['directory'])/'workflow.sqlite')+'?mode=rw',uri=True)
        self.db.execute('PRAGMA synchronous=FULL')
        if self.db.execute('PRAGMA integrity_check').fetchone()!=('ok',):
            raise RuntimeError('workflow journal corrupt')
    def close(self): self.db.close()
    def dependency(self,role,r):
        return rpc(self.p['sockets'][role],{'operation':'inspect','run':r})
    def request(self,uid,request):
        if uid not in self.p['peer_uids']: raise PermissionError('workflow peer denied')
        r=request['run']; identity=digest({'id':r['id'],'slot':r['slot'],'head':r['head']})
        old=self.db.execute('SELECT identity,status,result FROM tasks WHERE run=?',(r['id'],)).fetchone()
        if old and old[0]!=identity: raise RuntimeError('workflow identity changed')
        if request['operation']=='inspect':
            if not old or old[1]!='complete': raise RuntimeError('workflow not complete')
            return json.loads(old[2])
        if request['operation']!='execute': raise ValueError('workflow operation')
        if old:
            if old[1]=='complete': return json.loads(old[2])
            raise RuntimeError('uncertain prior stage; operator recovery required')
        with self.db:
            self.db.execute('INSERT INTO tasks VALUES(?,?,?,NULL)',(r['id'],identity,'pending'))
        role=self.p['role']
        if role=='research':
            sources=self.backend.sources()
            report=self.backend.model(role,{'sources':sources})
            if not isinstance(report.get('facts'),list) or not report['facts']:
                raise RuntimeError('no research facts')
            artifact={'sources':sources,'report':report}
        elif role=='writer':
            research=self.dependency('research',r)
            candidate=self.backend.candidate(r)
            draft=self.backend.model(role,{'research':research['artifact'],'candidate':candidate})
            # Publication must contain the exact reviewed text, never just a caller-supplied head.
            if not isinstance(draft.get('article'),str) or draft['article']!=candidate:
                raise RuntimeError('draft differs from candidate commit; no publication')
            artifact={'article':draft['article'],'research_digest':research['digest']}
        elif role=='review':
            research=self.dependency('research',r); writer=self.dependency('writer',r)
            if writer['artifact']['research_digest']!=research['digest']:
                raise RuntimeError('research/writer binding mismatch')
            if writer['artifact']['article']!=self.backend.candidate(r):
                raise RuntimeError('reviewed candidate mismatch')
            review=self.backend.model(role,{'research':research['artifact'],'writer':writer['artifact']})
            if review.get('approved') is not True or not isinstance(review.get('reasons'),list):
                raise RuntimeError('independent review denied')
            artifact={'approved':True,'writer_digest':writer['digest'],'review':review}
        else: raise ValueError('unknown role')
        result={'identity':identity,'head':r['head'],'role':role,'artifact':artifact,'digest':digest(artifact)}
        with self.db:
            self.db.execute('UPDATE tasks SET status=?,result=? WHERE run=?',('complete',json.dumps(result),r['id']))
        return result


def execute(p,r):
    results={}
    for role in ('research','writer','review'):
        results[role]=rpc(p['workflow_sockets'][role],{'operation':'execute','run':r})
        if results[role]['head']!=r['head'] or results[role]['role']!=role:
            raise RuntimeError('stage identity mismatch')
    return results['review']


def serve(p):
    if os.environ.get('LISTEN_PID')!=str(os.getpid()) or os.environ.get('LISTEN_FDS')!='1':
        raise PermissionError('workflow socket activation required')
    worker=Worker(p,Backend(p))
    try:
        with socket.fromfd(3,socket.AF_UNIX,socket.SOCK_STREAM) as server:
            if server.getsockname()!=p['sockets'][p['role']] or not server.getsockopt(socket.SOL_SOCKET,socket.SO_ACCEPTCONN):
                raise PermissionError('workflow activation mismatch')
            while True:
                with server.accept()[0] as client:
                    try:
                        _,uid,_=struct.unpack('3i',client.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
                        if uid not in p['peer_uids']: raise PermissionError('peer denied')
                        with client.makefile('rb') as f: line=f.readline(65537)
                        if len(line)>65536 or not line.endswith(b'\n'): raise ValueError('frame')
                        result=worker.request(uid,json.loads(line)); reply={'allowed':True,'result':result}
                    except Exception:
                        reply={'allowed':False}
                    try: client.sendall((json.dumps(reply)+'\n').encode())
                    except OSError: pass
    finally: worker.close()

if __name__=='__main__': serve(authorize())
