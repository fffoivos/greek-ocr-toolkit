def canonical_result(row,tool,status,edits,evidence):
    out=dict(tool=tool,tool_version=versions[tool]['version'],tool_digest=versions[tool]['digest'],binding=identity(row),
        raw_text_sha256=digest(row['raw_text']),status=status,edits=edits,evidence=evidence)
    validate_result(out,row,tool,versions)
    return out

def legacy_convert(row,tool,r,path):
    raw=row['raw_text'];parent=r.get('parent_label',r.get('label_parent',r.get('parent_text')))
    parent_sha=r.get('parent_text_sha256',r.get('original_label_sha256',r.get('parent_utf8_sha256')))
    assert parent==raw if parent is not None else parent_sha==digest(raw),(tool,row['id'])
    target=r.get('new_label',r.get('text',r.get('label',raw)))
    holds=r.get('holds',r.get('hold_slots',[]))
    edits=[] if holds else span_edits(raw,target)
    state='required_evidence_unresolved' if holds or r.get('status') in {'hold','failed','out_of_scope'} else 'applied' if edits else 'verified_no_change'
    evidence=dict(source_artifact=str(path),source_artifact_sha256=artifact_shas[str(path)],original_record_sha256=digest(canonical(r)),
        original_status=r.get('status','ok'),holds=holds,producer={k:r[k] for k in ['source_job','variant','policy_digest','wave'] if k in r},
        parent_label_conversion='parent_label -> exact raw_text' if 'parent_label' in r else 'exact raw parent verified')
    return canonical_result(row,tool,state,edits if state=='applied' else [],evidence)

def n1_candidates(text):
    return [s for t in tokens.tokenize(text) if t.digit_count>=4 for s in t.slots if not s.boundary and s.glyph in ('-','.')]

