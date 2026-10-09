"""Evidence completeness, identity and transformation checks, not OCR tests."""
from research_orientation import *
def readrows(file):return [json.loads(l) for l in (ROOT/file).read_text().splitlines()]
def main():
    checks=[]
    manifest=load('testset/manifest.json');cases=manifest['cases'];assert len(cases)==136
    ids={c['id'] for c in cases};assert len(ids)==136
    for c in cases:
        p=ROOT/c['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==c['sha256'],c['id'];assert list(Image.open(p).size)==c['size']
        if c['kind']=='whole':
            orig=Image.open(ROOT/'pages'/f"{c['source']}.png").convert('RGB');actual=Image.open(p).convert('RGB');assert np.array_equal(np.array(orig.rotate(-c['applied_cw'],expand=True)),np.array(actual)),c['id']
    checks.append('136 manifest images, SHA-256, dimensions and 40 exact quarter turns verified')
    for c in cases:
        if c['kind']=='composite' and c['roi_unit']=='word':
            page=Image.open(ROOT/c['path']).convert('RGB');roi=page.crop(c['roi']);inside=roi.crop((8,8,roi.width-8,roi.height-8))
            padded=Image.open(ROOT/'testset'/f"{c['template']}__r{c['roi_truth_cw']}.png").convert('RGB');sameword=padded.crop((20,20,padded.width-20,padded.height-20))
            assert np.array_equal(np.array(inside),np.array(sameword)),c['id']
    checks.append('All four pasted-word ROI interiors equal the standalone rotated word pixels; only white margins differ')
    for file in ['geometry','osd','ocr_vote','constrained_vote','rapid']:
        rs=readrows(file+'.jsonl');assert len(rs)==148,file
        assert len({(r['id'],r['scope']) for r in rs})==148,file
        assert {r['id'] for r in rs}==ids,file
        for r in rs:assert r['pred_cw'] in (0,90,180,270,None);assert r['correct']==(r['pred_cw']==r['truth_cw'])
    checks.append('Five candidates have all 148 distinct required evaluations; decisions agree with recorded labels')
    assert len(readrows('layout.jsonl'))==64;assert len(readrows('lines.jsonl'))==40
    assert len(load('table_results.json')['cases'])==12
    checks.append('64 layout cases, 40 line cases and 12 fresh table cases present')
    ptests=load('backend_results.json')['pdf_tests'];assert len(ptests)==8
    for r in ptests:assert r['native_text_cells']==0;assert r['mae_to_rotate0'] is not None and r['mae_to_rotate0']<2
    checks.append('Both PDF backends rendered all four rotations without native text and matched display frames')
    assert len(load('local_results.json')['cases'])==12;assert len(load('real_local_results.json')['cases'])==3
    checks.append('Blind mixed proposals and three real local labels present')
    report=(ROOT/'REPORT.md').read_text();assert report.rstrip().splitlines()[-1].startswith('RESULT: ANSWERED ')
    import re
    for target in re.findall(r'\]\(([^)]+)\)',report):
        if not target.startswith(('http','/','#')):assert (ROOT/target).exists(),target
    checks.append('Report result footer and all explicit local Markdown links verified')
    # Confirm no source file drift between evidence snapshot and verification.
    for r in load('source_evidence.json'):assert hashlib.sha256(Path(r['file']).read_bytes()).hexdigest()==r['sha256'],r['file']
    checks.append('Installed source and read-only detector hashes still match archived evidence')
    save('verification.json',dict(passed=True,checks=checks));print('\n'.join(checks),flush=True)
if __name__=='__main__':main()
