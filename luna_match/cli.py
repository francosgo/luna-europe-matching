"""JSON in, JSON out scoring subprocess for integration adapters."""
import json
import sys
from .engine import match
if __name__ == '__main__':
    try:
        data=sys.stdin.read(1000001)
        if len(data)>1000000: raise ValueError('Payload too large')
        print(json.dumps(match(json.loads(data))))
    except (ValueError,TypeError,KeyError,AttributeError) as exc:
        print(json.dumps({'error':str(exc)}))
        sys.exit(1)
