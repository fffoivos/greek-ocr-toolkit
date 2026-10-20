# Lead pixel review of the planted controls (17 Oct 2026, 12:41 Athens)

The Opus lead (Sol-reading track) checked the SR-B1 contact sheets by eye.

## bsb, 10 controls: all valid
Each planted edit differs from the printed ink:

| Control | Printed | Planted |
|---|---|---|
| k61655a3133 | μορφὰς | μορπὰς |
| k516e6e3d8a | δυστυχοῦς | δπστυχοῦς |
| kc6e381393b | ἀποστρέφομαι | ἀλοστρέφομαι |
| kc26bee9ff1 | στιγμῆς | στιπμῆς |
| kbe9db70958 | ἔξωθεν | ἔξωπεν |
| k33afe3d843 | κρίσεις | κρισεις |
| kcd9dc6b69c | θέλομεν | θελομεν |
| kdf400ce002 | Φιλαρέτου | Φιλαρετου |
| kc25d024c94 | ἤρξατο | ἠρξατο |
| k30ef2c58bb | χρειασθῇ | χρειασθῃ |

So letters=n holds for the 5 letter controls and marks=n for the 5 mark controls.

## yer, 5 controls: 4 valid as built, 1 re-keyed from the ink
- k3f7529f98f другихъ: ъ, flag clear.
- k3f58438b50 яхъ, морскихъ: ъ ъ.
- kb7face236c называетъ, родимымъ: ъ ъ.
- kc8a4ce55a6 скрутить, дать: ь ь, no flag.
- **k15896cc479 (supplement s003): mis-keyed by the build.**
  - The ink reads Король, Государь (ь), then однакожъ, думаетъ, онъ, with clear left flags.
  - Google wrote ь in all five places.
  - Expected becomes {"1":"ь","2":"ь","3":"ъ","4":"ъ","5":"ъ"}. This is ink truth from this review.
  - The item is kept as a mixed control. The "modern orthography" filter let it in only because Google's own ъ→ь error hid the hard signs.

Only 5 yer controls exist (5/64 = 7.8%), because only two eligible soft-sign lines exist outside the bed (SR-B1 receipt).

## owner39, 4 controls: forms valid, options must be rebuilt
The pixels agree with every expected form and head:
- αυτής: no breathing, no accent on α, so literal;
- που: none;
- τη: none;
- στάδιο: acute on α, no breathing.

**Blinding defect.** These T2 controls carry 3 breathing-varied options. All 39 bed cards carry 4 accent-varied options, so a reader could spot the controls. SR-B1b regenerates the control options with the bed's own option generator. Expected forms and heads stay; the expected choice follows from the new options.
