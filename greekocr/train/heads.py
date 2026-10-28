"""P1 recognizer head arms — A (precomposed) and C (two-head) — per docs/architecture/04 §4.4.

The three pre-registered arms share the ENCODER (SVTRv2CTC.encode) and the training data; only the
head + label codec differ. This module adds arms A and C; arm B (nfd-sequential) is the default
single-head SVTRv2CTC in model.py and needs nothing here.

  A — precomposed baseline. One flat CTC softmax over a PRECOMPOSED vocabulary (v4/v5-style charset,
      extended): NFC-composed classes where a precomposed codepoint exists, falling back to the bare
      base/mark atoms where it does not. The precomposed codec is DERIVED DETERMINISTICALLY from the
      NFD codec (no corpus): a codepoint is a class iff it is NFC-stable AND its NFD decomposes wholly
      into codec atoms. So arm A's vocab ⊇ arm B's atoms, replacing common base+mark runs with single
      classes and keeping the marks for the uncomposable tail.

  C — two-head. A per-frame BASE softmax (CTC, with blank) over the 233 non-mark atoms + a per-frame
      MARKS multi-label sigmoid over the 14 combining marks (no blank of its own). Decode: greedy-CTC
      the base head into segments, then for EACH base segment MAX-POOL the marks logits across the
      segment's frames (tolerates spike offset — 04 §4.4), threshold, and emit the base char with its
      marks in NFD-canonical order. Loss = base CTC + λ·BCE(marks); marks are teacher-force-aligned to
      base positions from GT at train time (uniform-proportional aligner for the pilot; a CTC
      forced-alignment upgrade is noted but not required to pick the winner).

Scoring for every arm is the SAME strict-NFD CER (cer.py, D-4a): each arm's decode returns an NFD
string, so the arms are directly comparable. Arm C emits marks in NFD-canonical order by construction,
so it can never produce an equal-ccc swap — GT is stored NFD (canonical), so this costs nothing.

Run `python3 train/heads.py` for the self-check (exit 0 on pass). No data or GPU needed.
"""

from __future__ import annotations

import json
import unicodedata
from dataclasses import dataclass
from typing import Dict, List, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

from greekocr.train.cer import Codec, collapse_ctc, load_codec  # noqa: F401 (load_codec used by callers)
from greekocr.train.model import ENC_DIM, SVTRv2CTC

# S15e(d) — FROZEN P1 arm-C hyperparameters (pinned in docs/prereg_t1.md Changelog 2026-07-08,
# pre-results). Not tuned per result: λ = marks-BCE weight in two_head_loss; thresh = marks sigmoid
# decision threshold in decode_two_head.
ARM_C_LAMBDA = 0.5
ARM_C_THRESH = 0.5

# ---------------------------------------------------------------------------
# Arm C — split the NFD codec into a base head (CTC) + a marks head (sigmoid)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TwoHeadCodec:
    """Derived from a Codec: the base/marks factorization arm C trains against."""

    base_ch_by_id: Tuple[str, ...]  # base head id (0=blank) -> ch ; index 0 = ""
    mark_ch_by_index: Tuple[str, ...]  # marks head index (0..n_marks-1) -> ch
    base_id_of_nfd: Dict[int, int]  # nfd atom id -> base head id (1..n_base-1)
    mark_index_of_nfd: Dict[int, int]  # nfd mark atom id -> marks head index
    n_base: int  # base head class count, INCLUDING blank (id 0)
    n_marks: int  # marks head class count (no blank)


def build_two_head_codec(codec: Codec) -> TwoHeadCodec:
    """Factorize the NFD codec by atom `kind`: kind=='mark' -> marks head, else -> base head."""
    base_atoms = [a for a in codec.atoms if a["kind"] != "mark"]
    mark_atoms = [a for a in codec.atoms if a["kind"] == "mark"]
    if not base_atoms or not mark_atoms:
        raise ValueError("two-head codec needs both base and mark atoms")

    base_ch_by_id: List[str] = [""]  # id 0 = base-CTC blank
    base_id_of_nfd: Dict[int, int] = {}
    for a in base_atoms:
        base_id_of_nfd[a["id"]] = len(base_ch_by_id)
        base_ch_by_id.append(codec.atom_by_id[a["id"]])

    mark_ch_by_index: List[str] = []
    mark_index_of_nfd: Dict[int, int] = {}
    for a in mark_atoms:
        mark_index_of_nfd[a["id"]] = len(mark_ch_by_index)
        mark_ch_by_index.append(codec.atom_by_id[a["id"]])

    return TwoHeadCodec(
        base_ch_by_id=tuple(base_ch_by_id),
        mark_ch_by_index=tuple(mark_ch_by_index),
        base_id_of_nfd=base_id_of_nfd,
        mark_index_of_nfd=mark_index_of_nfd,
        n_base=len(base_ch_by_id),
        n_marks=len(mark_ch_by_index),
    )


