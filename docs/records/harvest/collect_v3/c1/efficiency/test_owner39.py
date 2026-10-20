"""Owner39 protocol, isolation, scoring arithmetic and legacy regressions."""
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import types
import unittest

sys.dont_write_bytecode=True
import owner39_common as common
import owner39_score as owner
from owner39_validate import validate_pack
from test_efficiency import ROOT, fixture, scorer

PROJECTS=ROOT.parents[5]
EVIDENCE=PROJECTS/'greek-ocr-toolkit-spellcheck/docs/labelfix/spellcheck/R2_evidence'
R2=PROJECTS/'greek-ocr-toolkit-spellcheck-r2cards'


def read(path):
    return json.loads(path.read_text())


def rows(path):
    return [json.loads(s) for s in path.read_text().splitlines()]


def perfect(t):
    # Test-only form construction, never a reader artifact. Owner-unknown
    # breathing deliberately remains unknown in the submitted heads.
    marks={'breathing':{'psili':'\u0313','dasia':'\u0314'},'accent':{'acute':'\u0301','grave':'\u0300','circumflex':'\u0342'},
           'diaeresis':{'present':'\u0308'},'subscript':{'present':'\u0345'}}
    chars=[c for c in common.clusters(t['truth_word']) if common.is_letter(c[0])]
    chars[t['anchor_index']]=t['base']+''.join(marks[h].get(t['heads'][h],'') for h in common.HEADS)
    text=common.literal_normalize('NFC',''.join(chars))
    return dict(card_id=t['card_id'],choice='literal',transcription=text,anchor_heads=dict(t['heads']),letter_heads=[],
                readability='readable',ownership_ok=True if any(v not in ('none','unknown') for v in t['heads'].values()) else None,
                confidence='high',note='',usage={'input_tokens':0,'output_tokens':0})


class OwnerPackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=read(ROOT/'MANIFEST.json');cls.truth=read(ROOT/'keys/owner39/truth.json')
        cls.packs=[p for p in cls.manifest['packs'] if p['bed']=='owner39']

    def test_34_all_cards_two_readers_and_reverse_seeded_order(self):
        self.assertEqual(len(self.truth),39);self.assertEqual(len(self.packs),8)
        self.assertEqual(self.manifest['per_item_reads_per_arm'],{'bsb':1,'yer':1,'owner39':2})
        for arm in ('E0a','E0b','E2','E3'):
            order=sorted(self.truth);random.Random('eff:owner39:'+arm).shuffle(order)
            self.assertEqual(next(p['item_ids'] for p in self.packs if p['arm']==arm and p['reader']=='r1'),order)
            self.assertEqual(next(p['item_ids'] for p in self.packs if p['arm']==arm and p['reader']=='r2'),list(reversed(order)))
        self.assertNotEqual(read(ROOT/'keys/owner39/E0a.json')['order'],read(ROOT/'keys/owner39/E0b.json')['order'])

    def test_35_e0_t4_verbatim(self):
        protocol=(EVIDENCE/'READER_PROTOCOL_R2.md').read_text().split('## Reader prompt (verbatim, T4 version, which adds two rules learned on T2)\n\n')[1].split('\n## Resolver')[0].strip()+'\n'
        for p in self.packs:
            if p['arm'] in ('E0a','E0b'):self.assertEqual((ROOT/p['path']/'PROTOCOL.md').read_text(),protocol)

    def test_36_readme_and_answer_schema_verbatim_all_readers(self):
        blind=R2/'docs/labelfix/spellcheck/R2/decks/T2/blind'
        for p in self.packs:
            for name in ('README.md','answer_schema.json'):self.assertEqual((ROOT/p['path']/name).read_bytes(),(blind/name).read_bytes())

    def test_37_e2_only_native_image_sentence_changed(self):
        # Extract the replacement constants without importing Pillow/the builder.
        tree=ast.parse((ROOT/'build_owner39.py').read_text()); constants={}
        for n in tree.body:
            if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ('OLD_IMAGE_SENTENCE','NEW_IMAGE_SENTENCE'):
                constants[n.targets[0].id]=ast.literal_eval(n.value)
        control=(ROOT/'packs/owner39/E0a/r1/PROTOCOL.md').read_text()
        changed=control.replace(constants['OLD_IMAGE_SENTENCE'],constants['NEW_IMAGE_SENTENCE'])
        for reader in ('r1','r2'):
            d=ROOT/'packs/owner39/E2'/reader;self.assertEqual((d/'PROTOCOL.md').read_text(),changed)
            for row in rows(d/'cards.jsonl'):
                self.assertNotIn('line_image',row);self.assertIn('letter_image',row)

    def test_38_e3_compact_preserves_rules_and_minimal_lines(self):
        compact=(ROOT/'packs/owner39/E3/r1/PROTOCOL.md').read_text()
        self.assertLess(len(compact),len((ROOT/'packs/owner39/E0a/r1/PROTOCOL.md').read_text()))
        for phrase in ('ONLY','no web search','zoom/','GIVEN ORDER','full native line_image','misprints','grammar','complete exact word','all four','unknown','ownership_ok','null','clearly visible blank','incrementally','planted checks','count/order','hard cards'):
            self.assertIn(phrase,compact)
        self.assertEqual(compact,(ROOT/'packs/owner39/E3/r2/PROTOCOL.md').read_text())
        for line in (ROOT/'packs/owner39/E3/r1/cards.jsonl').read_text().splitlines():
            self.assertEqual(line,json.dumps(json.loads(line),ensure_ascii=False,separators=(',',':')))

    def test_39_options_use_only_r2_stripped_bases_and_fixed_accent(self):
        original={r['db_id']:r for r in read(EVIDENCE/'reader_errors_39_owner_final.json')['cards']}
        for row in rows(ROOT/'packs/owner39/E0a/r1/cards.jsonl'):
            t=self.truth[row['card_id']];source=original[t['db_id']]
            self.assertEqual(row['options'],common.options(source['google_word'],row['anchor_index'],'accent','eff:owner39:options:'+row['card_id']))
            self.assertEqual(set(row),{'card_id','word_image','line_image','anchor_index','anchor_base','options','extra_options'})

    def test_40_sources_rehashed_unchanged(self):
        for p,h in read(ROOT/'keys/owner39/source_hashes.json').items():self.assertEqual(hashlib.sha256(Path(p).read_bytes()).hexdigest(),h)

    def test_41_existing_beds_and_keys_byte_unchanged(self):
        for p,h in read(ROOT/'keys/build2_prebuild_state.json')['frozen_beds'].items():self.assertEqual(hashlib.sha256((ROOT.parents[4]/p).read_bytes()).hexdigest(),h)

    def test_42_legacy_scorer_exact_regression(self):
        source=subprocess.check_output(['git','show','b8658ae0:docs/harvest/collect_v3/c1/efficiency/score.py'],cwd=ROOT.parents[4],text=True)
        old=types.ModuleType('legacy_scorer');old.__file__=str(ROOT/'score.py');exec(compile(source,old.__file__,'exec'),old.__dict__)
        m,t,s=fixture()
        for variant in ('perfect','partial','unknown'):
            current=copy.deepcopy(s)
            if variant=='partial':current=current[:3]
            if variant=='unknown':current[0][3][0]['letters']='u'
            usage={('bsb','E1','r1'):dict(total_tokens=123,tool_uses=7,duration_ms=800)}
            self.assertEqual(scorer.score(m,t,current,usage),old.score(m,t,current,usage))

    def test_43_templates_extend_original_twenty_readers(self):
        for name in ('usage','verdicts'):
            path=f'docs/harvest/collect_v3/c1/efficiency/keys/{name}.template.json'
            original=json.loads(subprocess.check_output(['git','show','b8658ae0:'+path],cwd=ROOT.parents[4]))
            actual=read(ROOT/f'keys/{name}.template.json')['readers']
            self.assertEqual(actual[:20],original['readers']);self.assertEqual(len(actual),28)
            self.assertEqual({(r['bed'],r['arm'],r['reader']) for r in actual[20:]},{('owner39',a,r) for a in ('E0a','E0b','E2','E3') for r in ('r1','r2')})

    def test_44_isolation_rejects_extra_truth_even_if_manifest_lists_it(self):
        pack=copy.deepcopy(self.packs[0])
        with tempfile.TemporaryDirectory(dir=ROOT,prefix='.test-owner-') as td:
            root=Path(td);dest=root/pack['path'];shutil.copytree(ROOT/pack['path'],dest)
            (dest.parent/'r2').mkdir()
            evil=dest/'owner_truth.json';evil.write_text('{}')
            pack['files'].append(dict(path=str(evil.relative_to(root)),sha256=hashlib.sha256(evil.read_bytes()).hexdigest(),bytes=2))
            with self.assertRaises(AssertionError):validate_pack(root,pack)

    def test_45_isolation_rejects_symlink(self):
        pack=copy.deepcopy(self.packs[0])
        with tempfile.TemporaryDirectory(dir=ROOT,prefix='.test-owner-') as td:
            root=Path(td);dest=root/pack['path'];shutil.copytree(ROOT/pack['path'],dest)
            (dest.parent/'r2').mkdir();p=next((dest/'img').iterdir());p.unlink();p.symlink_to(ROOT/'keys/owner39/truth.json')
            with self.assertRaises(AssertionError):validate_pack(root,pack)

    def test_46_owner_status_and_breathing_exception(self):
        self.assertEqual(Counter(t['owner_status'] for t in self.truth.values()),{'left_as_shown':38,'noted':1})
        special=next(t for t in self.truth.values() if t['owner_status']=='noted')
        self.assertEqual(special['db_id'],'384c3f89-p000059-l0013:s33')
        self.assertEqual(special['heads']['accent'],'circumflex');self.assertEqual(special['heads']['breathing'],'unknown')
        self.assertNotIn('breathing',special['scored_heads'])

    def test_63_isolation_rejects_actual_owner_note_inside_allowed_file(self):
        pack=copy.deepcopy(self.packs[0])
        with tempfile.TemporaryDirectory(dir=ROOT,prefix='.test-owner-') as td:
            root=Path(td);dest=root/pack['path'];shutil.copytree(ROOT/pack['path'],dest)
            (dest.parent/'r2').mkdir();(root/'keys/owner39').mkdir(parents=True)
            for name in ('truth.json','input_mapping.json'):shutil.copyfile(ROOT/'keys/owner39'/name,root/'keys/owner39'/name)
            note=next(t['owner_note'] for t in self.truth.values() if t['owner_note'])
            p=dest/'PROTOCOL.md';p.write_text(p.read_text()+'\n'+note+'\n')
            f=next(f for f in pack['files'] if f['path'].endswith('/PROTOCOL.md'))
            f.update(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
            with self.assertRaisesRegex(AssertionError,'Private owner/source text'):validate_pack(root,pack)

    def test_64_isolation_rejects_hardlink_even_with_bound_manifest(self):
        pack=copy.deepcopy(self.packs[0])
        with tempfile.TemporaryDirectory(dir=ROOT,prefix='.test-owner-') as td:
            root=Path(td);dest=root/pack['path'];shutil.copytree(ROOT/pack['path'],dest)
            (dest.parent/'r2').mkdir();source=next((dest/'img').iterdir());alias=dest/'img/duplicate.png';os.link(source,alias)
            pack['files'].append(dict(path=str(alias.relative_to(root)),sha256=hashlib.sha256(alias.read_bytes()).hexdigest(),bytes=alias.stat().st_size))
            with self.assertRaises(AssertionError):validate_pack(root,pack)


from collections import Counter


class OwnerScorerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=read(ROOT/'MANIFEST.json');cls.truth=read(ROOT/'keys/owner39/truth.json')
        cls.items={r['card_id']:r for r in rows(ROOT/'packs/owner39/E0a/r1/cards.jsonl')}

    def setUp(self):
        self.submissions=[('owner39',a,r,[perfect(t) for t in self.truth.values()]) for a in ('E0a','E0b','E2','E3') for r in ('r1','r2')]

    def result(self,usage=None):
        return scorer.score(self.manifest,read(ROOT/'keys/truth.json'),self.submissions,usage)['beds']['owner39']

    def test_47_perfect_truth_and_replicates(self):
        result=self.result();a=result['arms']['E0a']
        self.assertTrue(a['complete']);self.assertEqual(a['submitted_readers'],2)
        for reader in ('r1','r2'):
            v=a['readers'][reader]['agreement_with_truth']
            self.assertEqual(v['all_fields_per_card']['agree'],39);self.assertEqual(v['fields']['breathing']['expected'],38)
            self.assertEqual(v['fields']['accent']['expected'],39)
            self.assertEqual(result['E0a_E0b_agreement'][reader]['all_fields_per_card']['agree'],39)

    def test_48_unknown_is_not_none_or_credit(self):
        self.submissions[0][3][0]['anchor_heads']['accent']='unknown'
        a=self.result()['arms']['E0a']['readers']['r1']
        self.assertEqual(a['agreement_with_truth']['fields']['accent']['agree'],38)
        self.assertEqual(a['agreement_with_truth']['fields']['accent']['compared'],39)
        self.assertEqual(a['unknown_counts']['accent'],1)

    def test_49_unknown_unknown_raw_call_is_not_confirmed_agreement(self):
        for n in (0,2):self.submissions[n][3][0]['anchor_heads']['accent']='unknown'
        result=self.result()['E0a_E0b_agreement']['r1']['fields']['accent']
        self.assertEqual(result['literal_call_agree'],39);self.assertEqual(result['agree'],38)

    def test_50_noted_breathing_excluded_even_if_reader_decides(self):
        row=next(r for r in self.submissions[0][3] if self.truth[r['card_id']]['owner_status']=='noted')
        row['anchor_heads']['breathing']='dasia';row['transcription']='ἧγε'
        v=self.result()['arms']['E0a']['readers']['r1']['agreement_with_truth']
        self.assertEqual(v['fields']['breathing']['agree'],38);self.assertEqual(v['all_fields_per_card']['agree'],39)

    def test_51_wrong_base_detected_independently(self):
        row=self.submissions[0][3][0];ls=common.clusters(row['transcription']);index=self.truth[row['card_id']]['anchor_index']
        ls[index]='α'+ls[index][1:];row['transcription']=common.literal_normalize('NFC',''.join(ls))
        self.assertEqual(self.result()['arms']['E0a']['readers']['r1']['agreement_with_truth']['fields']['base']['agree'],38)

    def test_52_missing_reader_does_not_collapse_repeated_assignments(self):
        self.submissions=self.submissions[:1]
        a=self.result()['arms']['E0a'];self.assertFalse(a['complete'])
        self.assertEqual(a['readers']['r1']['agreement_with_truth']['compared_items'],39)
        self.assertEqual(a['readers']['r2']['agreement_with_truth']['compared_items'],0)
        self.assertEqual(len(a['readers']['r2']['missing_items']),39)

    def test_53_duplicate_card_and_reader_rejected(self):
        self.submissions[0][3].append(self.submissions[0][3][0])
        with self.assertRaisesRegex(ValueError,'Duplicate'):self.result()
        self.submissions[0][3].pop();self.submissions.append(self.submissions[0])
        with self.assertRaisesRegex(ValueError,'duplicate'):self.result()

    def test_54_literal_and_head_consistency_required(self):
        row=self.submissions[0][3][0];row['anchor_heads']['accent']='grave' if row['anchor_heads']['accent']!='grave' else 'acute'
        with self.assertRaisesRegex(ValueError,'disagrees with transcription'):self.result()

    def test_55_invalid_or_missing_heads_rejected(self):
        for bad in ('u',None,[]):
            row=perfect(next(iter(self.truth.values())));row['anchor_heads']['accent']=bad
            with self.subTest(bad=bad),self.assertRaises(ValueError):owner.normalize(row,self.items[row['card_id']])
        row['anchor_heads'].pop('accent')
        with self.assertRaisesRegex(ValueError,'all four'):owner.normalize(row,self.items[row['card_id']])

    def test_56_missing_usage_stays_null_zero_placeholders_ignored(self):
        cost=self.result()['arms']['E0a']['efficiency']
        self.assertIsNone(cost['tokens_per_card']);self.assertIsNone(cost['tokens_per_unique_card'])

    def test_57_measured_usage_both_denominators(self):
        usage={('owner39','E0a',r):dict(total_tokens=390,tool_uses=39,duration_ms=3900) for r in ('r1','r2')}
        cost=self.result(usage)['arms']['E0a']['efficiency']
        self.assertEqual(cost['assigned_card_reads'],78);self.assertEqual(cost['unique_cards'],39)
        self.assertEqual(cost['tokens_per_card'],10);self.assertEqual(cost['tokens_per_unique_card'],20)
        self.assertEqual(cost['tool_uses_per_unique_card'],2);self.assertEqual(cost['reader_wall_ms_per_unique_card'],200)

    def test_58_partial_usage_never_extrapolated(self):
        usage={('owner39','E0a','r1'):dict(total_tokens=390,tool_uses=39,duration_ms=3900)}
        cost=self.result(usage)['arms']['E0a']['efficiency']
        self.assertIsNone(cost['tokens_per_unique_card']);self.assertEqual(cost['readers'][0]['tokens_per_card'],10)

    def test_59_option_choice_resolves_form(self):
        item=next(iter(self.items.values()));form=item['options']['A'];head=common.tuple_heads(owner.letters(form)[item['anchor_index']])
        row=perfect(self.truth[item['card_id']]);row.update(choice='A',anchor_heads=head,ownership_ok=True if any(v!='none' for v in head.values()) else None)
        normalized=owner.normalize(row,item);self.assertEqual(normalized['heads'],head)

    def test_60_other_letter_heads_validated_but_not_scored(self):
        row=next(r for r in self.submissions[0][3] if len(owner.letters(r['transcription']))>1)
        index=next(i for i in range(len(owner.letters(row['transcription']))) if i!=self.truth[row['card_id']]['anchor_index'])
        row['letter_heads']=[dict(index=index,**{h:'unknown' for h in common.HEADS})]
        self.assertEqual(self.result()['arms']['E0a']['readers']['r1']['agreement_with_truth']['all_fields_per_card']['agree'],39)
        row['letter_heads'].append(row['letter_heads'][0])
        with self.assertRaisesRegex(ValueError,'Duplicate/invalid'):self.result()

    def test_61_cli_owner39_partial_and_usage(self):
        with tempfile.TemporaryDirectory(dir=ROOT,prefix='.test-owner-') as td:
            td=Path(td);v=td/'answers.jsonl';v.write_text(json.dumps(self.submissions[0][3][0],ensure_ascii=False)+'\n')
            u=td/'usage.json';u.write_text(json.dumps({'owner39/E0a/r1':dict(total_tokens=390,tool_uses=39,duration_ms=3900)}))
            out=td/'scores.json'
            p=subprocess.run([sys.executable,'-B',str(ROOT/'score.py'),'--verdict','owner39','E0a','r1',str(v),'--usage',str(u),'--output',str(out)],capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr)
            a=read(out)['beds']['owner39']['arms']['E0a']
            self.assertEqual(a['readers']['r1']['agreement_with_truth']['compared_items'],1)
            self.assertEqual(a['efficiency']['readers'][0]['tokens_per_card'],10)

    def test_62_unreadable_is_explicit_unknown_base_and_heads(self):
        row=self.submissions[0][3][0];row.update(choice='unreadable',anchor_heads={h:'unknown' for h in common.HEADS},readability='unreadable',ownership_ok=None)
        a=self.result()['arms']['E0a']['readers']['r1'];self.assertEqual(a['unknown_counts']['base'],1)
        self.assertEqual(a['agreement_with_truth']['all_fields_per_card']['agree'],38)


if __name__=='__main__':
    unittest.main(verbosity=2)
