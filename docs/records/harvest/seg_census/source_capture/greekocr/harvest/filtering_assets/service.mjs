// Thin streaming host for the BYTE-IDENTICAL owner-accepted segmentation policy.
import fs from 'node:fs';
import vm from 'node:vm';
import readline from 'node:readline';
import crypto from 'node:crypto';
const bytes=fs.readFileSync(new URL('./segmentation-policy.js',import.meta.url));
const context=vm.createContext({});vm.runInContext(bytes.toString('utf8'),context);
const policySha=crypto.createHash('sha256').update(bytes).digest('hex');
function at(points,x){if(x<=points[0][0])return points[0][1];for(let i=1;i<points.length;i++)if(x<=points[i][0]){const [a,y]=points[i-1],[b,z]=points[i];return y+(z-y)*(x-a)/(b-a)}return points.at(-1)[1]}
// Verbatim algorithm from reconcile_neighbour_bands.mjs, lifted into a function.
function reconcile(raw,crop){
 if(raw.status==='unavailable')return raw;
 const bands=crop.lines.filter(l=>l.votes>0),physical=new Map(),groupBindings=[];
 if(!bands.length)return {...raw,status:'unavailable',reason:'No observed crop font bands'};
 for(const row of raw.rows){const perBand=new Map();for(const group of row.groups){const b=group.bbox,x=(b[0]+b[2])/2,y=(b[1]+b[3])/2;const candidates=bands.map((l,i)=>({i,distance:Math.abs(y-(at(l.curves.mean,x)+at(l.curves.base,x))/2)})).sort((a,b)=>a.distance-b.distance);const index=candidates[0].i;if(!perBand.has(index))perBand.set(index,[]);perBand.get(index).push(group);groupBindings.push({source_row_id:row.row_id,band_index:index,side:bands[index].side,bbox:b,positive:group.positive,unresolved:group.unresolved});}
  for(const [index,groups]of perBand){if(bands[index].side==='main')continue;if(!physical.has(index))physical.set(index,[]);physical.get(index).push({source_row_id:row.row_id,full_line:row.full_line,entire_source_row_in_band:perBand.size===1,groups});}}
 let whole=0,partial=0,unresolved=0,full=0,splitBands=0;for(const pieces of physical.values()){if(pieces.length!==1||!pieces[0].entire_source_row_in_band)splitBands++;for(const piece of pieces){whole+=piece.groups.filter(g=>g.positive).length;partial+=piece.groups.filter(g=>!g.positive&&!g.unresolved).length;unresolved+=piece.groups.filter(g=>g.unresolved).length;}if(pieces.length===1&&pieces[0].entire_source_row_in_band&&pieces[0].full_line)full++;}
 const resolved=unresolved===0&&splitBands===0;return {id:raw.id,index:raw.index,status:resolved?'measured':'unresolved',source:'Native word groups reconciled to existing crop font bands',whole_neighbour_words:whole,partial_neighbour_words:partial,unresolved_neighbour_words:unresolved,whole_word_count_resolved:resolved,additional_full_line_count:full,split_neighbour_bands:splitBands,physical_neighbour_band_count:physical.size,group_bindings:groupBindings,raw_target_row_id:raw.target_row_id,qualification:raw.qualification};
}
for await(const line of readline.createInterface({input:process.stdin,crlfDelay:Infinity})){
 try{const request=JSON.parse(line);if(request.policy_sha256!==policySha)throw Error('frozen policy hash mismatch');
 const result=request.operation==='reconcile'?reconcile(request.context,request.crop):context.combinedBoxJudgement(request.evidence);
 process.stdout.write(JSON.stringify({ok:true,result})+'\n');
 }catch(error){process.stdout.write(JSON.stringify({ok:false,error:String(error)})+'\n');}
}
