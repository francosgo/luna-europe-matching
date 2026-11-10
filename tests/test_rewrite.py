import json
import os
import unittest
from unittest.mock import patch, MagicMock
from luna_match.rewrite import rewrite

class RewriteTests(unittest.TestCase):
    def test_disabled_by_default(self):
        with patch.dict(os.environ,{'LUNA_LOCAL_MODEL':''}):
            with self.assertRaises(ValueError):rewrite('original','shorten',[])
    def test_local_response_parsed_without_saving_or_approving(self):
        response=MagicMock();response.__enter__.return_value.read.return_value=json.dumps({'done':True,'response':json.dumps({'body':'Short draft'})}).encode()
        with patch.dict(os.environ,{'LUNA_LOCAL_MODEL':'test-local'}), patch('urllib.request.urlopen',return_value=response) as send:
            self.assertEqual(rewrite('original','shorten',[]),'Short draft')
            self.assertEqual(send.call_args.args[0].full_url,'http://127.0.0.1:11434/api/generate')
