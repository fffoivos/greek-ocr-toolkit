"""Offline ADM3 byte preservation, selection, metadata, hash and summary checks."""
from collections import Counter
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import append_adm3_headings_caps as adm


class ADM3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = adm.baseline()
        cls.data = adm.ADMISSIONS.read_bytes()
        cls.lines = cls.data.splitlines(keepends=True)
        cls.rows = [json.loads(l) for l in cls.lines]
        cls.new, cls.counts, cls.dropped, cls.inputs = adm.candidates()
        cls.summary = adm.load(adm.SUMMARY)
        cls.recs = adm.records(adm.W / 'caps_masked/records.jsonl')
        ids = {r['row_id'] for r in cls.new}
        cls.w1 = adm.records(adm.RUN / 'W1/features.jsonl', ids)
        with (adm.RUN / 'W1/crop_tight_page.jsonl').open() as stream:
            for line in stream:
                r = json.loads(line)
                if r['id'] in ids: cls.w1[r['id']] = r

    def test_01_wave_subset_byte_unchanged(self):
        subset = b''.join(l for l,r in zip(self.lines,self.rows) if r['arm']==adm.WAVE_ARM)
        self.assertEqual(adm.digest(subset), adm.prior.BASE_SHA)
        self.assertEqual(subset, adm.prior.baseline()[0])

    def test_02_kosmopolis_subset_byte_unchanged(self):
        subset = b''.join(l for l,r in zip(self.lines,self.rows)
                         if r['arm']==adm.ARM and r['primary_class']=='poly1850')
        self.assertEqual(adm.digest(subset), adm.KOSMO_SHA)
        self.assertEqual(sum(r['arm']==adm.ARM and r['primary_class']=='poly1850' for r in self.rows),462)
        self.assertEqual(self.data[:len(self.base)], self.base)

    def test_03_arm_and_class_filters(self):
        self.assertEqual(sum(r['arm']==adm.WAVE_ARM for r in self.rows),16562)
        self.assertEqual(sum(r['arm']==adm.ARM and r['primary_class']=='headings_caps' for r in self.rows),1626)
        self.assertEqual(Counter(r['arm'] for r in self.rows),{adm.WAVE_ARM:16562,adm.ARM:2088})
        self.assertEqual(self.summary['candidate_filter_counts'],dict(wave1d=16562,kosmopolis_poly1850=462,headings_caps=1626))
        self.assertEqual(self.summary['arm_filter_counts'],{'wave-1d':0,adm.WAVE_ARM:16562,adm.ARM:2088})

    def test_04_exact_candidate_suffix_unique_and_ordered(self):
        self.assertEqual(self.data[len(self.base):],adm.encode(self.new))
        self.assertEqual(len({r['row_id'] for r in self.rows}),18650)
        self.assertEqual([r['row_id'] for r in self.new],sorted(r['row_id'] for r in self.new))

    def test_05_new_row_fields_metadata_and_provenance(self):
        old = json.loads(self.base.splitlines()[-1])
        for r in self.new:
            self.assertEqual(set(r),set(old))
            self.assertEqual((r['arm'],r['marks_status'],r['primary_class'],r['tranche']),
                             (adm.ARM,'pending_opus','headings_caps','W1'))
            self.assertEqual(r['provenance']['sol_reading'],'sol/recut-v1 abaa200c')
            self.assertEqual(r['provenance']['caps3_build'],'sol/recut-v1 d8c31c97')
            self.assertEqual(r['provenance']['clip_screen'],adm.screen_provenance(self.inputs))
            w=self.w1[r['row_id']]
            for key in ('label','page_id','source'): self.assertEqual(r[key],w[key])
            self.assertEqual(r['line_index'],int(r['row_id'].rsplit('-l',1)[1]))
            self.assertEqual(r['gazette_stratum'],w.get('gazette_stratum') if r['source']=='gazette_modern' else None)

    def test_06_every_crop_hash_and_collector_hash(self):
        for r in self.new:
            x=self.recs[r['row_id']]
            want=x['masked_crop_sha256'] if x['output_kind']=='masked' else x['original_crop_sha256']
            self.assertEqual(adm.sha(r['crop']),want)
            self.assertEqual(r['crop_sha256'],want)
            self.assertEqual(r['original_crop_sha256'],self.w1[r['row_id']]['crop_sha256'])
            self.assertEqual(r['crop_masked_tag'],'crop_masked' if x['output_kind']=='masked' else None)
        self.assertEqual(Counter(r['guard_status'] for r in self.new),{'masked':1623,'guarded_original':3})

    def test_07_all_release_exclusion_classes_and_screens(self):
        excluded=set()
        for name,spec in self.inputs.items():
            if name.startswith('exclusion_ids:'): excluded.update(Path(spec['path']).read_text().split())
        self.assertIn('exclusion_ids:n1_locked_eval',self.inputs)
        screen=adm.records(adm.CAPS/'screen.jsonl')
        for r in self.new:
            rid=r['row_id']
            self.assertNotIn(rid,excluded)
            self.assertFalse(screen[rid]['flagged'])
            self.assertFalse(self.w1[rid].get('screen_merged'))
            self.assertFalse(self.recs[rid].get('screen_merged'))
            self.assertFalse(self.recs[rid].get('rotated_crop'))

    def test_08_count_reconciliation_and_exact_dropped_ids(self):
        self.assertEqual({k:v for k,v in self.counts.items() if not k.startswith('collector:')},{'screen_pool':2211,'admitted':1626,'edge_clip_screen':544,'output_kind:unmatched_original':37,'release_exclusions_line_class':2,'screen_merged':2})
        self.assertEqual(sum(v for k,v in self.counts.items() if k.startswith('collector:')),1626)
        pool=set(adm.records(adm.CAPS/'keys/pool.jsonl'))
        dropped={rid for ids in self.dropped.values() for rid in ids}
        self.assertEqual(pool-{r['row_id'] for r in self.new},dropped)
        self.assertEqual(self.summary['adm3']['difference_from_1629'],-3)

    def test_09_screen_helper_tolerance_and_validation(self):
        s=self.summary['adm3']['edge_clip_screen']
        receipt=adm.load(adm.CAPS/'screen_receipt.json')
        self.assertEqual(s['helper'],receipt['helper'])
        self.assertEqual(s['tolerance'],{'cut_left':['left_fraction','gt',0.0],'cut_right':['right_fraction','gt',0.0]})
        self.assertEqual(s['removed'],544)
        self.assertEqual(s['removed_per_source'],{'bsb_poly1850':19,'elstat':0,'gazette_modern':433,'ia_greek_latin':1,'ia_poly1850':25,'kosmopolis':12,'lekythos':38,'nlg':16})
        self.assertEqual(s['caps2_validation'],dict(clipped_flagged=6,clipped_n=6,false_positives=17,crop_ok_n=89))
        validation=receipt['caps2_validation']
        self.assertEqual(sum(x['flagged'] and 'crop_clipped' in x['verdict']['errors'] for x in validation),6)
        self.assertEqual(sum(x['flagged'] and x['verdict']['crop_ok']=='y' for x in validation),17)

    def test_10_hash_rejections_and_guarded_branch(self):
        row=next(r for r in self.new if r['guard_status']=='guarded_original')
        w,x=self.w1[row['row_id']],self.recs[row['row_id']]
        self.assertEqual(adm.make_row(w,x,adm.screen_provenance(self.inputs)),row)
        with patch.object(adm,'sha',return_value='0'*64):
            with self.assertRaisesRegex(ValueError,'CAPS3 crop hash mismatch'): adm.make_row(w,x,{})
        with self.assertRaisesRegex(ValueError,'collector crop hash mismatch'):
            adm.make_row(dict(w,crop_sha256='0'*64),x,{})
        with self.assertRaisesRegex(ValueError,'unsupported output kind'):
            adm.make_row(w,dict(x,output_kind='unmatched_original'),{})

    def test_11_summary_sha_counts_and_bound_hashes(self):
        self.assertEqual(self.summary['sha256'],adm.digest(self.data))
        self.assertEqual(self.summary['wave1d_subset_sha256'],adm.prior.BASE_SHA)
        self.assertEqual(self.summary['kosmopolis_subset_sha256'],adm.KOSMO_SHA)
        self.assertEqual(self.summary['bound_inputs'],adm.bindings())
        self.assertEqual(self.summary['release_exclusions_sha256'],self.inputs['release_exclusions']['sha256'])
        want=Counter((r['arm'],r['source'],r['primary_class']) for r in self.rows)
        self.assertEqual(want,{(r['arm'],r['source'],r['primary_class']):r['rows'] for r in self.summary['counts_per_arm_source_class']})
        self.assertEqual(self.summary,adm.expected_summary(self.base,self.new,self.counts,self.dropped,self.inputs))

    def test_12_append_refuses_unexpected_bytes(self):
        with patch.object(adm,'candidates',return_value=(self.new,self.counts,self.dropped,self.inputs)):
            with patch.object(Path,'read_bytes',return_value=b'unexpected'):
                with patch.object(adm,'baseline',return_value=self.base):
                    with self.assertRaisesRegex(ValueError,'refusing unexpected admissions'): adm.append()


if __name__=='__main__': unittest.main()
