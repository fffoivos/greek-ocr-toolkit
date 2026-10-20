import tempfile
from pathlib import Path
import unittest
from greekocr.harvest.line_pipeline_census import Ledger
from greekocr.harvest.line_pipeline import digest, identity
from greekocr.harvest import admission


class ExternalCropInput(unittest.TestCase):
    def test_external_crop_uses_existing_heldout_disposition(self):
        crop='f'*64
        with tempfile.TemporaryDirectory() as tmp:
            ledger=Ledger(Path(tmp)/'ledger.sqlite',{'config':{'final_policy':{'heldout_crop_sha256':[crop]}}})
            row=dict(parent_id='train',id='row',split='train',source='fixture',book_id='book',edition_id='book',page_id='page',raw_text='λέξεις αρκετές για έλεγχο',crop_sha256=crop)
            ledger.register(row,admission.load_codec())
            ledger.save_decision(row,dict(binding=identity(row),disposition='ADMIT',admitted=True,final_text_sha256=digest(row['raw_text']),reasons=[]))
            ledger.deduplicate()
            import json
            decision=json.loads(ledger.db.execute('select payload from decisions').fetchone()[0])
            self.assertEqual(decision['disposition'],'DROP')
            self.assertEqual(decision['reasons'],[{'reason':'heldout_crop_identity'}])
            ledger.db.close()


if __name__=='__main__':unittest.main()
