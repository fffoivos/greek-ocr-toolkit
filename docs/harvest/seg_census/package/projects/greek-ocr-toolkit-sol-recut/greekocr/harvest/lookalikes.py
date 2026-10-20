"""Existing case-sensitive diagnostic groups, shared without character folding.

Extracted unchanged from greekocr/_vendor/bench/e1_readout.py::HOMOGLYPHS.
CENSUS2 R6 used script identities, not these groups; R6 remains unchanged.
"""
import hashlib
import json

HOMOGLYPHS = ('ΑAА', 'ΒBВ', 'ΕEЕ', 'ΖZ', 'ΗHН', 'ΙIІ', 'ΚKК', 'ΜMМ', 'ΝN',
              'ΟOО', 'ΡPР', 'ΤTТ', 'ΥY', 'ΧXХ', 'ϹCС', 'οoо', 'ρpр', 'νv', 'аa', 'сc', 'еe', 'хx', 'іi')
LOOKALIKE_TABLE_NAME = "greekocr.harvest.lookalikes.HOMOGLYPHS"


def lookalike_table_sha256():
    """SHA-256 of ordered groups as compact UTF-8 JSON, no newline."""
    return hashlib.sha256(json.dumps(HOMOGLYPHS, ensure_ascii=False,
                                    separators=(",", ":")).encode()).hexdigest()
