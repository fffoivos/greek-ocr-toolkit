"""Frozen serialization/evidence vocabulary. Provenance is stored outside this record."""
import hashlib
import json

EVIDENCE_SCHEMA = 'ctc-window-score-v1'
LINE_PROVENANCE = 'saved_alignment_confidence'
REGION_PROVENANCE = 'minimum_max_frame_posterior_including_blank'
RECORD_KEYS = frozenset(('prediction', 'n_frames', 'scale', 'strip_width', 'confidence', 'spans'))
OPTIONAL_RECORD_KEYS = frozenset(('frame_confidences', 'frame_prediction_sha256', 'transferred'))


def alignment_sha256(alignment):
    return hashlib.sha256(json.dumps(alignment.to_record(), sort_keys=True).encode()).hexdigest()
