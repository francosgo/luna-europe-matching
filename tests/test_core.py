import copy
import json
import tempfile
import unittest
from pathlib import Path
from luna_match.engine import match
from luna_match.store import Store
from luna_match.mcp import handle

FIXTURE = json.loads((Path(__file__).parents[1] / 'examples/match.json').read_text())

class MatchingTests(unittest.TestCase):
    def test_known_calculation_and_uncertainty(self):
        result = match(FIXTURE)
        self.assertEqual(result['score'], 66.7)
        self.assertEqual(result['coverage'], 83.3)
        self.assertEqual(result['unknown_upper_bound'], 83.3)
        self.assertEqual(result['eligibility'], 'unresolved')

    def test_hard_gap_blocks_high_score(self):
        data = copy.deepcopy(FIXTURE)
        data['requirements'][-1]['assessment'] = 'gap'
        self.assertEqual(match(data)['eligibility'], 'blocked')

    def test_missing_provenance_and_injection_rejected(self):
        for refs in ([], ['invented']):
            data = copy.deepcopy(FIXTURE)
            data['requirements'][0]['evidence_ids'] = refs
            with self.assertRaises(ValueError): match(data)

    def test_invalid_weights(self):
        for weight in (-1, 0, float('nan'), float('inf'), True, '10'):
            data = copy.deepcopy(FIXTURE)
            data['requirements'][0]['weight'] = weight
            with self.assertRaises(ValueError): match(data)

    def test_irrelevant_personal_attributes_do_not_change_score(self):
        data = {**FIXTURE, 'age': 50, 'gender': 'test', 'photo': 'test', 'psr': 99}
        self.assertEqual(match(data)['score'], match(FIXTURE)['score'])

    def test_mcp_calls_same_engine(self):
        response = handle({'id':1,'method':'tools/call','params':{'name':'explain_match','arguments':FIXTURE}})
        self.assertEqual(json.loads(response['result']['content'][0]['text'])['score'], 66.7)
        self.assertIsNone(handle({'method':'notifications/initialized'}))

class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Store(Path(self.tmp.name)/'review.sqlite')
        self.db.seed('one', 'Original')
    def tearDown(self): self.tmp.cleanup()
    def test_edit_invalidates_approval_and_stale_approval_fails(self):
        a = self.db.latest('one')
        self.db.approve('one', a['revision'], a['hash'])
        b = self.db.save('one', 'Changed', 1)
        self.assertEqual(b['status'], 'draft')
        with self.assertRaises(ValueError): self.db.approve('one',1,a['hash'])
        with self.assertRaises(ValueError): self.db.save('one','Lost update',1)
    def test_pending_request_blocks_approval(self):
        a = self.db.latest('one')
        self.db.request('one',1,'Make it shorter')
        with self.assertRaises(ValueError): self.db.approve('one',1,a['hash'])
        b = self.db.save('one','Shorter',1)
        self.assertFalse(self.db.requests())
        self.assertEqual(self.db.approve('one',2,b['hash'])['status'],'approved')
    def test_feedback_is_allowlisted_and_suppressed_for_small_groups(self):
        with self.assertRaises(ValueError): self.db.feedback('my private email',1)
        self.db.feedback('useful_match',1)
        self.assertEqual(self.db.aggregate(),[])
        for _ in range(9): self.db.feedback('useful_match',1)
        self.assertEqual(self.db.aggregate()[0]['n'],10)

if __name__ == '__main__': unittest.main()
