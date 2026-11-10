"""Local latency benchmark; not matching accuracy or end-to-end agent time."""
import json
import platform
import statistics
from pathlib import Path
from time import perf_counter
from luna_match.engine import match

sample = json.loads(Path('examples/match.json').read_text())
times = []
for _ in range(1000):
    start = perf_counter()
    match(sample)
    times.append((perf_counter()-start)*1000)
print(json.dumps({'calls':len(times),'python':platform.python_version(),'median_ms':statistics.median(times),
    'p95_ms':sorted(times)[949],'scope':'Synthetic 3-requirement local scoring only; excludes retrieval, drafting, network and human review.'},indent=2))
