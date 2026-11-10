"""Stripe sandbox Checkout + signed webhook parser; no entitlement is granted here."""
import hashlib
import hmac
import json
import os
import time
import urllib.parse
import urllib.request

def create_checkout(price_id, return_origin, idempotency_key):
    key=os.environ.get('STRIPE_SECRET_KEY','')
    if not key.startswith('sk_test_'):
        raise ValueError('Only a Stripe test-mode secret key is accepted')
    if not price_id.startswith('price_') or not idempotency_key:
        raise ValueError('A configured recurring Price ID and idempotency key are required')
    parsed=urllib.parse.urlsplit(return_origin)
    if parsed.scheme!='https' or not parsed.netloc or parsed.query or parsed.fragment:
        raise ValueError('Use your configured HTTPS return origin')
    fields={'mode':'subscription','line_items[0][price]':price_id,'line_items[0][quantity]':'1',
            'success_url':return_origin.rstrip('/')+'/success?session_id={CHECKOUT_SESSION_ID}',
            'cancel_url':return_origin.rstrip('/')+'/cancel'}
    request=urllib.request.Request('https://api.stripe.com/v1/checkout/sessions',
        data=urllib.parse.urlencode(fields).encode(),headers={'Authorization':'Bearer '+key,'Idempotency-Key':idempotency_key})
    with urllib.request.urlopen(request,timeout=15) as response:
        return json.load(response)

def verify_webhook(raw, signature_header, secret, now=None):
    now=time.time() if now is None else now
    values={}
    for item in signature_header.split(','):
        k,_,v=item.partition('=');values.setdefault(k,[]).append(v)
    try:stamp=int(values['t'][0])
    except (KeyError,ValueError):raise ValueError('Invalid signature timestamp')
    if abs(now-stamp)>300:raise ValueError('Expired signature')
    if not secret:raise ValueError('Webhook secret required')
    expected=hmac.new(secret.encode(),str(stamp).encode()+b'.'+raw,hashlib.sha256).hexdigest()
    if not any(hmac.compare_digest(expected,s) for s in values.get('v1',[])):
        raise ValueError('Invalid signature')
    event=json.loads(raw)
    if event.get('livemode') is not False:raise ValueError('Only test events accepted')
    return event
