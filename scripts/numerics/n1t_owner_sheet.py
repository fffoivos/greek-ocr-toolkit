"""Run only after complete N1-T readings and combiner; uses the prescribed renderer."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from greekocr.numerics.owner_v2 import build
sys.path.insert(0,str(ROOT/'scripts/numerics'))
from n1t_packs import rows


def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lead-approved',action='store_true')
    a=p.parse_args()
    if not a.lead_approved: raise ValueError('phase 2 requires lead go and --lead-approved')
    from n1ts import phase2
    phase2(a.lead_approved)


def publish(cards, spec, target, compact=False):
    import importlib.util
    cleanup=Path.home()/'Projects/greek-ocr-toolkit-cleanup/greekocr/adjudicate'
    specmod=importlib.util.spec_from_file_location('n1t_owner_renderer',cleanup/'owner_sheet.py',submodule_search_locations=[str(cleanup)])
    module=importlib.util.module_from_spec(specmod);sys.modules[specmod.name]=module;specmod.loader.exec_module(module)
    target=Path(target)
    target.parent.mkdir(parents=True,exist_ok=True)
    from n1t_boxes import detection_image
    if compact:
        import base64
        import io
        from PIL import Image
        from greekocr.numerics.prune import has_gap_component
        # Render native line pixels with the same colored styles and number lane.
        module.detection_image=lambda image, slots, **kw: detection_image(image,slots,scale=1,**kw)
        def uri(image):
            if isinstance(image,str) and image.startswith('data:image/'):return image
            if not isinstance(image,Image.Image):
                with Image.open(image) as im:image=im.copy()
            stream=io.BytesIO();image.save(stream,'PNG',optimize=True)
            return 'data:image/png;base64,'+base64.b64encode(stream.getvalue()).decode()
        module._uri=uri
    else:
        module.detection_image=detection_image
    html=module.render(cards,spec)
    # The v1 sheet keyed notes by slot; v2 keys by complete line. Read legacy
    # documents only when no line note exists, without migrating/writing remotely.
    needle="const snapshot = await db.doc('notes/' + id).get();"
    replacement="""let snapshot = await db.doc('notes/' + id).get();
      if (!snapshot.exists && el.dataset.legacyNoteIds) {
        const saved = [];
        for (const legacy of JSON.parse(el.dataset.legacyNoteIds)) {
          const old = await db.doc('notes/' + legacy).get();
          if (old.exists) saved.push({id: legacy, ...old.data()});
        }
        if (saved.length) {
          const data = {note: saved.map(d => saved.length > 1 ? d.id + ': ' + (d.note || '') : (d.note || '')).join('\\n')};
          const printedNotes = saved.filter(d => d.printed_edited && typeof d.printed === 'string');
          if (printedNotes.length === 1) data.printed = printedNotes[0].printed;
          snapshot = {exists: true, data: () => data};
        }
      }"""
    if html.count(needle)!=1: raise ValueError('owner note loader changed')
    html=html.replace(needle,replacement)
    import hashlib
    from collections import Counter
    base=target.parent
    products={'cards.json':json.dumps(cards,ensure_ascii=False,indent=2)+'\n','spec.json':json.dumps(spec,ensure_ascii=False,indent=2)+'\n','n1_sheet.html':html}
    for name,text in products.items(): (base/name).write_text(text)
    summary=dict(cards=len(cards),line_ids=[c['line_id'] for c in cards],groups=dict(Counter(c['group'] for c in cards)),
        printed_prefilled=len(cards),printed_source='ours-proposal',
        hashes={name:hashlib.sha256((base/name).read_bytes()).hexdigest() for name in products})
    (base/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    return summary

if __name__=='__main__':main()
