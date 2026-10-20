import unittest
from greekocr.harvest.line_pipeline import automatic_result


class NumericAdjacency(unittest.TestCase):
    def result(self, text):
        row = dict(parent_id='fixture', id='row', split='train', crop_sha256='0'*64, raw_text=text)
        return automatic_result(row, 'numerics', {}, '0.2', 'd'*64)

    def test_unrelated_punctuation_is_negative(self):
        for text in ['Το 1986 τελειώνει.', 'word-word 1234', '· heading 1234', '1234.', '.1234']:
            with self.subTest(text=text):
                self.assertEqual(self.result(text)['status'], 'verified_no_change')

    def test_adjacent_candidates_remain_unresolved(self):
        for text in ['1.234', '12-34', '1·234', '1.2', '١.٢', '1 . 234', '12 - 34', '1\t·\t234']:
            with self.subTest(text=text):
                self.assertIsNone(self.result(text))

    def test_composed_text_is_scanned(self):
        row = dict(parent_id='fixture', id='row', split='train', crop_sha256='0'*64, raw_text='1234.')
        self.assertIsNone(automatic_result(row, 'numerics', {}, '0.2', 'd'*64, observed_text='1.234'))


if __name__ == '__main__':
    unittest.main()
