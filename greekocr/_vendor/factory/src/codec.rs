//! Codec v1 — versioned NFD atom inventory (docs/data_contracts.md §1).
//! GT is NFD; rendering uses NFC. Encoding rejects lines with unmapped codepoints.

use serde::Serialize;
use std::collections::HashMap;
use unicode_normalization::UnicodeNormalization;

pub const CODEC_VERSION: &str = "v1";

#[derive(Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "lowercase")]
pub enum Kind {
    Base,
    Mark,
    Digit,
    Punct,
    Space,
    Sym,
}

#[derive(Serialize)]
pub struct Atom {
    pub id: u32,
    pub cp: String,
    pub ch: char,
    pub kind: Kind,
    pub script: &'static str,
}

pub struct Codec {
    pub atoms: Vec<Atom>,
    map: HashMap<char, u32>,
}

const GREEK_BASES: &str = "ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρςστυφχψωϜϝϘϙϠϡϚϛ";
// ß/œ/æ have NO canonical decomposition — they are atoms (needed for de/fr).
const LATIN_BASES: &str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzßœŒæÆ";
// NFD-atomic Cyrillic for ru/uk (ё й ї decompose to base+mark and are NOT atoms).
const CYRILLIC_BASES: &str = "АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдежзиклмнопрстуфхцчшщъыьэюяІіЇЄєҐґ";
// Combining marks (contract list). ccc: 230 for the stack marks, 240 for ypogegrammeni, 202 cedilla.
const MARKS: &[char] = &[
    '\u{0300}', '\u{0301}', '\u{0302}', '\u{0303}', '\u{0304}', '\u{0306}', '\u{0308}',
    '\u{030A}', '\u{030C}', '\u{0313}', '\u{0314}', '\u{0327}', '\u{0342}', '\u{0345}',
];
// NOTE: U+037E (Greek question mark) canonically decomposes to ';' and U+0387 (ano teleia)
// to U+00B7 — after NFD only ';' and '·' exist, so those are the atoms.
// U+02B9 modifier prime (NFD of U+0374 keraia) + U+0375 lower numeral sign, explicit to avoid
// lookalike-literal ambiguity.
const PUNCT: &str = ".,;:·!?¿¡'\"«»()[]-–—…’‘“”\u{02B9}\u{0375}";
// G0-3 (owner decision 2026-07-07): € £ added as atoms (real modern-text currency; 13k/0.6k lines).
// $ and • deliberately NOT added — they are LaTeX-math / list-bullet residue handled by filters.
const SYMS: &str = "%&*§†‡°+=/€£";

