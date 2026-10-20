"""Stream the census table once; write a compact table of all rows (TSV.gz) for later analysis."""
import gzip, json, sys
from pathlib import Path
from common import nchars, output_type, reason_code

SRC = Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells/population_cells.jsonl.gz')
OUT = Path(sys.argv[1])
n = agree = 0
with gzip.open(SRC, 'rt') as f, gzip.open(OUT, 'wt') as o:
    o.write('row_id\twave\tsource\tprimary_class\tscript_class\twidth\theight\tchars\tfilter_chars\toutput_type\tverdict_05\treason_05\tcrop_sha256\ttext\n')
    for line in f:
        r = json.loads(line)
        t = r['raw_text'] or ''
        c = nchars(t)
        n += 1
        agree += (c == r['characters'])
        o.write('\t'.join(map(str, [r['row_id'], r['wave'], r['source'], r['primary_class'], r['script_class'],
                r['width_px'], r['height_px'], c, r['characters'], output_type(t), r['verdict_05'],
                reason_code(r['verdict_05'], r['reason_05']), r['crop_sha256'],
                json.dumps(t, ensure_ascii=False)])) + '\n')
print(n, 'rows; my chars == filter chars on', agree)
