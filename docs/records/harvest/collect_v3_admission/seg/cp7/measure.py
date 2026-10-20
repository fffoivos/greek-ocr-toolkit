"""Frozen candidate measurement. No detection, OCR, OSD, or fallback fitting."""
import sys
from cp7_common import *
sys.path.insert(0,str(ROOT))
from PIL import Image
from greekocr.harvest import geometry_observations as g, orientation_screen as orient
from greekocr.harvest import separator_inventory as sep
from greekocr.harvest.neighbour_words import neighbour_word_evidence
from greekocr.harvest.admission import evaluate,non_segmentation_eligibility
sys.path.insert(0,str(COLLECTOR))
from collect_v3.storage import ensure_crop


def crop(record):
    assert Path(sys.prefix).resolve()==(COLLECTOR/'.venv').resolve(),'collector interpreter required'
    target=HERE/'crops'/ (record['crop_sha256']+'.png')
    target.parent.mkdir(parents=True,exist_ok=True)
    ensure_crop(dict(record,crop=str(target)))
    assert sha(target)==record['crop_sha256']
    return target


def cache_for(r):
    pid=r['id'].rsplit('-l',1)[0]
    for base in (SEG/'CP4_geometry',SEG/'CP3_geometry',LIVE/'cache/g1b'):
        p=base/pid
        if (p/'receipt.json').exists():return p
    raise ValueError('missing_geometry_cache')


def load_page(r):
    cache=cache_for(r)
    return g.load_cached_page(r['crop_source_image'],cache,r['crop_source_sha256'])


def prepare_separators(page,pid):
    directory=HERE/'separators'/pid
    if directory.exists():return sep.load(page,directory)
    # Exclusive claim before invoking the existing pixel/structure preparer.
    directory.parent.mkdir(parents=True,exist_ok=True)
    dump(directory.parent/(pid+'.attempt.json'),dict(binding=sep.binding(page)),exclusive=True)
    data=sep.prepare(page)
    directory.mkdir()
    dump(directory/'inventory.json',data)
    dump(directory/'receipt.json',dict(binding=sep.binding(page),
        inventory_sha256=sha(directory/'inventory.json'),preparation_calls=1,row_detector_calls=0))
    return sep.load(page,directory)


def observe(r,*,median=None):
    path=crop(r)
    with Image.open(path) as im:axis=orient.observe_orientation(im.convert('L'))
    if axis.get('status')=='orientation_unknown':
        assert sha(r['crop_source_image'])==r['crop_source_sha256']
        with Image.open(r['crop_source_image']) as im:
            assert getattr(im,'n_frames',1)==1
            regions=orient.measure_page_regions(im.convert('L'))
        axis=orient.inherit_regional_axis(axis,r['crop_bbox'],regions,
            page_binding=dict(source=r['crop_source_image'],source_sha256=r['crop_source_sha256'],frame=0))
    page=None
    try:
        page=load_page(r)
        structural=neighbour_word_evidence(page,r['crop_bbox'],target_row_id=r.get('measured_row_id'))
    except (ValueError,OSError,KeyError) as e:
        structural=dict(status='unavailable',reason=str(e),union_drop=None,merged=None,neighbour_drop=None)
    try:
        if page is None:raise ValueError('geometry_unavailable')
        pid=r['id'].rsplit('-l',1)[0]
        inventory=prepare_separators(page,pid)
        crossing=orient.column_crossings(page,r['crop_bbox'],inventory['boundaries'])
        crossing['inventory_sha256']=sha(HERE/'separators'/pid/'inventory.json')
    except (ValueError,OSError,KeyError) as e:
        crossing=dict(status='unavailable',drop=None,reason=str(e))
    composed=orient.compose_cp5(axis,structural,crossing)
    text=None
    if 'label' in r:
        result=evaluate(r,page_median_height=median)
        text=dict(checks={k:v for k,v in result['checks'].items() if k not in ('geometry_unavailable','neighbour_words')},
            **non_segmentation_eligibility(result['checks']))
    # Geometry failure is an explicit policy loss, never measured detection.
    return dict(row_id=r['id'],crop_sha256=r['crop_sha256'],
        crop_bbox=r['crop_bbox'],source=r['crop_source_image'],source_sha256=r['crop_source_sha256'],
        geometry_binding=page['binding'] if page else None,
        merged=structural.get('merged'),neighbour_words=structural.get('neighbour_drop'),
        orientation=axis.get('rotated'),geometry_unavailable=composed['geometry_unavailable'],
        orientation_unknown=axis.get('status')=='orientation_unknown',text_rules=text,
        structural=structural,crossing=crossing,orientation_observation=axis,composed=composed,
        screen_drop=composed['drop'],
        admission_drop=True if text and not text['passed'] else composed['drop'])
