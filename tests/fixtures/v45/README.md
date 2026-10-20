# Canonical scanner v4.5 fixtures

Run offline with the installed Pillow-capable interpreter:

```
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B tests/test_scan_rollout.py
```

`p1_atoms.json` has accepted complete answer argv and rejected real paths/invalid atoms. `record_confined.txt` is the exact historically confined recorder, pinned by AST SHA-256. The grammar and pin are separate: recognizing data does not validate answer correctness or execute the recorder.

`p2_returns.json` describes deterministic synthetic white-source returns: allowed shrink with MAD 1, rejected MAD 2, upscale, and distortion. Tests also generate textured sources, same-aspect crops, opaque/partial-alpha RGBA, arbitrary common-scale shrink, unproven zooms, and historical images in temporary manifest-seeded packs.

`p3_loops.json` contains a finite literal positive loop and dynamic-bound/path-escape negatives. `batch_confined.txt` is the recorded batch helper, used with fresh synthetic items/images to reconstruct 19 overwritten snapshots. Other tests cover integer ranges, output order, extra images, unsafe helpers, nonliteral argv, future writes, isolated mkdir, and mixed answer/image heredocs.

The suite also loads the 53 established canonical and archived v4 regression cases. Missing historical witnesses are explicit skips; the SCAN2 qualification run must have zero skips. The two RU1 fixtures restore missing originals only into temporary snapshots from a hash-verified local cache; source packs remain unchanged.

`rejected_recorder_overwrites.json` adds the two SCAN2R5 histories: noninteger helper argv and an unsupported import. Both overwrite the recorder before an answer invocation and restore its exact source only afterward; both must remain VOID. `Scan2FProbes` also verifies that matching restored bytes alone cannot restore authority, whereas a new literal definition can.