impl Codec {
    pub fn v1() -> Codec {
        let mut atoms: Vec<(char, Kind, &'static str)> = Vec::new();
        for c in GREEK_BASES.chars() {
            atoms.push((c, Kind::Base, "grek"));
        }
        for c in LATIN_BASES.chars() {
            atoms.push((c, Kind::Base, "latn"));
        }
        for c in CYRILLIC_BASES.chars() {
            atoms.push((c, Kind::Base, "cyrl"));
        }
        for &c in MARKS {
            atoms.push((c, Kind::Mark, "zinh"));
        }
        for c in "0123456789".chars() {
            atoms.push((c, Kind::Digit, "zyyy"));
        }
        for c in PUNCT.chars() {
            atoms.push((c, Kind::Punct, "zyyy"));
        }
        for c in SYMS.chars() {
            atoms.push((c, Kind::Sym, "zyyy"));
        }
        // ids: 0 = blank (reserved, not an atom row), 1 = space, then (kind, codepoint) sorted.
        let kind_rank = |k: Kind| match k {
            Kind::Base => 0u8,
            Kind::Mark => 1,
            Kind::Digit => 2,
            Kind::Punct => 3,
            Kind::Sym => 4,
            Kind::Space => 5,
        };
        atoms.sort_by_key(|(c, k, _)| (kind_rank(*k), *c as u32));
        atoms.dedup_by_key(|(c, _, _)| *c);
        let mut out = Vec::with_capacity(atoms.len() + 1);
        out.push(Atom { id: 1, cp: "U+0020".into(), ch: ' ', kind: Kind::Space, script: "zyyy" });
        for (i, (c, k, s)) in atoms.iter().enumerate() {
            out.push(Atom {
                id: (i + 2) as u32,
                cp: format!("U+{:04X}", *c as u32),
                ch: *c,
                kind: *k,
                script: s,
            });
        }
        let map = out.iter().map(|a| (a.ch, a.id)).collect();
        Codec { atoms: out, map }
    }

    pub fn n_classes(&self) -> usize {
        self.atoms.len() + 1 // + blank(0)
    }

    /// Canonical GT form: NFD with whitespace runs collapsed to single U+0020.
    pub fn normalize_gt(text: &str) -> String {
        let mut out = String::with_capacity(text.len());
        let mut prev_space = true; // also trims leading
        for c in text.nfd() {
            // G0-3 (owner 2026-07-07): fold Greek confusables to their canonical codec atom and drop
            // STANDALONE spacing breathings/tonos (they modify no base). Recovers ~390k polytonic lines
            // (ʼ elision 246k, ϲ lunate-sigma 40k, koronis 102k, psili 57k) instead of rejecting them.
            let c = match c {
                '\u{02BC}' | '\u{1FBD}' | '\u{1FBF}' => '\u{0027}', // modifier-apostrophe / koronis / psili -> '
                '\u{03F2}' => '\u{03C3}',                          // Greek lunate sigma -> σ
                '\u{1FFE}' | '\u{0384}' => continue,               // spacing dasia / spacing tonos -> drop
                other => other,
            };
            if c.is_whitespace() {
                if !prev_space {
                    out.push(' ');
                    prev_space = true;
                }
            } else {
                out.push(c);
                prev_space = false;
            }
        }
        while out.ends_with(' ') {
            out.pop();
        }
        out
    }

    /// Encode an ALREADY-normalized GT string. None if any codepoint is unmapped.
    pub fn encode(&self, gt_nfd: &str) -> Option<Vec<u32>> {
        gt_nfd.chars().map(|c| self.map.get(&c).copied()).collect()
    }

    pub fn is_mark(c: char) -> bool {
        MARKS.contains(&c)
    }

    /// Marks that stack ABOVE the base (used by the accent-survival top-band probe).
    pub fn is_top_mark(c: char) -> bool {
        matches!(c, '\u{0300}' | '\u{0301}' | '\u{0302}' | '\u{0303}' | '\u{0304}' | '\u{0306}'
            | '\u{0308}' | '\u{030A}' | '\u{030C}' | '\u{0313}' | '\u{0314}' | '\u{0342}')
    }

    /// Marks that hang BELOW the baseline: ypogegrammeni (U+0345, ccc 240) + cedilla (U+0327, ccc 202).
    /// Used by the bottom-band survival probe + detector-crop bottom-cut bound (repair).
    pub fn is_bottom_mark(c: char) -> bool {
        matches!(c, '\u{0345}' | '\u{0327}')
    }

    /// Render form: NFC (fonts carry precomposed glyphs).
    pub fn render_form(gt_nfd: &str) -> String {
        gt_nfd.nfc().collect()
    }

    pub fn emit_json(&self) -> String {
        #[derive(Serialize)]
        struct Out<'a> {
            version: &'a str,
            blank_id: u32,
            policy: serde_json::Value,
            atoms: &'a [Atom],
        }
        serde_json::to_string_pretty(&Out {
            version: CODEC_VERSION,
            blank_id: 0,
            policy: serde_json::json!({
                "normalization": "NFD",
                "whitespace": "runs collapse to U+0020",
                "unknown_codepoint": "reject line at ingest (accounted)",
                "mark_order": "NFD canonical ordering; equal-ccc keeps source order (D-4a strict)",
                "note_decompositions": "U+037E -> ';', U+0387 -> U+00B7, ё/й/ї/ΐ/ΰ etc. -> base+mark",
            }),
            atoms: &self.atoms,
        })
        .expect("codec serializes")
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn polytonic_roundtrip_and_order() {
        let c = Codec::v1();
        // ᾧ = omega + dasia(0314) + perispomeni(0342) + ypogegrammeni(0345) in NFD order
        let gt = Codec::normalize_gt("ᾧ");
        let chars: Vec<char> = gt.chars().collect();
        assert_eq!(chars, vec!['ω', '\u{0314}', '\u{0342}', '\u{0345}']);
        assert!(c.encode(&gt).is_some());
        assert_eq!(Codec::render_form(&gt), "ᾧ");
    }

    #[test]
    fn greek_punct_decompositions() {
        let gt = Codec::normalize_gt("τί\u{037E} καὶ\u{0387}");
        assert!(gt.contains(';'));
        assert!(gt.contains('\u{00B7}'));
        assert!(Codec::v1().encode(&gt).is_some());
    }

    #[test]
    fn g0_3_confusable_folds_and_currency() {
        let c = Codec::v1();
        // ʼ elision + koronis + psili -> ' ; lunate sigma -> σ ; spacing dasia/tonos dropped.
        assert_eq!(Codec::normalize_gt("δ\u{02BC}"), "δ'");
        assert_eq!(Codec::normalize_gt("\u{1FBD}"), "'");
        assert_eq!(Codec::normalize_gt("\u{1FBF}"), "'");
        assert_eq!(Codec::normalize_gt("\u{03F2}"), "σ");
        assert_eq!(Codec::normalize_gt("α\u{1FFE}β"), "αβ"); // spacing dasia dropped
        assert_eq!(Codec::normalize_gt("α\u{0384}β"), "αβ"); // spacing tonos dropped
        for s in ["δ\u{02BC} τ\u{02BC}", "\u{03F2}υνεσις", "10 €", "5 £"] {
            assert!(c.encode(&Codec::normalize_gt(s)).is_some(), "{s} must encode after G0-3");
        }
    }

    #[test]
    fn cyrillic_nfd_atoms() {
        let c = Codec::v1();
        for s in ["ёж", "йод", "її", "Київ"] {
            let gt = Codec::normalize_gt(s);
            assert!(c.encode(&gt).is_some(), "{s} must encode via base+mark");
        }
    }

    #[test]
    fn unknown_rejected() {
        let c = Codec::v1();
        assert!(c.encode(&Codec::normalize_gt("汉字")).is_none());
    }

    #[test]
    fn ids_contiguous() {
        let c = Codec::v1();
        for (i, a) in c.atoms.iter().enumerate() {
            assert_eq!(a.id as usize, i + 1);
        }
    }

    #[test]
    fn codec_lint_no_atom_nfd_decomposes_except_grandfathered_u0407() {
        // S15b (review F2): normalize_gt emits NFD, so any atom whose `ch` canonically decomposes is a
        // DEAD class slot — the decomposed base+mark form is emitted instead and the precomposed atom
        // is never reachable from corpus text. Exactly ONE such atom exists in v1: U+0407 (Ї ->
        // U+0406 І + U+0308 ◌̈), grandfathered (codec frozen + custody-pinned; retire at the next codec
        // version). This test guards every FUTURE codec emission: no NEW decomposable atom may be added.
        let c = Codec::v1();
        let offenders: Vec<(u32, char)> = c
            .atoms
            .iter()
            .filter(|a| {
                let nfd: Vec<char> = a.ch.to_string().nfd().collect();
                nfd.len() != 1 || nfd[0] != a.ch
            })
            .map(|a| (a.id, a.ch))
            .collect();
        assert_eq!(offenders.len(), 1, "unexpected NFD-decomposable (dead) atoms: {offenders:?}");
        assert_eq!(
            offenders[0].1, '\u{0407}',
            "the only grandfathered dead atom must be U+0407 (Ï); retire at next codec version: {offenders:?}"
        );
    }
}
