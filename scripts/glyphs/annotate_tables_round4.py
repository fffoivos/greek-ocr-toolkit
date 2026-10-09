"""Provisional pixel annotations for the round-4 development set.

The hand-set grids below come from inspecting the PNGs. This evaluation-only
file never reads PDF text, boxes.json, detector outputs, or model predictions.
Within each hand-defined cell, connected ink proposes text envelopes for visual
review. These proposals remain provisional; see each JSON's limitations.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage as ndi

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/tables/annotations'


def runs(mask):
 e=np.diff(np.r_[False,mask,False].astype(int))
 return list(zip(np.flatnonzero(e==1),np.flatnonzero(e==-1)))


def elements(gray,box,xh):
 a,t,b,bot=map(int,box);crop=gray[t:bot,a:b]
 if crop.size==0:return []
 bg=ndi.maximum_filter(crop,size=max(3,round(2*xh)))
 contrast=bg.astype(float)-crop
 ink=contrast>max(40,float(np.percentile(contrast,95))*.55)
 labels,n=ndi.label(ink)
 bodies=[];marks=[]
 for i,sl in enumerate(ndi.find_objects(labels),1):
  if sl is None:continue
  y,x=sl;hh=y.stop-y.start;ww=x.stop-x.start;area=(labels[sl]==i).sum()
  q=(x.start+a,y.start+t,x.stop+a,y.stop+t)
  if .45*xh<=hh<=2.7*xh and .15*xh<=ww<=8*xh and area>.04*xh*xh:
   bodies.append(q)
  elif hh<.65*xh and ww<xh and area>.008*xh*xh:marks.append(q)
 if not bodies:return []
 for q in marks:
  if any(max(0,q[0]-r[2],r[0]-q[2])<.45*xh and max(0,q[1]-r[3],r[1]-q[3])<.6*xh for r in bodies):bodies.append(q)
 groups=[]
 for q in sorted(bodies,key=lambda q:(q[1]+q[3])/2):
  match=[g for g in groups if min(abs((r[1]+r[3]-q[1]-q[3])/2) for r in g)<.65*xh]
  if match:match[0].append(q)
  else:groups.append([q])
 return [list(map(int,[min(q[0] for q in g),min(q[1] for q in g),max(q[2] for q in g),max(q[3] for q in g)])) for g in groups]


class Annotation:
 def __init__(self,key,rotation=0):
  self.key=key;self.path=ROOT/'.astra/pages'/f'{key}.png'
  im=Image.open(self.path).convert('L');self.size=im.size;self.rotation=rotation
  self.gray=np.array(im.rotate(rotation,expand=True));self.tables=[]
 def mapped(self,b):
  if not self.rotation:return list(map(int,b))
  # Clockwise inspection rotation only; the detector input is never rotated.
  a,t,r,bot=b;w,h=self.size
  assert self.rotation==270
  return list(map(int,[t,h-r,bot,h-a]))
 def table(self,tid,extent,xh,notes=''):
  d=dict(id=tid,extent=self.mapped(extent),cells=[],header_spans=[],notes=notes,
         orientation_degrees_clockwise_for_reading=(360-self.rotation)%360)
  self.tables.append(d);self.current=d;self.xh=xh
 def cell(self,box,row,col,rowspan=1,colspan=1,header=False,panel='main',empty=None):
  boxes=elements(self.gray,box,self.xh) if empty is not True else []
  cid=f'{self.current["id"]}:{panel}:r{row}c{col}'
  cell=dict(id=cid,panel=panel,row=row,column=col,row_span=rowspan,column_span=colspan,
            box=self.mapped(box),header=header,empty=not boxes,
            text_elements=[dict(id=f'{cid}:e{i}',box=self.mapped(b)) for i,b in enumerate(boxes)])
  if empty is False and not boxes:cell['review_flag']='expected text; envelope proposal missing'
  self.current['cells'].append(cell)
  if header:self.current['header_spans'].append(dict(cell_id=cid,row=row,column=col,row_span=rowspan,column_span=colspan))
 def grid(self,xs,centres,half,row0=0,col0=0,panel='main',slope=0,empty=None):
  for i,y in enumerate(centres):
   for j,(a,b) in enumerate(zip(xs,xs[1:])):
    shift=slope*((a+b)/2-xs[0]);margin=.1*self.xh
    self.cell([a+margin,y-half+shift,b-margin,y+half+shift],i+row0,j+col0,panel=panel,
              empty=(i,j) in empty if empty else None)
 def save(self):
  for t in self.tables:
   t['panels']={p:dict(rows=max(c['row']+c['row_span'] for c in t['cells'] if c['panel']==p),
                       columns=max(c['column']+c['column_span'] for c in t['cells'] if c['panel']==p))
                for p in sorted({c['panel'] for c in t['cells']})}
  record=dict(schema_version=1,key=self.key,status='provisional pixel-reviewed grids; automatic envelope proposals',
    source=dict(path=str(self.path.relative_to(ROOT)),sha256=hashlib.sha256(self.path.read_bytes()).hexdigest(),image_size=list(self.size),pdf_text_used=False),
    coordinate_origin='TOPLEFT',units='source pixels',
    method='Hand-set cells/row sequences from page pixels; independent connected-ink envelopes inside cells; page overlay reviewed.',
    limitations=['Envelopes are provisional, not certified character transcriptions.','Nested navigation panels have independent row/column indices; no fictitious shared row phase is imposed.','Faint punctuation, touching rules and stamps can affect automatic envelope proposals.'],
    tables=self.tables)
  (OUT/f'{self.key}.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
  im=Image.open(self.path).convert('RGB');d=ImageDraw.Draw(im)
  for table in self.tables:
   d.rectangle(table['extent'],outline='red',width=3)
   for c in table['cells']:
    d.rectangle(c['box'],outline='orange' if c['empty'] else '#3399dd',width=1)
    for e in c['text_elements']:d.rectangle(e['box'],outline='#00a040',width=2)
  im.thumbnail((1600,1800));im.save(ROOT/'.astra/out'/f'{self.key}.annotations.jpg',quality=94)
  print(self.key,len(self.tables),'tables',sum(len(t['cells']) for t in self.tables),'cells',sum(len(c['text_elements']) for t in self.tables for c in t['cells']),'elements')


def navigation():
 a=Annotation('an-7a2b17a3fb0f-p000200')
 left=[386,434,470,517,554,590,640,676,709,764,797,836,887,922,958,1009,1045,1081,1129,1168,1201,1252,1287,1324,1379,1417,1452,1502,1537,1573,1624,1660,1696,1747,1783,1820,1870,1905,1938,1991,2024,2063]
 for tid,extent,logxs,trigxs,bottomxs,dy in [
  ('left',[716,155,1827,2110],[743,855,1018],[1047,1090,1250,1413,1598,1749,1798],[1030,1121,1267,1372,1534,1641,1800],0),
  ('right',[2089,150,3198,2095],[2123,2219,2374],[2405,2450,2610,2768,2945,3105,3170],[2385,2485,2630,2733,2869,2985,3168],-13)]:
  a.table(tid,extent,23,'One leaf with a logarithm panel, an upper trigonometric panel, and three lower logarithm pairs.')
  a.cell([logxs[0],197+dy,logxs[-1],308+dy],0,0,rowspan=2,colspan=2,header=True,panel='log')
  for j in range(2):a.cell([logxs[j]+4,314+dy,logxs[j+1]-4,355+dy],2,j,header=True,panel='log')
  a.grid(logxs,[y+dy for y in left],16,row0=3,panel='log')
  for j in range(6):a.cell([trigxs[j]+4,197+dy,trigxs[j+1]-4,253+dy],0,j,header=True,panel='trig')
  cy=[282+(i//3)*122+(i%3)*37+dy for i in range(31)]
  a.grid(trigxs,cy,17,row0=1,panel='trig')
  for j in range(6):a.cell([trigxs[j]+4,1540+dy,trigxs[j+1]-4,1602+dy],32,j,header=True,panel='trig')
  for j in range(6):a.cell([bottomxs[j]+4,1630+dy,bottomxs[j+1]-4,1720+dy],0,j,header=True,panel='lower')
  cy=[1747+(i//3)*122+(i%3)*37+dy for i in range(9)]
  a.grid(bottomxs,cy,17,row0=1,panel='lower')
 a.save()


def vouli35():
 a=Annotation('s2-200e977f2dab5291c42c-p00035');a.table('main',[568,748,2900,3820],44)
 xs=[585,688,1278,1665,2018,2108,2380,2463,2775,2855]
 for box,col,cs,rs in [([590,790,1280,1180],0,2,2),([1290,790,1710,1180],2,1,2),([1730,790,2095,1180],3,2,2),([2120,790,2860,1080],5,4,1),([2120,1090,2470,1200],5,2,1),([2480,1090,2860,1200],7,2,1)]:
  a.cell(box,0 if rs==2 or box[1]<1000 else 1,col,colspan=cs,rowspan=rs,header=True)
 cy=[1226+i*65.2 for i in range(38)]
 occupied={1,9,12,13,14,15,16,17,19,20,21,22,23,24,25,26,27,28,29,30,32,33,35,36}
 decreases={1,14,15,17,21,22,23,25,28,33}
 empty={(i,j) for i in range(38) for j in range(9) if (j==2 and i+1 not in occupied)
        or (j in (5,6) and i+1 in decreases) or (j in (7,8) and i+1 not in decreases)}
 a.grid(xs,cy,30,row0=2,slope=.015,empty=empty)
 a.grid(xs,[3745],32,row0=40,slope=.015)
 a.save()


def vouli20():
 a=Annotation('s2-831443dc5e6f1ccfbaf5-p00020');a.table('main',[55,931,3295,3788],38)
 xs=[78,173,581,897,978,1252,1350,1630,1722,2103,2387,2480,2765,2864,3165,3250]
 for box,col,cs,rs in [([90,968,570,1260],0,2,2),([601,960,958,1250],2,2,2),([995,960,1335,1250],4,2,2),([1365,944,2104,1070],6,3,1),([1365,1080,1710,1280],6,2,1),([1740,1080,2104,1280],8,1,1),([2130,959,2868,1080],9,4,1),([2150,1090,2470,1285],9,2,1),([2500,1090,2860,1285],11,2,1),([2880,994,3260,1310],13,2,2)]:
  a.cell(box,0 if rs==2 or box[1]<1080 else 1,col,colspan=cs,rowspan=rs,header=True)
 cy=[1339,1405,1470,1534,1600,1666,1798,1860,1926,1994,2060,2124,2189,2255,2320,2385,2450,2515,2580,2646,2712,2776,2841,2910,2972,3036,3101,3166,3231,3296,3362,3427,3492,3558]
 occupied={1,2,4,5,6,9,10,12,14,23,27,29,30,31,32,33,34}
 empty={(i,j) for i in range(34) for j in (2,3) if i+1 not in occupied or (j==3 and i+1!=27)}
 a.grid(xs,cy,29,row0=2,slope=.023,empty=empty)
 # Municipality 6 has a second printed name line; it belongs to that cell.
 cell=next(c for c in a.current['cells'] if c['row']==7 and c['column']==1)
 cell['box'][3]=1758
 cell['text_elements']=[dict(id=cell['id']+f':e{i}',box=b) for i,b in enumerate(elements(a.gray,cell['box'],38))]
 cell['empty']=not cell['text_elements']
 a.grid(xs,[3680],35,row0=36,slope=.023)
 a.save()


def grammar():
 a=Annotation('an-a3c2bdf81256-p000112')
 for tid,extent,ys in [('adjectives',[101,392,1160,1255],[498+i*51.3 for i in range(15)]),('participles',[105,1367,1147,2178],[1408+i*52.3 for i in range(15)])]:
  a.table(tid,extent,26,'Two parallel paradigm panels; inflected forms on one printed line are one logical entry.')
  if tid=='adjectives':
   a.cell([185,389,597,446],0,1,header=True,panel='left');a.cell([711,386,1150,445],0,1,header=True,panel='right')
  row0=1 if tid=='adjectives' else 0
  a.grid([104,163,610],ys,24,row0=row0,panel='left')
  rightys=[489+i*51.1 for i in range(13)] if tid=='adjectives' else [1395+i*52.2 for i in range(15)]
  a.grid([657,711,1145],rightys,24,row0=row0,panel='right')
 a.save()


def dense():
 a=Annotation('an-d3237d690aa0-p000138')
 reviewed_centres=[
  [360,423,494,565,623,700,769,838,907,977,1041,1114,1178,1249,1318,1375,1452,1518,1575,1647,1712,1790,1860,1929,1996,2063,2135,2201,2273,2338,2410,2475,2542,2609,2677,2746,2816],
  [366,436,503,572,640,708,775,845,913,981,1051,1120,1188,1255,1325,1389,1456,1517,1584,1653,1728,1790,1862,1932,1997,2070,2138,2206,2269,2339,2412,2479,2544,2621,2691,2762,2831],
  [376,444,510,580,647,716,786,854,922,992,1060,1130,1199,1266,1331,1399,1470,1534,1601,1668,1738,1809,1877,1947,2014,2080,2152,2219,2287,2358,2427,2491,2563,2631,2694,2762,2831],
  [366,432,495,570,637,705,774,842,913,982,1044,1118,1186,1254,1321,1389,1458,1524,1590,1659,1727,1796,1866,1934,2003,2070,2139,2207,2279,2346,2417,2485,2553,2619,2688,2760,2828]]
 for tid,extent,xs in [('left',[446,196,2100,2946],[474,993,1250,1770,2050]),('right',[2370,196,4010,2930],[2390,2940,3180,3700,3990])]:
  a.table(tid,extent,31,'Two independent dictionary/index panels on this leaf. Each term and its locator are distinct entries.')
  for p,(l,m,r) in enumerate([(xs[0],xs[1],xs[2]),(xs[2]+40,xs[3],xs[4])]):
   a.cell([l,210,r,282],0,0,colspan=2,header=True,panel=str(p))
   # Reviewed pixel projection peaks; the four panels have different phases.
   cy=reviewed_centres[p+(0 if tid=='left' else 2)]
   # Locator starts vary with term length. Pick the largest visible word
   # gutter in the manually bounded row, then inspect the resulting overlay.
   for row,y in enumerate(cy,1):
    t,b=int(y-31),int(y+36)
    crop=a.gray[t:b,int(l):int(r)]
    dark=crop < 130
    proj=dark.sum(axis=0)
    gaps=[(aa,bb) for aa,bb in runs(proj<2) if aa>.3*(r-l) and bb<.95*(r-l)]
    cut=l+sum(max(gaps,key=lambda v:v[1]-v[0]))/2 if gaps else m
    a.cell([l,t,cut,b],row,0,panel=str(p));a.cell([cut,t,r,b],row,1,panel=str(p))
 a.save()


def votes():
 a=Annotation('s2-80513ae109b4f749ca58-p00003');a.table('votes',[304,1457,1796,2900],35,'Two independent lists of 21 names; a printed N or an empty vote cell follows each name. No header inside the list.')
 a.grid([310,983,1043],[1495+i*68.7 for i in range(21)],32,panel='left')
 a.grid([1057,1714,1790],[1493+i*68.8 for i in range(21)],32,panel='right')
 a.save()


def budget():
 a=Annotation('s2-dee99fdf5214acdc6f25-p00005');a.table('budget',[182,191,1658,1807],35,'Five budget entries plus a total; headings span description and amount. Paragraph text remains in its description cell. Leaders are not text elements.')
 blocks=[(191,264,274,470),(480,550,558,951),(966,1030,1033,1302),(1390,1460,1464,1594),(1605,1674,1675,1807)]
 for i,(ht,hb,t,b) in enumerate(blocks):
  row=3*i+(1 if i>=3 else 0)  # reserve row 9 for the printed total
  a.cell([192,ht,1653,hb],row,0,colspan=2,header=True)
  # Earlier paragraph lines span the page; only the final amount line has
  # a description/amount boundary. Keep all of that paragraph's text.
  a.cell([187,t,1653,b-63],row+1,0,colspan=2)
  a.cell([187,b-63,1340,b],row+2,0);a.cell([1340,b-63,1653,b],row+2,1)
 a.cell([720,1328,1334,1390],9,0);a.cell([1334,1328,1655,1390],9,1)
 a.save()


def sideways():
 a=Annotation('s2-6419488b7f8e69fd20da-p00001',rotation=270)
 # Coordinates below are the clockwise inspection view, 4657 x 3287.
 a.table('sideways',[140,393,4290,2646],40,'Annotation is mapped back to original pixels; no orientation correction is applied to detector output.')
 xs=[167,520,806,1095,1387,1678,1965,2258,2544,2835,3120,3404,3693,3981,4270]
 a.cell([180,414,4270,593],0,0,colspan=14,header=True)
 a.cell([188,618,510,1627],1,0,rowspan=5,header=True)
 for start,end,label in [(1,6,'1888'),(6,11,'1889'),(11,14,'1890')]:
  a.cell([xs[start]+9,620,xs[end]-9,803],1,start,colspan=end-start,header=True)
  a.cell([xs[start]+9,833,xs[end]-9,1035],2,start,colspan=end-start,header=True)
  a.cell([xs[start]+9,1047,xs[min(start+3,end)]-9,1254],3,start,colspan=min(3,end-start),header=True)
  if end-start==5:
   a.cell([xs[start+3]+9,1047,xs[start+4]-9,1254],3,start+3,header=True)
   a.cell([xs[start+4]+9,1047,xs[end]-9,1544],3,start+4,rowspan=2,header=True)
 for j in range(1,14):
  if j not in (5,10):a.cell([xs[j]+7,1262,xs[j+1]-7,1540],4,j,header=True)
  a.cell([xs[j]+7,1545,xs[j+1]-7,1625],5,j,header=True)
 a.grid(xs,[1741+i*64.5 for i in range(12)],30,row0=6,slope=-.006)
 a.grid(xs,[2556],36,row0=18,slope=-.006)
 a.save()


if __name__=='__main__':
 OUT.mkdir(parents=True,exist_ok=True)
 for f in (navigation,vouli35,vouli20,grammar,dense,votes,budget,sideways):f()
