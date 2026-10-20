import json,sys
out='/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/adj/answers_b1_r1.jsonl'
with open(out,'a') as f:
    for line in sys.stdin:
        line=line.strip()
        if not line: continue
        p=line.split('\t')
        d={"id":p[0],"answer":p[1],"printed":p[2],"confidence":p[3],"reason":p[4]}
        f.write(json.dumps(d,ensure_ascii=False)+'\n')
