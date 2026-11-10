import hashlib
import hmac
import json
import os
import unittest
from unittest.mock import patch
from payments.stripe_sandbox import verify_webhook, create_checkout

class PaymentTests(unittest.TestCase):
    def test_signed_event_and_expiry(self):
        body=json.dumps({'id':'evt_demo','livemode':False}).encode()
        sig=hmac.new(b'test-secret',b'1000.'+body,hashlib.sha256).hexdigest()
        self.assertEqual(verify_webhook(body,'t=1000,v1='+sig,'test-secret',1001)['id'],'evt_demo')
        with self.assertRaises(ValueError):verify_webhook(body,'t=1000,v1='+sig,'test-secret',2000)
        with self.assertRaises(ValueError):verify_webhook(body+b' ','t=1000,v1='+sig,'test-secret',1001)
    def test_live_keys_fail_closed(self):
        with patch.dict(os.environ,{'STRIPE_SECRET_KEY':'sk_live_example'}):
            with self.assertRaises(ValueError):create_checkout('price_example','https://example.com','test')
