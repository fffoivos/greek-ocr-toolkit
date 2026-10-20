# CP3 M1: process evidence captured by the lead (Sol sandbox cannot run ps)

Captured: 2026-10-18 02:32:27 EEST (unix 1792279947)

```
50732     1 Sun Oct 18 00:20:39 2026           02:11:48 bash /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/overnight_chain.sh
50737 50732 Sun Oct 18 00:20:39 2026           02:11:48 /Library/Frameworks/Python.framework/Versions/3.11/Resources/Python.app/Contents/MacOS/Python -B collect_v3/run.py --config /Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/config_w1_mac.json -
50982     1 Sun Oct 18 00:21:20 2026           02:11:07 bash /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/materialize2.sh
```

Directory mtimes at capture (stat -f %m, s):
```
W2/crops 1792279944
cache/g1b 1792279944
```

Chain log (start of the materialize):
```
[2026-10-18 00:20:39 EEST] materialize W2 start: nice -n 10 .venv/bin/python -B collect_v3/run.py --config /Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/config_w1_mac.json --output-root 
```

Bound to the review-2 window (unix 1792279838–1792279863): the materialize process above was running throughout (its start precedes the window and it is still alive at capture), and it is the only process with the live run root as --output-root.