def nfd_ids_to_base_marks(nfd_ids, th: TwoHeadCodec) -> Tuple[List[int], List[List[float]]]:
    """Teacher-forced factorization of an NFD label id sequence into arm-C targets.

    Walk the NFD atoms: each BASE atom opens a new base position; each following MARK atom sets a bit
    in the current position's multi-hot mark vector. Returns (base_ids, marks_multihot) where
    base_ids are base-head ids (1..n_base-1) and marks_multihot[i] is an n_marks vector for base i.
    A leading mark with no base (never valid in stored NFD) is dropped, accounted by the caller.
    """
    base_ids: List[int] = []
    marks: List[List[float]] = []
    for i in nfd_ids:
        i = int(i)
        if i in th.base_id_of_nfd:
            base_ids.append(th.base_id_of_nfd[i])
            marks.append([0.0] * th.n_marks)
        elif i in th.mark_index_of_nfd:
            if marks:  # attach to the current base position
                marks[-1][th.mark_index_of_nfd[i]] = 1.0
            # else: orphan mark, dropped (invalid NFD) — caller may count it
        else:
            raise ValueError(f"nfd id {i} is neither base nor mark in this codec")
    return base_ids, marks


# ---------------------------------------------------------------------------
# Arm A — derive a precomposed codec (NFC) deterministically from the NFD codec
# ---------------------------------------------------------------------------

# Covers Basic Latin, Latin-1/Extended, Greek + Greek Extended, Cyrillic, common punctuation/symbols
# — every script our codec touches. Any NFC-stable codepoint whose canonical NFD decomposes wholly
# into codec atoms becomes a precomposed class (this is corpus-free and fully deterministic).
_PRECOMP_SCAN_HI = 0x2C00


def derive_precomposed_atoms(codec: Codec) -> List[dict]:
    """Precomposed vocabulary for arm A, as a list of atom dicts ordered by codepoint.

    A codepoint ch is a class iff NFC(ch)==ch (it is a valid NFC output — base, mark, or precomposed)
    AND every codepoint of NFD(ch) is a codec atom (the codec can express it). This yields: all base
    atoms, all mark atoms (fallback for uncomposable runs), and every precomposed form whose full NFD
    is codec-expressible (e.g. ά, ἅ, ΐ, ё).
    """
    atom_set = set(codec.atom_by_id[1:])  # all NFD atoms (base + mark), skip blank ""
    chosen: List[str] = []
    for cp in range(0x20, _PRECOMP_SCAN_HI):
        ch = chr(cp)
        if unicodedata.normalize("NFC", ch) != ch:
            continue  # not an NFC output (would recompose) — never emitted by NFC(label)
        nfd = unicodedata.normalize("NFD", ch)
        if all(c in atom_set for c in nfd):
            chosen.append(ch)
    chosen.sort(key=ord)  # deterministic id assignment by codepoint
    atoms = []
    for k, ch in enumerate(chosen, start=1):
        atoms.append({"id": k, "cp": f"U+{ord(ch):04X}", "ch": ch, "kind": "precomposed"})
    return atoms


def build_precomposed_codec_json(codec: Codec, src_version: str) -> dict:
    """Assemble the arm-A precomposed codec object (NFC form). Caller writes it to disk."""
    atoms = derive_precomposed_atoms(codec)
    return {
        "version": f"precomposed_{src_version}",
        "blank_id": 0,
        "form": "NFC",
        "policy": {
            "derivation": "NFC-stable codepoints whose canonical NFD decomposes wholly into "
            f"codec {src_version} atoms; arm A of docs/architecture/04 §4.4",
            "normalization": "NFC (labels re-encoded from NFD via NFC for this arm only)",
            "scoring": "decode -> NFD -> strict CER (cer.py, D-4a); comparable to arms B/C",
        },
        "atoms": atoms,
    }


def build_precomposed_index(prec_codec: Codec) -> Dict[str, int]:
    """ch -> precomposed atom id, for encoding NFC labels."""
    return {prec_codec.atom_by_id[a["id"]]: a["id"] for a in prec_codec.atoms}


