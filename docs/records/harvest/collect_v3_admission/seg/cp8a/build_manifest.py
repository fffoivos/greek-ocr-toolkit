"""Bind a conservative transitive source superset, tables, parameters and qualification."""
import importlib.metadata,json,platform,sys
from qualify import ROOT,BASE,SEG,CP7,HERE,sha,dump,load

def main():
    files=set((ROOT/'greekocr').rglob('*.py'))
    files.update(p for p in (ROOT/'greekocr').rglob('*') if p.is_file() and p.suffix in ('.json','.txt','.tsv','.csv','.yaml','.toml'))
    files.update((ROOT/'tests').glob('test_seg*.py'))
    files.update([ROOT/'tests/test_harvest_admission.py',ROOT/'tests/test_neighbour_words.py',BASE/'admw2/test_builder.py'])
    files.update(SEG.glob('*.py'));files.update(CP7.glob('*.py'));files.update(HERE.glob('*.py'))
    files.update([BASE/'build_release_admission.py',BASE/'stage_crops.py',SEG/'calibration_ledger.json',
        SEG/'CP5pb_calibration.json',SEG/'CP7_FREEZE.json',SEG/'CP7_FREEZE_r2.json',
        CP7/'r2/LEAD_ADJUDICATION_r2.json',CP7/'r2/runtime_amendment_cp7c2.json'])
    files.update(HERE/p for p in ('custody.json','parity.json','r1_matrices.json','r2_matrices.json','qualification_tests.json','admw2_native_qualification.json'))
    for parent in (CP7/'answers',CP7/'r2/answers',CP7/'scan',CP7/'r2/scan',CP7/'keys',CP7/'r2/keys'):
        files.update(p for p in parent.rglob('*') if p.is_file())
    files.update(p for directory in (HERE/'sol_packs',HERE/'rollouts') for p in directory.rglob('*') if p.is_file())
    files.update(HERE.glob('*.rescan.json'))
    freeze=load(SEG/'CP7_FREEZE_r2.json')
    manifest=dict(schema='SEG-CP8a-application-1',evaluator='greekocr.harvest.qualified_admission.evaluate_evidence',
        qualification_scope='frozen observation composition parity and original-snapshot text re-evaluation; CP6 fixtures; ADMW2 native rerun separately',
        accepted_baseline='aa3d9067',runtime_amendment='CP7c2 runtime only',
        parameters={k:v for k,v in freeze.items() if k not in ('files','geometry_files')},
        dependencies={d.metadata['Name']:d.version for d in importlib.metadata.distributions()},
        python=sys.version,platform=platform.platform(),files={str(p.relative_to(ROOT)):sha(p) for p in sorted(files)})
    dump(HERE/'application_manifest.json',manifest)
    print(sha(HERE/'application_manifest.json'))
if __name__=='__main__':main()
