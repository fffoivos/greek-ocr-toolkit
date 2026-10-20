"""Build a local CLLG README/loaded-Kraken-model contract, without fetching."""
from __future__ import annotations
import argparse
from pathlib import Path
import re
from greekocr._vendor.bench.common import sha256
from greekocr._vendor.bench.e1_common import atomic_json


def readme_facts(readme):
    import yaml
    text = Path(readme).read_text(encoding='utf-8')
    front = re.match(r'\A---\s*\n(.*?)\n---(?:\n|$)',text,re.S)
    if front is None: raise ValueError('CLLG README requires YAML front-matter')
    header = front.group(1); data = yaml.safe_load(header)
    if not isinstance(data,dict): raise ValueError('invalid CLLG front-matter')
    def quote(field):
        match = re.search(r'^'+re.escape(field)+r':[\s\S]*?(?=^[A-Za-z_][\w-]*:|\Z)',header,re.M)
        if match is None: raise ValueError('CLLG README missing '+field)
        return match.group(0).rstrip()
    software = data.get('software_name'); hints = data.get('software_hints',[])
    scripts = data.get('script',[]); metrics = data.get('metrics',{})
    base = data.get('base_model',[])
    if (software!='kraken' or 'kraken 7.1' not in hints or set(scripts)!={'Grek','Latn'}
            or metrics.get('CER')!=4.54 or data.get('license')!='CC-BY-4.0'
            or not any('10.5281/zenodo.10592716' in b for b in base)):
        raise ValueError('CLLG README does not establish released Kraken 7.1 recognition facts')
    if 'recognition' not in data.get('model_type',[]): raise ValueError('CLLG must be a recognition model')
    facts = dict(software=dict(name=software,hints=hints), script=scripts,
        metric=dict(name='CER',value=metrics['CER']), licence=data['license'], base_model=base)
    evidence = dict(software=quote('software_name')+'\n'+quote('software_hints'),
        script=quote('script'), metric=quote('metrics'), licence=quote('license'), base_model=quote('base_model'))
    # Software fields need not be adjacent; retain each exact excerpt separately.
    evidence['software'] = [quote('software_name'),quote('software_hints')]
    return facts,evidence


def build_contract(readme, checkpoint, out):
    from greekocr._vendor.bench.e2_native import cllg_kraken
    facts,evidence = readme_facts(readme)
    native = cllg_kraken(checkpoint)
    contract = dict(schema='e2-cllg-contract-v1', reviewed=True,
        readme_sha256=sha256(readme), checkpoint_sha256=sha256(checkpoint),
        established=list(facts), facts=facts, readme_evidence=evidence,
        backend='kraken-native', factory='greekocr._vendor.bench.e2_native:cllg_kraken',
        class_order=native.binding['class_order'], preprocess=native.binding['preprocess'],
        class_order_source='loaded kraken model.codec.c2l; sorted by original label sequence',
        preprocessing_source='installed kraken.lib.dataset.ImageInputTransforms + loaded model input/padding',
        native_binding=native.binding)
    atomic_json(out,contract)
    return contract


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--readme',type=Path,required=True)
    p.add_argument('--checkpoint',type=Path,required=True)
    p.add_argument('--out',type=Path)
    args = p.parse_args()
    build_contract(args.readme,args.checkpoint,args.out or args.readme.with_name('readme_contract.json'))


if __name__=='__main__': main()
