"""SPLIT1's single, local variant of the reference owner sheet."""
import base64, html, json, sys
from pathlib import Path
from bs4 import BeautifulSoup
HERE=Path(__file__).resolve().parent
REVIEW=Path.home()/'Projects/greek-ocr-toolkit-review'
sys.path.insert(0,str(REVIEW))
from greekocr.adjudicate.owner_sheet import render

def uri(rec):return 'data:image/png;base64,'+base64.b64encode((HERE/rec['path']).read_bytes()).decode()
def esc(s):return html.escape(str(s),quote=True)
def overlay(rec):
 x0,y0,x1,y1=rec['crop_bbox'];a,b,c,d=rec['bbox'];w,h=rec['size']
 return f'<svg viewBox="0 0 {w} {h}"><rect class="tbox" x="{a-x0}" y="{b-y0}" width="{c-a}" height="{d-b}"/></svg>'
def sample_html(rec):
 w,h=rec['size'];dw=max(1,int(w*min(3,940/w,300/h)))
 return f'<div class="zw"><div class="ov" style="width:{dw}px" data-w="{w}" data-dw="{dw}"><img src="{uri(rec)}" alt="saved Google sample crop">{overlay(rec)}</div><div class="lens" hidden></div></div><table class="w"><tr><th>Google text</th><td>{esc(rec["old_label"])}</td></tr><tr><th>Sample ID</th><td class="sample-id">{esc(rec["id"])}<br>edition {esc(rec["edition_id"])}</td></tr></table>'

