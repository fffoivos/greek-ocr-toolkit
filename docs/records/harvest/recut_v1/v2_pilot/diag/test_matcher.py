"""Boundary and index-preservation checks; no fixture or cache writes."""
import os
import sys
sys.dont_write_bytecode=True
for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
    os.environ[name]='1'
import unittest
from run_diag import install_guard
install_guard()
import numpy as np
from matcher import LineFit, candidates, match, original_match


class EligibilityTests(unittest.TestCase):
    def fit(self,centre,x0=0,x1=100,xh=10):
        return LineFit(x0,x1,np.full(x1-x0,centre,dtype=float),xh,xh,xh,0,(x0,0,x1,1))

    def test_existing_fifty_percent_gate_is_real(self):
        box=(0,40,100,60)
        self.assertIsNone(original_match(box,[self.fit(50,0,49)]))
        self.assertEqual(original_match(box,[self.fit(50,0,50)]),0)

    def test_opt_in_preserves_inclusive_boundaries(self):
        box=(0,40,100,60)
        self.assertEqual(match(box,[self.fit(65,0,50)],min_horizontal_overlap=.5),0)
        self.assertIsNone(match(box,[self.fit(65.0001)],min_horizontal_overlap=.5))

    def test_filter_preserves_original_global_index_and_ranking(self):
        box=(0,40,100,60)
        fits=[self.fit(50,0,60),self.fit(55),self.fit(53),self.fit(48)]
        self.assertEqual(original_match(box,fits),0)
        self.assertEqual(match(box,fits,min_horizontal_overlap=.75),3)
        self.assertEqual([r['index'] for r in candidates(box,fits,min_horizontal_overlap=.75)],[3,2,1])

    def test_ties_preserve_original_index_order_after_filter(self):
        fits=[self.fit(50,0,60),self.fit(50),self.fit(50)]
        self.assertEqual(match((0,40,100,60),fits,min_horizontal_overlap=.75),1)
        self.assertEqual([r['index'] for r in candidates((0,40,100,60),fits,min_horizontal_overlap=.75)],[1,2])

    def test_default_and_redundant_gate_preserve_original(self):
        box=(0,40,100,60)
        for fits in ([],[self.fit(50,150,250)],[self.fit(70),self.fit(50)],[self.fit(50),self.fit(50)]):
            self.assertEqual(match(box,fits),original_match(box,fits))
            self.assertEqual(match(box,fits,min_horizontal_overlap=.5),original_match(box,fits))
            self.assertEqual(candidates(box,fits),candidates(box,fits,min_horizontal_overlap=.5))

    def test_opt_in_cannot_weaken_existing_gate(self):
        self.assertIsNone(match((0,40,100,60),[self.fit(50,0,49)],min_horizontal_overlap=0))

    def test_invalid_threshold_rejected(self):
        for threshold in (-.01,1.01,float('nan')):
            with self.assertRaises(ValueError):
                match((0,40,100,60),[],min_horizontal_overlap=threshold)

    def test_network_and_external_writes_denied(self):
        import socket
        from run_diag import PILOT
        with self.assertRaises(PermissionError):
            socket.getaddrinfo('localhost',80)
        with self.assertRaises(PermissionError):
            (PILOT/'T6c1b_forbidden_probe').open('w')


if __name__=='__main__':
    unittest.main(verbosity=2)
