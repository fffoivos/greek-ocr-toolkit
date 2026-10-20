# KR1b scanner note for the Sol-reading lead

c2 is **VOID** under scanner v4. c1 is clean and stands. c2b replaces c2; this note does not override the VOID ruling or change the scanner.

Source rollout: `/Users/foivoskarounos-zamparloukos/.codex/sessions/2026/10/17/rollout-2026-10-17T15-59-18-01a149f1-feb5-7361-aaaf-06176f23d721.jsonl`. SHA256 is recorded below. Record numbers below are the rollout ordinals (also zero-based JSONL indices).

## Exact scanner violations

```json
[
  {
    "record": 22,
    "reason": "absolute path outside reader_dir",
    "path": "/zoom/$"
  },
  {
    "record": 44,
    "reason": "absolute path outside reader_dir",
    "path": "/zoom/$"
  }
]
```

## Record 22

Exact tool-input quote:

```javascript
for(let i=1;i<=8;i++) image((await tools.view_image({path:`${(await tools.exec_command({cmd:"pwd","max_output_tokens":100})).output.trim()}/zoom/${String(i).padStart(2,"0")}.png`})).image_url);
```

## Record 44

Exact tool-input quote:

```javascript
text(await tools.exec_command({cmd:"python3 - <<'PY'\nimport json\nc=[json.loads(x) for x in open('cards.jsonl')]\na=[]\ndata=[('y','y','n',['crop_clipped'],'καὶ: final character clipped'),('y','y','y',[],''),('y','y','n',['crop_clipped'],'πα-: final hyphen clipped'),('y','y','n',['crop_clipped'],'φύσεώς: final character clipped'),('y','y','n',['crop_clipped'],'ραν: initial character clipped'),('y','y','y',[],''),('y','y','y',[],''),('n','y','y',['wrong_letter'],'Ὁποῖα → ὁποῖα')]\nfor card,d in zip(c,data):\n a.append(dict(zip(['card_id','letters','marks','crop_ok','errors','detail'],[card['card_id'],*d])))\nwith open('answers.jsonl','w') as f:\n for r in a:f.write(json.dumps(r,ensure_ascii=False)+'\\n')\nPY","max_output_tokens":1000}));
for(let i=9;i<=16;i++) image((await tools.view_image({path:`${(await tools.exec_command({cmd:"pwd","max_output_tokens":100})).output.trim()}/zoom/${String(i).padStart(2,"0")}.png`})).image_url);
```

## Resolution and suggested scanner improvement

The rollout session cwd is `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/kosmo2/c2`. Both inputs execute `pwd`, trim its output, and interpolate that value as the prefix of the image path. Thus record 22 constructs `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/kosmo2/c2/zoom/01.png` through `08.png`; record 44 constructs `09.png` through `16.png` in the same zoom directory. These resolve inside reader_dir. The literal `/zoom/$` is a fragment between two JavaScript interpolations, not the evaluated absolute path. The saved v4 scan also matches zoom/01.png through zoom/16.png to authorized images. This supports a likely false positive in literal path extraction; the current rule still voids c2.

Suggestion: resolve supported `${pwd}`-style template expressions (including this inline exec_command pwd form) against evidenced cwd/pwd output before applying the absolute-path containment check. Normalize the complete path and retain traversal and symlink checks. Reject unresolved or unsupported expressions; do not broadly allow `/zoom/$` or execute arbitrary JavaScript during scanning. Keep image provenance and all existing fail-closed checks. No scanner change is included in KR1b.

Rollout SHA256: `42de9fb718fae358441eba5ccd810aa440d4748caca4c4613c086b029feadfa6`. Scan evidence: `scan/kosmo2/c2.scan.json`.