def build_sheet(cards,summary,counts):
 records=[];payload=[]
 for c in cards:
  e=c['editions'][0];s=c['samples'][0];entries=[]
  for ed in c['editions']:
   entries.append({'edition_id':ed['edition_id'],'split':ed['proposed_split'],'forced':ed['forced'],'title':ed['title'],'rows':ed['row_count'],
    'classes':ed['rows_per_class'],'documents':ed['member_documents'],'source':ed['source'],'year':ed['year'],'reason':ed['reason']})
  payload.append({'id':c['id'],'entries':entries})
  records.append({'line_id':e['edition_id'],'doc_id':'split1:'+e['edition_id'],'label':('Gazette '+c['year']+' — '+str(len(entries))+' issues') if 'year' in c else e['edition_id'],
   'image':uri(s),'overlay_svg':overlay(s),'tool_verdict':{'train':'KEEP','dev':'UNCERTAIN','test':'CHANGED'}[e['proposed_split']],
   'data':{'card-id':c['id']},'rows':[{'name':'Google text','text':s['old_label']},{'name':'Sample ID','text':s['id']+' · edition '+s['edition_id']},
    {'name':'Edition','text':e['title']},{'name':'Source / year','text':e['source']+' / '+str(e['year'])},{'name':'Rows per class','text':json.dumps(e['rows_per_class'],ensure_ascii=False)},
    {'name':'Reason','text':e['reason']}],
   'tags':[{'text':'PARTIAL BSB W2'}] if any(x['partial_bsb_w2'] for x in c['editions']) else [],'group':c['group']})
 intro=f"Built {summary['stamp']}. Proposal only; the owner allocates splits. All {summary['rows']:,} W1/W2 snapshot rows; census held 142,959 downstream. {summary['editions']} editions; {summary['forced']} forced. Whole editions; metadata identity and v2 leakage first, then seeded greedy 85/5/10 row allocation per source × primary class. DATA_PLAN_v2_20261016.md §3 gives global usable-train class quotas, no split ratios. Raw rows shown here are not admitted yields. 10 BSB W2 documents partial; 436 later pages excluded.\nGazette: one card per year; select an issue to review its independent edition split, mark and note. Two representative crops on the year card identify their actual editions; samples do not change with the selector. Each issue is listed with its split and lock. No bulk year decision.\nKEEP accepts the proposal. DROP proposes the other side: train ↔ held-out; DEV versus TEST after a TRAIN drop remains an owner choice. Forced editions stay locked; marks record feedback and cannot override the forced side. Notes autosave only in a signed-in artifact with db+user; this local page is unpublished. No database writes on load.\nInner frame/tool pill: TRAIN green, DEV amber, TEST blue. Outer border: owner KEEP green / DROP red. b toggles the saved Google bbox (blue); no segmentation evidence was recomputed."
 sheet=render(records,{'title':'SPLIT1 — edition split review','intro':intro,'sheet_prefix':'split1','groups':[{'id':g,'heading':label} for g,label in [('forced','Forced by v2 / registered evaluation — locked'),('test','TEST proposals'),('dev','DEV proposals'),('train','TRAIN proposals')]]})
 soup=BeautifulSoup(sheet,'html.parser');soup.body['data-variant']='split1'
 instructions=soup.select_one('.instructions');instructions.string='KEEP = accept proposed split; DROP = move across train ↔ held-out. Forced side is locked. ↑ ↓ move between cards, including in notes; SPACE toggles KEEP/DROP (first press KEEP), including in an empty note. Click badge to mark. For Gazette select the issue first. z zooms both samples 3×; b toggles saved boxes; hover/click gives lens; Esc leaves note. Each issue has its own notes ID.'
 table='<details><summary>Counts against plan quotas and 85/5/10 targets</summary><table class="counts"><tr><th>Source × row class</th><th>Train</th><th>Dev</th><th>Test</th><th>Target train/dev/test</th><th>Global class train quota</th></tr>'
 from build_split1 import QUOTAS
 for k,v in counts.items():
  n=sum(v.values());q=QUOTAS.get(k.split(' × ')[1],'—');table+=f'<tr><td>{esc(k)}</td><td>{v["train"]}</td><td>{v["dev"]}</td><td>{v["test"]}</td><td>{n*.85:.1f}/{n*.05:.1f}/{n*.1:.1f}</td><td>{q}</td></tr>'
 table+='</table><p>Plan §3: 202,000 usable train rows, global class quotas; no source quotas. These counts include all raw rows and forced sides. The complete class quota/difference table is in SPLIT_PROPOSAL.md.</p></details>'
 instructions.insert_after(BeautifulSoup(table,'html.parser'))
 for node,c in zip(soup.select('.card'),cards):
  es=c['editions'];first=es[0];node['data-tool']=first['proposed_split'].upper()
  pill=node.select_one('.toolpill');pill['class']=['toolpill',first['proposed_split'].upper()];pill.string='tool: '+first['proposed_split'].upper()
  metadata=node.select_one('table.w');rs=metadata.select('tr');rs[0].extract();rs[1].extract()
  zw=node.select_one('.zw');firsttable=BeautifulSoup('<table class="w"><tr><th>Google text</th><td>'+esc(c['samples'][0]['old_label'])+'</td></tr><tr><th>Sample ID</th><td class="sample-id">'+esc(c['samples'][0]['id'])+'<br>edition '+esc(c['samples'][0]['edition_id'])+'</td></tr></table>','html.parser').table
  zw.insert_after(firsttable);firsttable.insert_after(BeautifulSoup(sample_html(c['samples'][1]),'html.parser'))
  metadata['class']=['w','edition-metadata']
  if 'year' in c:
   choices='<label class="issue-label">Active issue (mark and note apply only to this edition)<select class="issue-select" aria-label="Active Gazette issue">'
   for i,e in enumerate(es):choices+=f'<option value="{i}">{esc(e["title"])} · {e["proposed_split"].upper()} · {e["row_count"]} rows'+(' · forced by v2 🔒' if e['forced'] else '')+'</option>'
   choices+='</select></label><details class="issue-list"><summary>Complete issue list ('+str(len(es))+')</summary><ul>'
   for e in es:choices+='<li>'+esc(e['title'])+' — <b>'+e['proposed_split'].upper()+'</b>'+(' 🔒 forced by v2' if e['forced'] else '')+' · '+str(e['row_count'])+' rows · <code>'+e['edition_id']+'</code></li>'
   choices+='</ul></details>';node.select_one('.lid').insert_after(BeautifulSoup(choices,'html.parser'))
  lock=BeautifulSoup('<span class="lock-label"></span>','html.parser');node.select_one('.lid').append(lock)
  metadata.insert_after(BeautifulSoup('<p class="active-edition"></p>','html.parser'))
 # Keep the reference lens implementation; replace persistence/navigation with the edition-state adapter.
 script=soup.find('script');lens=script.string[script.string.index('(function () {\n  const Z = 3;'):]
 data=json.dumps(payload,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
 script.string='const SPLIT1_CARDS = '+data+';\n'+(HERE/'sheet_adapter.js').read_text()+'\n'+lens
 soup.head.append(BeautifulSoup('<style>'+ (HERE/'sheet_variant.css').read_text()+'</style>','html.parser'))
 result=str(soup);(HERE/'OWNER_REVIEW.html').write_text(result)
 size=len(result.encode());assert size<10_000_000,size
 summary['sheet_bytes']=size;summary['sheet_MB']=round(size/1_000_000,3)
 (HERE/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 with open(HERE/'SPLIT_PROPOSAL.md','a') as f:f.write(f'\nSheet size: **{size:,} bytes ({size/1_000_000:.3f} MB)**, below 10 MB. {len(cards)} cards, two byte-exact samples per card.\n')
