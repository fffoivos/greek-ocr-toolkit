"""Exercise the captured parent's real UNKNOWN-row branch on tiny in-memory data."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import numpy as np

class ParentAdmission(unittest.TestCase):
    def test_unknown_new_tuple_quarantined_whole_old_row_preserved(self):
        root=Path(__file__).resolve().parent
        common=types.ModuleType('scripts.labelfix.clariden.r1_common')
        common.HEADS={'breathing':range(3),'accent':range(4),'diaeresis':range(2),'subscript':range(2)}
        common.rows=lambda p: [json.loads(s) for s in Path(p).read_text().splitlines()]
        common.sha256=lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
        common.verify_receipt=lambda p: self.fail('UNKNOWN tuple must not reach extra-pool extraction')
        spec=importlib.util.spec_from_file_location('captured_r2_manifest',root/'evidence/r2_manifest.py')
        module=importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules,{'scripts.labelfix.clariden.r1_common':common}):
            spec.loader.exec_module(module)
        old=types.SimpleNamespace(path=Path('/synthetic'),arm='A',index=np.zeros(1,dtype=[('letter','i4'),('mask','i4'),('target','i1',(4,))]))
        # __len__ belongs on the class, not the instance.
        class Old:
            path=old.path
            arm=old.arm
            index=old.index
            def __len__(self): return len(self.index)
        old=Old()
        meta=[dict(slot_id=['a'*64,0],line_id='old-line',doc='old-doc',source='old-source',crop='old-crop')]
        module.inventory_ids=lambda dataset,inventory:meta
        r=dict(slot_id=['b'*64,0],line_id='new-line',doc='new-doc',source='new-source',
            role='train',provenance='native_print',targets=[1,0,None,None],
            unknown=['diaeresis','subscript'],loss_weight=1,pool='native')
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'manifest.jsonl';p.write_text(json.dumps(r)+'\n')
            pool=module.ManifestPool(old,p,p)
        self.assertEqual(len(pool),1)
        self.assertEqual(pool.quarantined,[r])
        self.assertEqual(pool.binding['quarantined'],1)
        self.assertTrue(pool.binding['old_pool_identity'])
        np.testing.assert_array_equal(pool.index['target'],old.index['target'])

if __name__=='__main__':
    unittest.main()