def nfd_ids_to_precomposed_ids(nfd_ids, codec: Codec, prec_index: Dict[str, int]) -> List[int]:
    """Arm-A label transcode: NFD atom ids -> NFC string -> precomposed atom ids."""
    nfd_str = codec.decode([int(i) for i in nfd_ids])
    nfc_str = unicodedata.normalize("NFC", nfd_str)
    out: List[int] = []
    for ch in nfc_str:
        if ch not in prec_index:
            raise ValueError(f"char U+{ord(ch):04X} {ch!r} missing from precomposed codec")
        out.append(prec_index[ch])
    return out


# ---------------------------------------------------------------------------
# Head modules (share the compact encoder via encode())
# ---------------------------------------------------------------------------


class PrecomposedRecognizer(nn.Module):
    """Arm A: shared encoder + one flat CTC softmax over the precomposed vocab."""

    def __init__(self, n_prec_classes: int) -> None:
        super().__init__()
        self.encoder = SVTRv2CTC(2, with_head=False)  # headless compact encoder
        self.head = nn.Linear(ENC_DIM, n_prec_classes)
        self.n_classes = n_prec_classes

    def forward(self, x: torch.Tensor, input_lengths=None) -> torch.Tensor:
        # WP-A: thread input_lengths so encode() masks each strip's own right-pad in attention.
        return F.log_softmax(self.head(self.encoder.encode(x, input_lengths)), dim=-1)  # [B, T, n_prec]


class TwoHeadRecognizer(nn.Module):
    """Arm C: shared encoder + base CTC head + marks multi-label sigmoid head."""

    def __init__(self, n_base: int, n_marks: int) -> None:
        super().__init__()
        self.encoder = SVTRv2CTC(2, with_head=False)
        self.base_head = nn.Linear(ENC_DIM, n_base)  # incl. CTC blank
        self.marks_head = nn.Linear(ENC_DIM, n_marks)  # sigmoid, no blank
        self.n_base = n_base
        self.n_marks = n_marks

    def forward(self, x: torch.Tensor, input_lengths=None):
        feats = self.encoder.encode(x, input_lengths)  # [B, T, 256]  (WP-A: pad-frame masking)
        base_logprobs = F.log_softmax(self.base_head(feats), dim=-1)  # [B, T, n_base]
        marks_logits = self.marks_head(feats)  # [B, T, n_marks] (raw; sigmoid at loss/decode)
        return base_logprobs, marks_logits


# ---------------------------------------------------------------------------
# Arm dispatch
# ---------------------------------------------------------------------------

HEAD_CHOICES = ("nfd", "precomposed", "two")  # B, A, C of docs/architecture/04 §4.4


def build_arm(
    head: str,
    arch: str,
    codec: Codec,
    prec_codec_path: str = None,
    verbose: bool = True,
    width_mult: float = 1.0,
) -> nn.Module:
    """Dispatch a recognizer for a P1 head arm.

    nfd (B)         -> the incumbent single-head SVTRv2CTC over the NFD codec (any arch).
    precomposed (A) -> compact encoder + flat CTC head over the precomposed codec.
    two (C)         -> compact encoder + base CTC head + marks sigmoid head.

    Arms A/C fix the encoder to `compact` (P1 varies only the head, 04 §4.4).
    """
    if width_mult != 1.0 and (head != "nfd" or arch != "compact"):
        raise ValueError("width_mult requires compact with the NFD CTC head")
    if head == "nfd":
        from greekocr.train.model import build_model

        m, _ = build_model(n_classes=codec.n_classes, arch=arch, verbose=verbose, width_mult=width_mult)
        return m
    if arch != "compact":
        raise ValueError(f"arm {head!r} uses the compact encoder only (P1 fixes it); got arch={arch!r}")
    if head == "precomposed":
        path = prec_codec_path or f"codec/precomposed_{codec.version}.json"
        prec = load_codec(path)
        m = PrecomposedRecognizer(prec.n_classes)
        if verbose:
            n = sum(p.numel() for p in m.parameters())
            print(f"[model] arm=precomposed: n_classes={prec.n_classes}, params={n:,} ({n / 1e6:.2f}M)")
        return m
    if head == "two":
        th = build_two_head_codec(codec)
        m = TwoHeadRecognizer(th.n_base, th.n_marks)
        if verbose:
            n = sum(p.numel() for p in m.parameters())
            print(f"[model] arm=two: base={th.n_base}, marks={th.n_marks}, params={n:,} ({n / 1e6:.2f}M)")
        return m
    raise ValueError(f"unknown head {head!r}; choices: {', '.join(HEAD_CHOICES)}")


