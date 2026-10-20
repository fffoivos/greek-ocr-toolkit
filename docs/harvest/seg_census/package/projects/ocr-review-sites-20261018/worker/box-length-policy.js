// Independent OCR-length screen using the measured target text box.
// Geometry, script coverage, component count and body-height proxies are
// reported separately. They cannot short-circuit this numerical comparison.
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
function detectedRowsJudgement(row,maxWholeWords=2){
 if(!row.box_evidence?.available||!row.detected_rows?.length)return {verdict:'UNCERTAIN',reason:'No target text box and detected row were established.'};
 if(row.orientation_resolved===false)return {verdict:'UNCERTAIN',reason:'The reading direction remains unresolved.'};
 const lines=row.detected_rows.filter(l=>Number.isFinite(l.votes)&&l.votes>0);
 if(!lines.length)return {verdict:'UNCERTAIN',reason:'The detector returned no row with observed support.'};
 const n=row.neighbour_evidence;
 // A vertically complete band is not proof of an entire second printed line.
 // Native source-row extent and whole-word evidence supply those distinctions.
 if(n?.additional_full_line_count>0)return {verdict:'DROP',reason:'A second complete printed line is visible.'};
 if(n?.whole_word_count_resolved!==false&&Number.isFinite(n?.whole_neighbour_words)&&n.whole_neighbour_words>maxWholeWords)return {verdict:'DROP',reason:'More than '+maxWholeWords+' complete neighbouring words are visible.'};
 if(n?.status==='measured'&&n.whole_word_count_resolved!==false&&Number.isFinite(n.whole_neighbour_words))return {verdict:'KEEP',reason:'No second complete line; '+n.whole_neighbour_words+' complete neighbouring word'+(n.whole_neighbour_words===1?'':'s')+' within the allowance. Clipped words are allowed.'};
 if((n?.status==='unresolved'||n?.status==='unavailable')&&lines.some(l=>l.side!=='main'))return {verdict:'UNCERTAIN',reason:'The complete neighbouring-word count or line extent is unresolved.'};
 if(lines.some(l=>l.side!=='main'))return {verdict:'UNCERTAIN',reason:'Native word evidence is needed to distinguish complete words from fragments.'};
 return {verdict:'KEEP',reason:'One target row; no neighbouring text was detected.'};
}
function paddingJudgement(row,maxPaddingHeights=1.5){
 const p=row.padding_evidence;
 if(!p?.available||!Number.isFinite(p.total_padding_line_heights))return {verdict:'UNCERTAIN',reason:'Target-line height or vertical padding is unavailable.'};
 return p.total_padding_line_heights>maxPaddingHeights?{verdict:'DROP',reason:'Top and bottom padding together exceed '+maxPaddingHeights+' target-line heights.'}:{verdict:'KEEP',reason:'Combined top and bottom padding is within '+maxPaddingHeights+' target-line heights.'};
}
function combinedBoxJudgement(row,lower=.5,upper=1.5,mode=2,options={}){
 const length=boxLengthJudgement(row,lower,upper,mode),geometry=detectedRowsJudgement(row,options.maxWholeWords??2),padding=paddingJudgement(row,options.maxPaddingHeights??1.5);
 // A decisive failure survives uncertainty in an independent check.
 if(length.verdict==='DROP')return length;
 if(geometry.verdict==='DROP')return geometry;
 if(padding.verdict==='DROP')return padding;
 if(length.verdict==='UNCERTAIN')return length;
 if(geometry.verdict==='UNCERTAIN')return geometry;
 if(padding.verdict==='UNCERTAIN')return padding;
 return {verdict:'KEEP',reason:'OCR length matches; neighbouring words and vertical padding are within the selected allowances, with no second complete line.'};
}
