"""Offline regression for LF4 flagged-slot pairing by scope rank."""
import unittest

from prod_finalize import finalize, seal_rows
from test_lf2d import candidate


class PairingTests(unittest.TestCase):
    def test_shuffled_slots_get_ok_reserves_by_scope_rank_and_source(self):
        # Draw order opposes slot rank and reserve order. The first reserve
        # is non-OK; the foreign source must consume only its own reserve.
        cs=[candidate('high',3),candidate('foreign-slot',2,source='other'),
            candidate('low',1),candidate('unfilled',4),candidate('ok',5),
            candidate('reserve-later',9,False),candidate('blocked',6,False),
            candidate('foreign-reserve',7,False,source='other'),
            candidate('reserve-first',8,False)]
        vs=[dict(line_id=r['row_id'],verdict='OK' if r['row_id'] in
                 ('ok','reserve-first','reserve-later','foreign-reserve')
                 else 'CROP_VIOLATES') for r in cs]
        final,details=finalize(cs,vs)
        self.assertEqual({r['flagged_id']:r['replacement_id']
                          for r in details['replacements']},
                         {'low':'reserve-first','high':'reserve-later',
                          'foreign-slot':'foreign-reserve','unfilled':None})
        self.assertEqual({r['row_id']:r['replaces'] for r in
                          seal_rows(final,details,cs,'0'*64)},
                         {'reserve-first':dict(parent_id='SYNTHETIC',row_id='low'),
                          'reserve-later':dict(parent_id='SYNTHETIC',row_id='high'),
                          'foreign-reserve':dict(parent_id='SYNTHETIC',row_id='foreign-slot'),
                          'ok':None})
        self.assertEqual({k:sum(r[k] for r in details['summary'])
                          for k in ('flagged','REPLACED','UNFILLED')},
                         dict(flagged=4,REPLACED=3,UNFILLED=1))


if __name__=='__main__':unittest.main(verbosity=2)