# ---------------------------------------------------------------------------
# Decode (per line -> NFD string, for strict CER)
# ---------------------------------------------------------------------------


def decode_precomposed(logprobs: torch.Tensor, prec_codec: Codec) -> str:
    """Arm A: greedy CTC over the precomposed head for ONE line [T, n_prec] -> NFD string."""
    ids = logprobs.argmax(dim=-1).tolist()
    prec_str = prec_codec.decode(collapse_ctc(ids, blank=prec_codec.blank_id))
    return unicodedata.normalize("NFD", prec_str)


# Canonical Greek mark order for emission (04 §4.3): NFD stable-sorts by ccc but keeps SOURCE order
# within equal ccc, so the decoder — not NFD — must place breathing/dialytika BEFORE the accent (the
# order Unicode's Greek Extended decompositions use, e.g. NFD(ἅ)=α+0314+0301). ypogegrammeni (ccc=240)
# and cedilla (ccc=202) fall in the right place by ccc alone.
_ABOVE_FIRST = {0x0313, 0x0314, 0x0308}  # psili, dasia, dialytika: canonical-first among ccc=230 marks


def _mark_sort_key(ch: str):
    cp = ord(ch)
    return (unicodedata.combining(ch), 0 if cp in _ABOVE_FIRST else 1, cp)


def _base_segments(base_ids: List[int], blank: int = 0) -> List[Tuple[int, List[int]]]:
    """Greedy-CTC segmentation with frame spans: (class_id, [frame indices]) per emitted base char."""
    segs: List[Tuple[int, List[int]]] = []
    prev = blank
    for t, c in enumerate(base_ids):
        c = int(c)
        if c == blank:
            prev = blank
            continue
        if c != prev:
            segs.append((c, [t]))
        else:
            segs[-1][1].append(t)
        prev = c
    return segs


def decode_two_head(
    base_logprobs: torch.Tensor,
    marks_logits: torch.Tensor,
    th: TwoHeadCodec,
    thresh: float = ARM_C_THRESH,
) -> str:
    """Arm C decode for ONE line: base_logprobs [T, n_base], marks_logits [T, n_marks] -> NFD string.

    For each base segment, MAX-POOL the marks logits across its frames (04 §4.4 — tolerates spike
    offset), sigmoid, threshold, and emit the base char + its marks in NFD-canonical order.
    """
    base_ids = base_logprobs.argmax(dim=-1).tolist()
    marks_prob = torch.sigmoid(marks_logits)  # [T, n_marks]
    pieces: List[str] = []
    for cls, frames in _base_segments(base_ids, blank=0):
        base_ch = th.base_ch_by_id[cls]
        seg = marks_prob[frames]  # [len(frames), n_marks]
        pooled = seg.max(dim=0).values  # max-pool over the segment's frames
        marks = [th.mark_ch_by_index[i] for i in range(th.n_marks) if float(pooled[i]) > thresh]
        marks.sort(key=_mark_sort_key)  # canonical Greek order; NFD won't reorder equal-ccc marks
        pieces.append(unicodedata.normalize("NFD", base_ch + "".join(marks)))
    return "".join(pieces)


# ---------------------------------------------------------------------------
# Loss
# ---------------------------------------------------------------------------


