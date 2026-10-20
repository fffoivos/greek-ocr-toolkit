# T6b masked-card checks (17 Oct 2026)

**Setup.** 100 uniform seeded cards per source (seed `t6b:<source>`), drawn over masked rows plus guarded rows (the guarded ones as their byte-exact originals). LABEL_CHECK_v2 is unchanged. Two Opus readers per source, one source at a time. Gate (coordinator): letters ≥90 and crop_ok ≥90 on the same 100 masked cards. A pass admits masked rows to the wave-1d arm only.

| source | letters y | crop_ok y | marks y / applicable | C1 crop_ok on the original crops | gate |
|---|---|---|---|---|---|
| gazette_modern | 97 | 96 | 71/72 | 70 (probe) / 82 (measured) | pass |
| kosmopolis | 98 | 97 | 85/94 | 53 | pass |
| lekythos | 98 | 96 | 87/99 | 57 | pass |

**Gazette by class.**
- The 100 cards are modern_scanned 64 (letters 61, crop 62), numerics_tables 28, dialogue 7 and latin 1.
- 14 numerics cards are vertical digit cells stored rotated. They led to the widened rotated_crop rule (h>w and ≥4 non-space characters; 1,681 W1 rows; sol/collect-v3 0a2f0452). Gazette numerics stay unchecked.
- Measured 1986–1990 modern_scanned: 51/54 letters, 53/54 crop_ok.

**Probe 1982–1985 supplement.** 30 more uniform cards (seed `t6b:gazette_modern:probe`; modern_scanned probe rows; excludes the 100 cards and rotated_crop; pool 1,542):
- the supplement alone: letters 25/30, crop_ok 26/30;
- combined with the 10 probe modern_scanned cards above, n=40: letters 35/40, crop_ok 35/40 → **fail**.
- Failures: line-end hyphens dropped from the label (3) and multi-line or skewed crops (3). W2 Gazette reads measured_1986_1990 only.

**Blinding.**
- The gazette and kosmopolis checks: KEY-IN-REACH (not opened). The crops symlink led into cards/<source>/crops, with <source>_key.json one level above.
- The lekythos and probe checks used copied crops, with the key out of reach.

Verdicts are in `verdicts/` and aggregates in `t6b_results.json`.
