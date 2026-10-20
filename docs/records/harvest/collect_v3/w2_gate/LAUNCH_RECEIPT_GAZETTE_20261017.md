# W2 Gazette read: gate install + launch (one-off by the sourcing lead, coordinator-authorised, 17 Oct 2026)

**Reason.** The Sol sandbox cannot write the run root or start a detached, networked collector. The coordinator authorised the lead to run these steps by hand, logged as O in SOL_ROUTING.

1. **Gate install** (GATE2b INSTALL.md, the two lines verbatim), 17:59:38 EEST:
   - live check: no collector processes; run.lock not open; live gate eb4a17ed…;
   - installed `run/c1_gate.json`: eb4a17ed1924ff77… → 4652febb230ee37306e9c27a732e6989f53a5e22c56d1645f459f467e72e3545, verified after the atomic mv;
   - change: + gazette_modern (passed; classes modern_scanned; measured 1986–1990 only; masked rows for the 1d arm only).
2. **Launch**, 17:59:45 EEST:
   `nice -n 10 sh collect_v3/launch_detached.sh $OUT --config $D/config_w1_mac.json --output-root $OUT run --tranche W2 --sources gazette_modern --execution-host owner_mac --enable-network --serbian-codec`
   - supervisor 70258, worker 70269;
   - go entry 2 (960 pages, cap USD 1.44; W2 ledger cap = 3.80 + 1.44);
   - the first pages completed at 18:00:30, so the W2 resume accepted the gate extension against snapshot eb4a17ed.