def _uniform_align_marks(marks_targets: List[List[float]], t_frames: int, n_marks: int) -> torch.Tensor:
    """Teacher-forced (uniform-proportional) per-frame mark targets for one line -> [T, n_marks].

    Spread the base positions evenly over the T frames and broadcast each position's mark multi-hot
    across its frame span. Crude but a legitimate teacher-forced aligner for the pilot; a CTC
    forced-alignment upgrade is a training refinement, not needed to pick the winning arm.
    """
    tgt = torch.zeros(t_frames, n_marks)
    n = len(marks_targets)
    if n == 0:
        return tgt
    for f in range(t_frames):
        pos = min(n - 1, (f * n) // t_frames)
        tgt[f] = torch.tensor(marks_targets[pos])
    return tgt


def two_head_loss(
    base_logprobs: torch.Tensor,  # [B, T, n_base] log-softmax
    marks_logits: torch.Tensor,  # [B, T, n_marks] raw
    base_targets: List[List[int]],  # per-sample base head ids
    marks_targets: List[List[List[float]]],  # per-sample [pos][n_marks] multi-hot
    input_lengths: torch.Tensor,  # [B] valid frame counts
    lam: float = ARM_C_LAMBDA,
    blank: int = 0,
) -> torch.Tensor:
    """Arm-C training loss: base CTC + λ·BCE(marks) with uniform teacher-forced mark alignment."""
    b, t, n_base = base_logprobs.shape
    n_marks = marks_logits.shape[-1]
    # base CTC (expects [T, B, C])
    tgt_flat = torch.tensor([i for seq in base_targets for i in seq], dtype=torch.long)
    tgt_lens = torch.tensor([len(seq) for seq in base_targets], dtype=torch.long)
    ctc = F.ctc_loss(
        base_logprobs.transpose(0, 1),
        tgt_flat,
        input_lengths.to(torch.long),
        tgt_lens,
        blank=blank,
        zero_infinity=True,
    )
    # marks BCE — MASKED to valid (non-padding) frames [S15e(d)]. Previously the aligner spread over
    # ALL t frames and the mean included padding, so the marks head was supervised with noise on the
    # padded tail — a penalty hitting ONLY the novel arm C (arm B's CTC already ignores padding via
    # input_lengths). Spread each line's targets over its VALID length and average over valid frames.
    aligned = torch.zeros(b, t, n_marks, device=marks_logits.device)
    fmask = torch.zeros(b, t, 1, device=marks_logits.device)
    for k in range(b):
        length = int(input_lengths[k])
        fmask[k, :length] = 1.0
        aligned[k, :length] = _uniform_align_marks(marks_targets[k], length, n_marks).to(marks_logits.device)
    bce_map = F.binary_cross_entropy_with_logits(marks_logits, aligned, reduction="none")  # [B,T,n_marks]
    bce = (bce_map * fmask).sum() / (fmask.sum() * n_marks).clamp(min=1.0)
    return ctc + lam * bce


# ---------------------------------------------------------------------------
# Self-check (build + shapes + encode/decode round-trips; no data, no GPU)
# ---------------------------------------------------------------------------


def _tiny_nfd_codec() -> Codec:
    """A minimal on-disk-free NFD codec: space, α, ι, dialytika, oxia, dasia — enough to exercise
    base/mark split, precomposed derivation (ΐ, ά, ἅ), and two-head alignment."""
    import os
    import tempfile

    atoms = [
        {"id": 1, "cp": "U+0020", "ch": " ", "kind": "space", "script": "zyyy"},
        {"id": 2, "cp": "U+03B1", "ch": "α", "kind": "base", "script": "grek"},  # α
        {"id": 3, "cp": "U+03B9", "ch": "ι", "kind": "base", "script": "grek"},  # ι
        {"id": 4, "cp": "U+0308", "ch": "̈", "kind": "mark", "script": "zinh"},  # dialytika
        {"id": 5, "cp": "U+0301", "ch": "́", "kind": "mark", "script": "zinh"},  # oxia
        {"id": 6, "cp": "U+0314", "ch": "̔", "kind": "mark", "script": "zinh"},  # dasia
    ]
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump({"version": "vtiny", "blank_id": 0, "atoms": atoms}, f)
        tmp = f.name
    try:
        return load_codec(tmp)
    finally:
        os.unlink(tmp)


def _selfcheck() -> None:
    torch.manual_seed(0)
    codec = _tiny_nfd_codec()
    a, i, dia, oxia, dasia = "α", "ι", "̈", "́", "̔"

    # --- arm C codec split ---
    th = build_two_head_codec(codec)
    assert th.n_base == 4 and th.n_marks == 3, (th.n_base, th.n_marks)  # blank+space+α+ι ; 3 marks
    # α + dasia + oxia  ->  base=[α], marks={dasia,oxia}
    nfd_ids = [2, 6, 5]  # α, dasia, oxia
    base_ids, marks = nfd_ids_to_base_marks(nfd_ids, th)
    assert th.base_ch_by_id[base_ids[0]] == a and len(base_ids) == 1
    on = {th.mark_ch_by_index[k] for k in range(th.n_marks) if marks[0][k] > 0.5}
    assert on == {dasia, oxia}, on

    # --- arm A precomposed derivation ---
    prec_obj = build_precomposed_codec_json(codec, "vtiny")
    chs = {atm["ch"] for atm in prec_obj["atoms"]}
    # base + marks fall through; precomposed forms whose NFD is codec-expressible appear as single classes
    assert a in chs and dia in chs and oxia in chs  # bases/marks retained
    assert "ά" in chs  # ά = NFC(α+oxia)
    assert "ἅ" in chs  # ἅ = NFC(α+dasia+oxia)
    assert "ϊ" in chs  # ϊ = NFC(ι+dialytika)
    assert "ΐ" in chs  # ΐ = NFC(ι+dialytika+oxia)
    import os
    import tempfile

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(prec_obj, f, ensure_ascii=False)
        prec_path = f.name
    try:
        prec_codec = load_codec(prec_path)
    finally:
        os.unlink(prec_path)
    prec_index = build_precomposed_index(prec_codec)
    # transcode α+dasia+oxia -> single precomposed ἅ, then decode back through NFD == original NFD
    pids = nfd_ids_to_precomposed_ids(nfd_ids, codec, prec_index)
    assert len(pids) == 1, pids  # composed to one class
    assert decode_precomposed_ids_roundtrip(pids, prec_codec) == codec.decode(nfd_ids)

    # --- head modules build + forward shapes (T == ceil(W/4)) ---
    W = 64
    x = torch.zeros(1, 1, 48, W)
    armA = PrecomposedRecognizer(prec_codec.n_classes)
    outA = armA(x)
    assert outA.shape == (1, W // 4, prec_codec.n_classes), outA.shape
    armC = TwoHeadRecognizer(th.n_base, th.n_marks)
    baseLP, markLG = armC(x)
    assert baseLP.shape == (1, W // 4, th.n_base) and markLG.shape == (1, W // 4, th.n_marks)

    # --- arm A decode: hand-built argmax path over the precomposed head ---
    T = 8
    lp = torch.full((T, prec_codec.n_classes), -20.0)
    a_id = prec_index[a]
    ha_id = prec_index["ἅ"]  # ἅ
    for t in range(T):
        lp[t, prec_codec.blank_id] = 0.0
    lp[1, prec_codec.blank_id] = -20.0
    lp[1, a_id] = 0.0  # emit α
    lp[4, prec_codec.blank_id] = -20.0
    lp[4, ha_id] = 0.0  # emit ἅ
    dec = decode_precomposed(lp, prec_codec)
    assert dec == a + unicodedata.normalize("NFD", "ἅ"), repr(dec)

    # --- arm C decode: base segment α over frames 2..3, marks dasia+oxia pooled ---
    T = 6
    baseLP2 = torch.full((T, th.n_base), -20.0)
    for t in range(T):
        baseLP2[t, 0] = 0.0  # blank
    a_base = th.base_id_of_nfd[2]
    baseLP2[2, 0] = -20.0
    baseLP2[2, a_base] = 0.0
    baseLP2[3, 0] = -20.0
    baseLP2[3, a_base] = 0.0  # one α over two frames (no blank between)
    markLG2 = torch.full((T, th.n_marks), -20.0)
    di_dasia = th.mark_index_of_nfd[6]
    di_oxia = th.mark_index_of_nfd[5]
    markLG2[3, di_dasia] = 20.0  # marks fire on frame 3 (spike offset from base peak) -> pooled
    markLG2[2, di_oxia] = 20.0
    decC = decode_two_head(baseLP2, markLG2, th)
    assert decC == unicodedata.normalize("NFD", "ἅ"), repr(decC)  # ἅ in NFD

    # --- arm C loss finite + differentiable on a tiny batch ---
    x2 = torch.zeros(2, 1, 48, 64, requires_grad=False)
    baseLP3, markLG3 = armC(x2)
    bt = [[a_base], [a_base]]
    mt = [[[0.0] * th.n_marks], [[0.0] * th.n_marks]]
    mt[0][0][di_oxia] = 1.0
    il = torch.tensor([16, 16])
    loss = two_head_loss(baseLP3, markLG3, bt, mt, il, lam=0.5)
    assert torch.isfinite(loss), loss
    loss.backward()  # gradients flow through both heads + encoder

    print(
        f"heads.py selfcheck PASS — armA(precomposed n={prec_codec.n_classes}) "
        f"armC(base={th.n_base}, marks={th.n_marks}); build/forward/decode/loss OK"
    )


def decode_precomposed_ids_roundtrip(pids: List[int], prec_codec: Codec) -> str:
    """Helper (test): precomposed ids -> NFD string, without a CTC path."""
    return unicodedata.normalize("NFD", prec_codec.decode(pids))


if __name__ == "__main__":
    _selfcheck()
