"""Turn Q1 joined records into recognizer crops without slicing recognized text."""
from __future__ import annotations

import copy

import numpy as np

from .lines import CURVES
from .tables import TextPiece, line_piece


def joined_text_pieces(result) -> list[TextPiece]:
    pieces = []
    for record in result.delivery:
        row = next(r for r in result.rows if r['id'] == record['row_id'])
        index = next(i for i in row['line_indices'] if result.lines[i]['piece_index'] == record['piece_index'])
        line = copy.copy(result.segmentation.lines[index])
        line.x0, line.x1, line.xheight = record['x0'], record['x1'], record['xheight']
        for name in CURVES:
            setattr(line, name, np.asarray(record[name]))
        piece = line_piece(line, index, result.image_size)
        piece.table_id = row['table_id']
        pieces.append(piece)
    return pieces
