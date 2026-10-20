// Segmentation 0.8: exactly the owner's three rules, in this order:
// 1. Other lines: additional complete line or >2 whole words; cut-off words do not count.
// 2. De-skewed main-row box length, height-normalised through the frozen predictor.
// 3. Crop height <= upright box height + 1.5 * de-skewed line height.
// Cut evidence and optional source context are diagnostics only.
// KEEP here passes this screen only; it is not a training-admission certificate.
function boxLengthJudgement(row,lower=.5,upper=1.5,mode=2){
 const e=row.box_evidence,chars=row.characters;
 if(!e?.available)return {verdict:'UNCERTAIN',reason:'No usable text box was measured.'};
 const expected=e.predictions?.[mode];
 if(!Number.isFinite(chars)||chars<0||!Number.isFinite(expected)||expected<0)return {verdict:'UNCERTAIN',reason:'Text-box prediction or saved character count is unavailable.'};
 if(!Number.isFinite(lower)||!Number.isFinite(upper)||lower<=0||lower>=upper)return {verdict:'UNCERTAIN',reason:'The selected output-length interval is invalid.'};
 const ratio=(chars+1)/(expected+1);
 return ratio<lower?{verdict:'DROP',reason:'Too little OCR output for the text box after height normalisation.'}:ratio>upper?{verdict:'DROP',reason:'Too much OCR output for the text box after height normalisation.'}:{verdict:'KEEP',reason:'OCR output agrees with the height-normalised text-box length.'};
}
// Stage A is crop-only. Source-context counts are diagnostic evidence only.
function lineInventoryJudgement(row,maxWholeWords=2){
 const lines=row.lines??[],main_cut=row.gate?.main_cut??{};
 const neighbours=lines.filter(l=>l.side!=='main');
 const result={verdict:'PASS',reason:'gate: pass',whole_words:neighbours.reduce((n,l)=>n+l.whole_words,0),cutoff_words:neighbours.reduce((n,l)=>n+l.cutoff_words,0),complete_rows:neighbours.filter(l=>l.complete).map(l=>l.index),main_cut};
 if(!lines.some(l=>l.side==='main'&&l.votes>0))return {...result,verdict:'UNCERTAIN',reason:'gate: no main row found'};
 if(row.orientation_resolved===false)return {...result,verdict:'UNCERTAIN',reason:'gate: reading direction unresolved'};
 if(result.complete_rows.length)return {...result,verdict:'DROP',reason:'gate: second complete line'};
 if(result.whole_words>maxWholeWords)return {...result,verdict:'DROP',reason:'gate: too many whole neighbour words'};
 return result;
}
function paddingJudgement(row,maxPaddingHeights=1.5){
 const p=row.padding_evidence;
 if(!p?.available||!Number.isFinite(p.total_padding_line_heights))return {verdict:'UNCERTAIN',reason:'Target-line height or vertical padding is unavailable.'};
 return p.total_padding_line_heights>maxPaddingHeights?{verdict:'DROP',reason:'Top and bottom padding together exceed '+maxPaddingHeights+' target-line heights.'}:{verdict:'KEEP',reason:'Combined top and bottom padding is within '+maxPaddingHeights+' target-line heights.'};
}
function combinedBoxJudgement(row,lower=.5,upper=1.5,mode=2,options={}){
 const gate=lineInventoryJudgement(row,options.maxWholeWords??2);
 if(row.gate_only===true)return gate;
 if(gate.verdict!=='PASS')return {verdict:gate.verdict,reason:gate.reason};
 const length=boxLengthJudgement(row,lower,upper,mode);
 if(length.verdict!=='KEEP')return {...length,reason:'length: '+length.reason};
 const padding=paddingJudgement(row,options.maxPaddingHeights??1.5);
 if(padding.verdict!=='KEEP')return {...padding,reason:'length: '+padding.reason};
 return {verdict:'KEEP',reason:'length: OCR length matches; vertical padding is within the selected allowance.'};
}
