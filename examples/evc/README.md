# CORD EVC v0.1 example

This example demonstrates dependency-freshness evaluation only.

Run from the repository root:

```bash
python -m unittest discover -s tests -p 'test_evc.py' -v
```

The library API:

```python
import json
from pathlib import Path
from assurance.evc import evaluate_graph, load_graph

graph = load_graph(Path("examples/evc/basic-graph.json").read_bytes())
result = evaluate_graph(graph)
print(json.dumps(result, indent=2))
```

Expected overall status for the unchanged example: `VALID`.

To simulate a changed tool permission, change the current-state digest for
`browser-readonly` while leaving the claim's `expected_sha256` unchanged.
Only the claim that depends on that object should become `STALE`.

**Important:** `VALID` means only that declared dependency digests match the
supplied snapshot and evidence references exist. This prototype does not verify
evidence bytes, signatures, issuer identity, trusted time, truth, safety, or
regulatory compliance. See [EVC specification](../../spec/EVC.md).
