import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import editorial_workflow as w

R={'id':'workflow-test','head':'a'*40,'slot':'2026-11-27'}
class Backend:
    def sources(self):return [{'url':'https://source.invalid','text':'fact'}]
    def candidate(self,r):return 'candidate'
    def model(self,role,payload):
        return {'research':{'facts':['fact']},'writer':{'article':'candidate'},
                'review':{'approved':True,'reasons':['checked']}}[role]

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.d=Path(self.tmp.name)
        self.results={};self.workers=[]
    def tearDown(self):
        for worker in self.workers:worker.close()
        self.tmp.cleanup()
    def worker(self,role):
        path=self.d/role;path.mkdir();w.initialize(path)
        worker=w.Worker({'role':role,'directory':str(path),'peer_uids':[os.getuid()]},Backend())
        worker.dependency=lambda role,r:self.results[role]
        self.workers.append(worker);return worker
    def execute(self,role):
        worker=self.worker(role)
        result=worker.request(os.getuid(),{'operation':'execute','run':R})
        self.results[role]=result
        return worker,result
    def test_order_exact_candidate_and_independent_review(self):
        for role in ('research','writer','review'):
            worker,result=self.execute(role)
            self.assertEqual(result['digest'],w.digest(result['artifact']))
            self.assertEqual(worker.request(os.getuid(),{'operation':'execute','run':R}),result)
        self.assertTrue(self.results['review']['artifact']['approved'])
    def test_writer_modified_draft_cannot_publish_or_retry(self):
        self.execute('research');worker=self.worker('writer')
        worker.backend.model=lambda *a:{'article':'uncommitted/unreviewed replacement'}
        with self.assertRaises(RuntimeError):worker.request(os.getuid(),{'operation':'execute','run':R})
        worker.backend=Backend()
        with self.assertRaises(RuntimeError):worker.request(os.getuid(),{'operation':'execute','run':R})
    def test_review_denial_and_foreign_head(self):
        self.execute('research');self.execute('writer');worker=self.worker('review')
        worker.backend.model=lambda *a:{'approved':False,'reasons':['fact mismatch']}
        with self.assertRaises(RuntimeError):worker.request(os.getuid(),{'operation':'execute','run':R})
        with self.assertRaises(RuntimeError):worker.request(os.getuid(),{'operation':'inspect','run':dict(R,head='b'*40)})
    def test_peer_denial_before_any_intent(self):
        worker=self.worker('research')
        with self.assertRaises(PermissionError):worker.request(os.getuid()+1,{'operation':'execute','run':R})
        self.assertEqual(worker.db.execute('SELECT count(*) FROM tasks').fetchone()[0],0)
