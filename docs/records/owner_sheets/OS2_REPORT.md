# OS2 compatible owner-sheet specs

Offline build from `inputs/coordinator_build_sheets_v2.py`; no publishing, network, database access, or `.git` writes. Replayed current baseline: 133 / 42 cards. The checked baseline specs are retained under `inputs/coordinator_*.json`.

Renderer change: **kept**. Section headings are needed by the coordinator’s 14-class builder. Optional note initialization, intro line breaks, and gap labels are additive. Legacy re-emission tests are unchanged; a new test compares the legacy path and covers these optional features. CSS/JS and the note database identity protocol are unchanged.

T6b pointer: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/build_gallery.py`; verdicts: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/{kosmopolis,lekythos,gazette_modern}__{a,b}.jsonl`; keys and checked masked rasters: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/cards/`. New T6b cards display the masked raster whose SHA-256 matches the key. Existing cards retain the coordinator raster and original group. Evidence and codes from every matching A/B partition are retained per card. The A/B files partition card ids; they are not duplicate adjudications of each card.

Counts below compare with the coordinator, not the superseded OS1 selection. Kept includes re-tagged. No removals. Each existing card stays in its original section and subgroup. Fault-code coverage counts include witnesses in other subsections, so a multi-fault line has one note document. Shortfalls are stated in section headers and subgroup labels. The six-card cap is per selected subsection; pre-existing cross-tagged witnesses can raise code coverage above six.

The coordinator used `label` / `text` / `google` to read C1 card labels, but those files store `google_text`. Empty Google rows are now filled from that exact field (and feature text for the four unsampled rotated cards). This fixes label display without changing ids, original crops, or groups. The old heuristic fault pill is replaced by exact checker codes. The original Russian group is renamed to include dialogue punctuation: its heuristic classified any Cyrillic р as a yer. Cards and group ids remain intact. Four rotated cards have no checker verdict; their explicit geometry tag is bound to the native crop and features, not invented checker codes. Literal question marks in Russian labels and their quoted corrections are preserved; uncertainty placeholders are expanded to `[uncertain]`, with raw detail retained in evidence.

## failure_modes_per_class

| Section | Kept | Added | Re-tagged | Removed |
|---|---:|---:|---:|---:|
| Polytonic 1850s (BSB) | 7 | 3 | 7 | 0 |
| Numerics and tables (ELSTAT) | 3 | 0 | 3 | 0 |
| Modern monotonic (Gazette 1986–90) | 2 | 8 | 2 | 0 |
| Modern monotonic (Gazette 1982–85) | 5 | 0 | 5 | 0 |
| Latin | 7 | 0 | 7 | 0 |
| Mixed Greek + Latin | 17 | 2 | 17 | 0 |
| Polytonic 1850s (IA) | 19 | 1 | 19 | 0 |
| Cyrillic, Russian pre-1918 | 6 | 6 | 6 | 0 |
| Polytonic 1900s (Kosmopolis) | 13 | 10 | 13 | 0 |
| Polytonic 1900s (Lekythos) | 12 | 17 | 12 | 0 |
| Polytonic (NLG greek_poly) | 8 | 0 | 8 | 0 |
| Polytonic 1850s (NLG) | 11 | 0 | 11 | 0 |
| Polytonic 1900s (NLG) | 13 | 0 | 13 | 0 |
| Cyrillic, Serbian | 10 | 0 | 10 | 0 |

Doc-id continuity: **133/133 kept**. Removed: none.

### Complete old-id continuity ledger

| Old doc id | Original group / section | Result |
|---|---|---|
| `bsb_poly1850--e18cacecef3b4590--s000-l0057` | s0g0 / s0 | kept, re-tagged |
| `bsb_poly1850--e2115ba0deaf6a07--s003-l0039` | s0g1 / s0 | kept, re-tagged |
| `bsb_poly1850--eded5a16c1b78a01--s005-l0055` | s0g1 / s0 | kept, re-tagged |
| `bsb_poly1850--e18cacecef3b4590--s000-l0007` | s0g1 / s0 | kept, re-tagged |
| `bsb_poly1850--d7db5a3b1eb289a3--s003-l0018` | s0g1 / s0 | kept, re-tagged |
| `bsb_poly1850--e18cacecef3b4590--s006-l0078` | s0g3 / s0 | kept, re-tagged |
| `bsb_poly1850--e18cacecef3b4590--s007-l0018` | s0g5 / s0 | kept, re-tagged |
| `elstat--ee37bc488988f1bd--s000-l0445` | s1g0 / s1 | kept, re-tagged |
| `elstat--ee37bc488988f1bd--s000-l0457` | s1g0 / s1 | kept, re-tagged |
| `elstat--c5f7ea1f26d39839--s000-l0367` | s1g1 / s1 | kept, re-tagged |
| `gazette_modern--1f7db88d63c02afa--s000-l0287` | s2g0 / s2 | kept, re-tagged |
| `gazette_modern--5ede709b65bee305--s000-l0016` | s2g1 / s2 | kept, re-tagged |
| `gazette_modern--40234942c05aef6f--s000-l0072` | s3g0 / s3 | kept, re-tagged |
| `gazette_modern--2e613d9290dd13d4--s000-l0209` | s3g1 / s3 | kept, re-tagged |
| `gazette_modern--8823b3ad4820a03d--s000-l0022` | s3g2 / s3 | kept, re-tagged |
| `gazette_modern--e49d2191ace06863--s000-l0041` | s3g3 / s3 | kept, re-tagged |
| `gazette_modern--62822e3af8f17cf4--s000-l0052` | s3g4 / s3 | kept, re-tagged |
| `ia_poly1850--007d7039d12e3816--s003-l0006` | s4g0 / s4 | kept, re-tagged |
| `ia_poly1850--c39403323b6d5d89--s005-l0007` | s4g1 / s4 | kept, re-tagged |
| `ia_poly1850--f806d3f10b2ecf9c--s005-l0058` | s4g2 / s4 | kept, re-tagged |
| `ia_poly1850--f806d3f10b2ecf9c--s003-l0018` | s4g2 / s4 | kept, re-tagged |
| `ia_poly1850--2d02eaf0f19a649a--s001-l0042` | s4g2 / s4 | kept, re-tagged |
| `ia_poly1850--b3d418e8a99d8bec--s005-l0023` | s4g2 / s4 | kept, re-tagged |
| `ia_poly1850--f806d3f10b2ecf9c--s006-l0027` | s4g3 / s4 | kept, re-tagged |
| `ia_poly1850--a89bd2c9bdb1ca6d--s007-l0016` | s5g0 / s5 | kept, re-tagged |
| `ia_poly1850--a89bd2c9bdb1ca6d--s005-l0038` | s5g1 / s5 | kept, re-tagged |
| `ia_poly1850--41e90f3ba967f920--s006-l0022` | s5g1 / s5 | kept, re-tagged |
| `ia_poly1850--2d02eaf0f19a649a--s007-l0032` | s5g1 / s5 | kept, re-tagged |
| `ia_poly1850--6a9e5e4676cec552--s002-l0035` | s5g2 / s5 | kept, re-tagged |
| `ia_poly1850--36dcee7ce4c29f8b--s003-l0110` | s5g2 / s5 | kept, re-tagged |
| `ia_poly1850--4ab77886725d9e1e--s006-l0028` | s5g2 / s5 | kept, re-tagged |
| `ia_poly1850--3773a91327e98bc0--s002-l0006` | s5g2 / s5 | kept, re-tagged |
| `ia_poly1850--8b16b26eee5a53a8--s001-l0033` | s5g3 / s5 | kept, re-tagged |
| `ia_poly1850--21c15fc15dc17003--s002-l0043` | s5g3 / s5 | kept, re-tagged |
| `ia_poly1850--df8f2267db2b7275--s002-l0041` | s5g4 / s5 | kept, re-tagged |
| `ia_poly1850--41e90f3ba967f920--s001-l0025` | s5g5 / s5 | kept, re-tagged |
| `ia_poly1850--007d7039d12e3816--s001-l0007` | s5g6 / s5 | kept, re-tagged |
| `ia_poly1850--36dcee7ce4c29f8b--s004-l0061` | s5g7 / s5 | kept, re-tagged |
| `ia_poly1850--e6e379cb4b1d54af--s003-l0025` | s5g8 / s5 | kept, re-tagged |
| `ia_poly1850--ebcfd6056abfa776--s003-l0099` | s5g8 / s5 | kept, re-tagged |
| `ia_poly1850--174d84a441d69a70--s002-l0040` | s5g9 / s5 | kept, re-tagged |
| `ia_poly1850--ca4f3983c96b6334--s001-l0007` | s6g0 / s6 | kept, re-tagged |
| `ia_poly1850--df8f2267db2b7275--s002-l0037` | s6g1 / s6 | kept, re-tagged |
| `ia_poly1850--2d02eaf0f19a649a--s005-l0015` | s6g2 / s6 | kept, re-tagged |
| `ia_poly1850--adb0f3293921eb50--s003-l0015` | s6g2 / s6 | kept, re-tagged |
| `ia_poly1850--63f57af8d450f3e8--s001-l0045` | s6g2 / s6 | kept, re-tagged |
| `ia_poly1850--231a44f61c5268e0--s001-l0026` | s6g2 / s6 | kept, re-tagged |
| `ia_poly1850--df8f2267db2b7275--s004-l0037` | s6g3 / s6 | kept, re-tagged |
| `ia_poly1850--ca4f3983c96b6334--s000-l0007` | s6g3 / s6 | kept, re-tagged |
| `ia_poly1850--adb0f3293921eb50--s006-l0016` | s6g4 / s6 | kept, re-tagged |
| `ia_poly1850--df8f2267db2b7275--s004-l0021` | s6g4 / s6 | kept, re-tagged |
| `ia_poly1850--29e9490734cc1653--s002-l0014` | s6g4 / s6 | kept, re-tagged |
| `ia_poly1850--ca4f3983c96b6334--s001-l0026` | s6g5 / s6 | kept, re-tagged |
| `ia_poly1850--2d02eaf0f19a649a--s005-l0018` | s6g6 / s6 | kept, re-tagged |
| `ia_poly1850--36dcee7ce4c29f8b--s000-l0055` | s6g7 / s6 | kept, re-tagged |
| `ia_poly1850--36dcee7ce4c29f8b--s001-l0067` | s6g7 / s6 | kept, re-tagged |
| `ia_poly1850--34543d92a48213e7--s001-l0026` | s6g7 / s6 | kept, re-tagged |
| `ia_poly1850--34543d92a48213e7--s002-l0012` | s6g7 / s6 | kept, re-tagged |
| `ia_poly1850--29e9490734cc1653--s002-l0016` | s6g8 / s6 | kept, re-tagged |
| `ia_poly1850--ac5b9928804aaa3d--s000-l0022` | s6g9 / s6 | kept, re-tagged |
| `ia_russian--3fd32314d172e951--s001-l0005` | s7g0 / s7 | kept, re-tagged |
| `ia_russian--3fd32314d172e951--s002-l0006` | s7g0 / s7 | kept, re-tagged |
| `ia_russian--3fd32314d172e951--s005-l0023` | s7g0 / s7 | kept, re-tagged |
| `ia_russian--3fd32314d172e951--s005-l0038` | s7g0 / s7 | kept, re-tagged |
| `ia_russian--d558bd3e803e7865--s003-l0032` | s7g0 / s7 | kept, re-tagged |
| `ia_russian--d558bd3e803e7865--s003-l0017` | s7g0 / s7 | kept, re-tagged |
| `kosmopolis--86098eebf5207e79--s006-l0038` | s8g0 / s8 | kept, re-tagged |
| `kosmopolis--ecc23d7812913d0a--s000-l0042` | s8g0 / s8 | kept, re-tagged |
| `kosmopolis--acb323b6cb8d169d--s000-l0020` | s8g0 / s8 | kept, re-tagged |
| `kosmopolis--654bf46f6d37c4b4--s003-l0014` | s8g0 / s8 | kept, re-tagged |
| `kosmopolis--86098eebf5207e79--s001-l0002` | s8g0 / s8 | kept, re-tagged |
| `kosmopolis--86098eebf5207e79--s006-l0049` | s8g0 / s8 | kept, re-tagged |
| `kosmopolis--3ccb484c8655e2ec--s003-l0022` | s8g1 / s8 | kept, re-tagged |
| `kosmopolis--ef37f6cfdd896488--s000-l0010` | s8g1 / s8 | kept, re-tagged |
| `kosmopolis--62ca52b56ebe780a--s005-l0023` | s8g1 / s8 | kept, re-tagged |
| `kosmopolis--ecc23d7812913d0a--s001-l0018` | s8g2 / s8 | kept, re-tagged |
| `kosmopolis--8f8439af940ad55b--s006-l0010` | s8g3 / s8 | kept, re-tagged |
| `kosmopolis--654bf46f6d37c4b4--s001-l0007` | s8g3 / s8 | kept, re-tagged |
| `kosmopolis--8ac130e14e062423--s001-l0016` | s8g3 / s8 | kept, re-tagged |
| `lekythos--456def1ccfc2283e--s003-l0167` | s9g0 / s9 | kept, re-tagged |
| `lekythos--dd72392a3777225e--s002-l0271` | s9g0 / s9 | kept, re-tagged |
| `lekythos--9447d290d59a2411--s000-l0254` | s9g0 / s9 | kept, re-tagged |
| `lekythos--9447d290d59a2411--s000-l0429` | s9g0 / s9 | kept, re-tagged |
| `lekythos--36e76126a4edbc72--s001-l0077` | s9g1 / s9 | kept, re-tagged |
| `lekythos--49c082ba27aa27da--s001-l0191` | s9g1 / s9 | kept, re-tagged |
| `lekythos--7f67b784930deef5--s000-l0052` | s9g1 / s9 | kept, re-tagged |
| `lekythos--49c082ba27aa27da--s002-l0179` | s9g1 / s9 | kept, re-tagged |
| `lekythos--793fb44fdc7e1aa6--s000-l0302` | s9g1 / s9 | kept, re-tagged |
| `lekythos--0fc3672826ddd6b3--s003-l0041` | s9g1 / s9 | kept, re-tagged |
| `lekythos--25feca8f4ab34ba0--s002-l0095` | s9g2 / s9 | kept, re-tagged |
| `lekythos--40ed3fea207e3d94--s002-l0006` | s9g3 / s9 | kept, re-tagged |
| `nlg--3d6bd7bd688acb61--s004-l0027` | s10g0 / s10 | kept, re-tagged |
| `nlg--3d6bd7bd688acb61--s000-l0025` | s10g0 / s10 | kept, re-tagged |
| `nlg--3d6bd7bd688acb61--s004-l0019` | s10g0 / s10 | kept, re-tagged |
| `nlg--3d6bd7bd688acb61--s002-l0014` | s10g0 / s10 | kept, re-tagged |
| `nlg--3d6bd7bd688acb61--s001-l0031` | s10g1 / s10 | kept, re-tagged |
| `nlg--3d6bd7bd688acb61--s007-l0027` | s10g1 / s10 | kept, re-tagged |
| `nlg--3d6bd7bd688acb61--s000-l0022` | s10g2 / s10 | kept, re-tagged |
| `nlg--3d6bd7bd688acb61--s003-l0033` | s10g3 / s10 | kept, re-tagged |
| `nlg--9aff599c7fffc574--s006-l0013` | s11g0 / s11 | kept, re-tagged |
| `nlg--9aff599c7fffc574--s006-l0008` | s11g0 / s11 | kept, re-tagged |
| `nlg--9aff599c7fffc574--s002-l0015` | s11g1 / s11 | kept, re-tagged |
| `nlg--9aff599c7fffc574--s003-l0007` | s11g1 / s11 | kept, re-tagged |
| `nlg--3d71f4f87abea186--s002-l0017` | s11g2 / s11 | kept, re-tagged |
| `nlg--3d71f4f87abea186--s004-l0011` | s11g2 / s11 | kept, re-tagged |
| `nlg--3d71f4f87abea186--s002-l0032` | s11g3 / s11 | kept, re-tagged |
| `nlg--6146c0455e0103d2--s007-l0016` | s11g3 / s11 | kept, re-tagged |
| `nlg--6146c0455e0103d2--s001-l0025` | s11g3 / s11 | kept, re-tagged |
| `nlg--6146c0455e0103d2--s004-l0009` | s11g4 / s11 | kept, re-tagged |
| `nlg--df6ccc87357b61b6--s001-l0011` | s11g5 / s11 | kept, re-tagged |
| `nlg--7870403c3df244ea--s000-l0016` | s12g0 / s12 | kept, re-tagged |
| `nlg--7870403c3df244ea--s007-l0025` | s12g0 / s12 | kept, re-tagged |
| `nlg--1144074169f43992--s006-l0032` | s12g1 / s12 | kept, re-tagged |
| `nlg--f4b52df5f8130047--s003-l0032` | s12g2 / s12 | kept, re-tagged |
| `nlg--f4b52df5f8130047--s005-l0019` | s12g2 / s12 | kept, re-tagged |
| `nlg--f4b52df5f8130047--s002-l0030` | s12g2 / s12 | kept, re-tagged |
| `nlg--1144074169f43992--s007-l0025` | s12g2 / s12 | kept, re-tagged |
| `nlg--1144074169f43992--s002-l0003` | s12g2 / s12 | kept, re-tagged |
| `nlg--1144074169f43992--s000-l0004` | s12g2 / s12 | kept, re-tagged |
| `nlg--7870403c3df244ea--s005-l0015` | s12g3 / s12 | kept, re-tagged |
| `nlg--7870403c3df244ea--s005-l0016` | s12g4 / s12 | kept, re-tagged |
| `nlg--1144074169f43992--s002-l0018` | s12g4 / s12 | kept, re-tagged |
| `nlg--f4b52df5f8130047--s005-l0015` | s12g5 / s12 | kept, re-tagged |
| `serbia--27b182bf4116728f--s001-l0026` | s13g0 / s13 | kept, re-tagged |
| `serbia--42fedee06e6cb85a--s000-l0022` | s13g0 / s13 | kept, re-tagged |
| `serbia--27b182bf4116728f--s001-l0002` | s13g0 / s13 | kept, re-tagged |
| `serbia--27b182bf4116728f--s001-l0035` | s13g0 / s13 | kept, re-tagged |
| `serbia--8fd9a36edc06b7f9--s001-l0004` | s13g0 / s13 | kept, re-tagged |
| `serbia--fc66165678b402fe--s001-l0032` | s13g0 / s13 | kept, re-tagged |
| `serbia--27b182bf4116728f--s001-l0021` | s13g1 / s13 | kept, re-tagged |
| `serbia--46c745f49e7507f4--s001-l0015` | s13g2 / s13 | kept, re-tagged |
| `serbia--9caa9fc02f50cad6--s001-l0009` | s13g2 / s13 | kept, re-tagged |
| `serbia--9f13a55215086cab--s000-l0012` | s13g2 / s13 | kept, re-tagged |

### Added ids

- `bsb_poly1850--1c417ec1fdb5d021--s001-l0022` — s0g2
- `bsb_poly1850--2032df1e3e983f1d--s001-l0015` — s0g5
- `bsb_poly1850--2fdb06c3a8566781--s003-l0023` — s0g2
- `gazette_modern--540b8d8de6eeb97f--s000-l0061` — s2_t6b_missing_word_or_span
- `gazette_modern--5a173b5ea9cc9922--s000-l0083` — s2_t6b_punctuation
- `gazette_modern--5ede709b65bee305--s000-l0098` — s2_t6b_wrong_letter
- `gazette_modern--73e4d3191f16b5e2--s000-l0091` — s2_t6b_crop_overrun
- `gazette_modern--9a7f184282a21b5e--s000-l0036` — s2_t6b_crop_overrun
- `gazette_modern--b45c6f04968613c9--s000-l0041` — s2_t6b_punctuation
- `gazette_modern--c1b2194696b35bb5--s000-l0077` — s2_t6b_extra_mark
- `gazette_modern--e4eb54e6104b20e6--s000-l0022` — s2_t6b_crop_overrun
- `ia_poly1850--29e9490734cc1653--s004-l0031` — s5g9
- `ia_poly1850--a89bd2c9bdb1ca6d--s004-l0025` — s5g9
- `ia_poly1850--ac5b9928804aaa3d--s007-l0016` — s6g9
- `ia_russian--03b43bc5289ad8ce--s003-l0028` — s7_yer
- `ia_russian--03b43bc5289ad8ce--s005-l0011` — s7_yer
- `ia_russian--03b43bc5289ad8ce--s007-l0006` — s7_yer
- `ia_russian--3fd32314d172e951--s006-l0010` — s7_yer
- `ia_russian--4ce4c0e3183ce075--s004-l0017` — s7_yer
- `ia_russian--61f76a57b26f9b13--s003-l0009` — s7_yer
- `kosmopolis--3ccb484c8655e2ec--s004-l0015` — s8_t6b_punctuation
- `kosmopolis--62ca52b56ebe780a--s005-l0034` — s8_t6b_crop_overrun
- `kosmopolis--654bf46f6d37c4b4--s007-l0020` — s8_t6b_wrong_mark
- `kosmopolis--86098eebf5207e79--s001-l0001` — s8_t6b_hyphen
- `kosmopolis--86098eebf5207e79--s004-l0016` — s8_t6b_extra_mark
- `kosmopolis--aaa124307e36f113--s001-l0062` — s8_t6b_crop_clipped
- `kosmopolis--addc07a6b4eaefef--s002-l0002` — s8_t6b_crop_clipped
- `kosmopolis--ef37f6cfdd896488--s002-l0036` — s8_t6b_missing_mark
- `kosmopolis--ef37f6cfdd896488--s002-l0041` — s8_t6b_punctuation
- `kosmopolis--ef37f6cfdd896488--s005-l0008` — s8_t6b_missing_mark
- `lekythos--0fc3672826ddd6b3--s000-l0033` — s9_t6b_wrong_mark
- `lekythos--1a3def6495932802--s000-l0144` — s9_t6b_wrong_mark
- `lekythos--1a3def6495932802--s001-l0133` — s9_t6b_wrong_letter
- `lekythos--1a3def6495932802--s001-l0262` — s9_t6b_punctuation
- `lekythos--3bfc4a385d61b883--s000-l0106` — s9_t6b_missing_mark
- `lekythos--456def1ccfc2283e--s001-l0119` — s9_t6b_crop_clipped
- `lekythos--456def1ccfc2283e--s002-l0041` — s9_t6b_wrong_mark
- `lekythos--793fb44fdc7e1aa6--s000-l0247` — s9g3
- `lekythos--7f67b784930deef5--s002-l0007` — s9_t6b_punctuation
- `lekythos--7f67b784930deef5--s003-l0048` — s9_t6b_crop_overrun
- `lekythos--7f67b784930deef5--s003-l0071` — s9_t6b_crop_overrun
- `lekythos--9447d290d59a2411--s000-l0388` — s9_t6b_extra_text
- `lekythos--dd72392a3777225e--s000-l0264` — s9_t6b_missing_mark
- `lekythos--dd72392a3777225e--s002-l0131` — s9_t6b_missing_mark
- `lekythos--e9f314aab488b65f--s001-l0199` — s9g3
- `lekythos--e9f314aab488b65f--s001-l0335` — s9_t6b_crop_clipped
- `lekythos--ff539dec2e1680a7--s000-l0214` — s9_t6b_punctuation

### Printed prefills and sources

| Doc id | Printed | Source and method |
|---|---|---|
| `bsb_poly1850--e18cacecef3b4590--s000-l0057` | καὶ ἡ ὑπὸ τῆς Ῥωσσίας πρόσκτησις τοῦ ση- | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/bsb_poly1850__poly1850__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c002 |
| `bsb_poly1850--e2115ba0deaf6a07--s003-l0039` | ὅσῳ βραχυτέρα καὶ ἧττον στενὴ, τόσῳ εὐθεραπευτοτέρα εἶναι αὕτη. | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/bsb_poly1850__poly1850__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c004 |
| `bsb_poly1850--eded5a16c1b78a01--s005-l0055` | γοῦν ἐφεξῆς σημεῖον τοῦ νοήματος δίδοσιν ἀκριβὲς, | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/bsb_poly1850__poly1850__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c019 |
| `bsb_poly1850--e18cacecef3b4590--s000-l0007` | θήκης μέγα καὶ ἰσχυρὸν σλαυϊκὸν κράτος ἱδρύε- | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/bsb_poly1850__poly1850__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c032 |
| `bsb_poly1850--d7db5a3b1eb289a3--s003-l0018` | τὴν λείαν. ἐγὼ δέ, ἔφη, ἐπὶ τούσδε, ἣν ἐπὶ σὲ κινῶνται, | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/bsb_poly1850__poly1850__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c038 |
| `bsb_poly1850--e18cacecef3b4590--s006-l0078` | Θεὸς, ἀπήντησεν αὐτό. Ὁ Θεὸς λοιπὸν σὲ ἀγαπᾷ; | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/bsb_poly1850__poly1850__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c087 |
| `bsb_poly1850--e18cacecef3b4590--s007-l0018` | ζε πρὸς ἴριδα ἐν μέσῳ θυέλλης· διότι ἡ ἴρις καίπερ | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/bsb_poly1850__poly1850__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c024 |
| `elstat--ee37bc488988f1bd--s000-l0445` | 4·547·331 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/elstat__numerics_tables__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c038 |
| `elstat--ee37bc488988f1bd--s000-l0457` | 4·479·781 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/elstat__numerics_tables__b.jsonl`; explicit full-label substitution in checker context; c093 |
| `elstat--c5f7ea1f26d39839--s000-l0367` | 555,6 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/elstat__numerics_tables__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c013 |
| `gazette_modern--40234942c05aef6f--s000-l0072` | Υψηλή Πίεση και Υποσταθ- | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/gazette_modern__modern_scanned__probe_1982_1985__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c043 |
| `gazette_modern--e49d2191ace06863--s000-l0041` | συμμετοχής του στο Ταμείο, χορηγείται σ' αυτόν ή στους | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/gazette_modern__modern_scanned__probe_1982_1985__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c003 |
| `ia_poly1850--007d7039d12e3816--s003-l0006` | mirum esse nemo potest negare initium cap. 15ⁱ, quo Thucydides | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__latin__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c066 |
| `ia_poly1850--f806d3f10b2ecf9c--s005-l0058` | tunc essent ab episcoporum regimine immunia, nus- | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__latin__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c004 |
| `ia_poly1850--a89bd2c9bdb1ca6d--s007-l0016` | WIII 180 29 ἐν καιροῖς καὶ ἀνταπεδίδου τοῖς ἁμαρτήσασιν. ὧν δὲ τὴν | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__mixed_greek_latin__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c011 |
| `ia_poly1850--a89bd2c9bdb1ca6d--s005-l0038` | Λαῖτοι 1. Laetus a Septimio | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__mixed_greek_latin__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c013 |
| `ia_poly1850--41e90f3ba967f920--s006-l0022` | associated with θλῖψις (Rom. ii. 9; viii. 35; 2 Cor. vi. 4; | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__mixed_greek_latin__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c060 |
| `ia_poly1850--2d02eaf0f19a649a--s007-l0032` | to the κρᾶσις, only because, as had been formerly said, without | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__mixed_greek_latin__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c067 |
| `ia_poly1850--6a9e5e4676cec552--s002-l0035` | omittam 2) exhibet haec: (cf. Ἀκροασις Α'ν 110—133 in ed. Leonis | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__mixed_greek_latin__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c014 |
| `ia_poly1850--4ab77886725d9e1e--s006-l0028` | § 143. n.—In Comic verse περὶ is | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__mixed_greek_latin__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c057 |
| `ia_poly1850--3773a91327e98bc0--s002-l0006` | cussion ἡ ὑποκειμένη ὕλη,—ὑπόθεσις. | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__mixed_greek_latin__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c077 |
| `ia_poly1850--8b16b26eee5a53a8--s001-l0033` | 1 Ἐκέλευσεν αὐτὸν ἄγεσθαι εἰς τὴν παρεμβολὴν. See above, pp. 253, 4, 5. | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__mixed_greek_latin__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c018 |
| `ia_poly1850--21c15fc15dc17003--s002-l0043` | τὴν ἐπισκοπὴν νεωστὶ τότε μετὰ Ἰουλιανὸν Δημήτριος ὑπειλήφει, ist somit | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__mixed_greek_latin__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c092 |
| `ia_poly1850--41e90f3ba967f920--s001-l0025` | οἶκτος cognatio est. Ὁ ἔλεος ægritudinem benevole ex | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__mixed_greek_latin__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c069 |
| `ia_poly1850--007d7039d12e3816--s001-l0007` | Corinthios esse locutos et quae essent locuti (c. 72 § 1: ὡς ἤσθοντο | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__mixed_greek_latin__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c081 |
| `ia_poly1850--36dcee7ce4c29f8b--s004-l0061` | κούσωσιν LTrWHR, ἀκούσονται T. superscript 6 κηρύξωσιν LTTrWHR. | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__mixed_greek_latin__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c059 |
| `ia_poly1850--e6e379cb4b1d54af--s003-l0025` | Strabonem eodem loco (ὃς τοῦ Ζήνωνος τοῦ Κιτιέως γνώρι- | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__mixed_greek_latin__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c002 |
| `ia_poly1850--ebcfd6056abfa776--s003-l0099` | ward (vgl. zu 3, 4), ebenso der Artikel vor Πιλάτῳ neben dem artieulirten τὸν Ἰησοῦν oder | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__mixed_greek_latin__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c010 |
| `ia_poly1850--ca4f3983c96b6334--s001-l0007` | Ἡλιόδ 244, 48. καὶ πολλὰ τὴν θεὰν ὡς δολερὰν | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__poly1850__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c004 |
| `ia_poly1850--df8f2267db2b7275--s002-l0037` | μνηστῆρες ἦλθον Ἑλλάδος νεανίαι. | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__poly1850__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c007 |
| `ia_poly1850--2d02eaf0f19a649a--s005-l0015` | καὶ γενησόμενα καὶ γεγονότα ἡμῶν ὁ τοιοῦτος ἀνῄρηται τὸν | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__poly1850__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c010 |
| `ia_poly1850--adb0f3293921eb50--s003-l0015` | ἐλπὶς, τοῦ μέλλοντος· ἡ δὲ μνήμη, τῶν παροιχομένων. Ὅπερ | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__poly1850__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c015 |
| `ia_poly1850--63f57af8d450f3e8--s001-l0045` | βρίζειν εἰς ὑμᾶς 32. ἐξηπάτησε, Ποτίδαιαν, | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__poly1850__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c034 |
| `ia_poly1850--231a44f61c5268e0--s001-l0026` | τῶν δημοτικῶν ᾀσμάτων· τὰ ὀλίγα ἐκεῖνα σπέρματα, τὰ ὁποῖα καὶ μόνα | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__poly1850__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c053 |
| `ia_poly1850--df8f2267db2b7275--s004-l0037` | οὔ που λέλειμμαι καὶ νεωτέρων κακῶν | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__poly1850__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c046 |
| `ia_poly1850--ca4f3983c96b6334--s000-l0007` | μοκράτης, ὅν παρουσιάζει ἡμῖν ἐν τέλει τοῦ μυθιστορήμα- | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__poly1850__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c083 |
| `ia_poly1850--adb0f3293921eb50--s006-l0016` | ἐγὼ δὲ ἥμαρτον. Καὶ τῶν ἀποφθεγμάτων δὲ τὰ ἀστεῖά ἐστιν | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__poly1850__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c049 |
| `ia_poly1850--df8f2267db2b7275--s004-l0021` | εὕρω πτερωτὸς ἢ κατὰ χθονὸς μολών; | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__poly1850__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c052 |
| `ia_poly1850--29e9490734cc1653--s002-l0014` | ζῶμα δέ οἱ πρῶτον παρακάββαλεν, αὐτὰρ ἔπειτα | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__poly1850__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c089 |
| `ia_poly1850--ca4f3983c96b6334--s001-l0026` | Ἡ ποιητικὴ λέξις γόος παρὰ Ξενοφῶντι οὐκ ἀπαντᾷ· | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__poly1850__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c077 |
| `ia_poly1850--2d02eaf0f19a649a--s005-l0018` | ΣΩ. Τούτων οὖν τι σαφὲς ἂν φαῖμεν τῆ ἀκριβεστάτη ἀλη- | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__poly1850__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c080 |
| `ia_poly1850--36dcee7ce4c29f8b--s001-l0067` | ὀργῆς, συλ²⁸λυπούμενος ἐπὶ τῇ ᵐ πωρώσει τῆς καρδίας | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__poly1850__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c088 |
| `ia_poly1850--34543d92a48213e7--s001-l0026` | οὔτε τὴν Μίλητον οἷοί τε ἔωσι ἐξελεῖν μὴ οὐκ ἐόντες ναυκράτορες ²⁴, | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__poly1850__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c093 |
| `ia_poly1850--34543d92a48213e7--s002-l0012` | ἐν τῇ ναυμαχίῃ ταύτῃ ἑτεραλκέως ²⁷ ἀγωνιζομένους νὺξ ἐπελθοῦσα | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__poly1850__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c095 |
| `ia_poly1850--29e9490734cc1653--s002-l0016` | 685 τὼ δὲ ζωσαμένω βήτην ἐς μέσσον ἀγῶνα, | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__poly1850__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c022 |
| `ia_russian--3fd32314d172e951--s002-l0006` | А ты видалъ такихъ?—спросилъ Челкашъ, съ | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_russian__cyrillic__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c076 |
| `ia_russian--3fd32314d172e951--s005-l0023` | что?!“ Ну, братъ, и крикнула!—Я такъ и вздрогнулъ. | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/yer_adjudication/table.json`; adjudicated yer slots in the full Google label; c079 |
| `ia_russian--3fd32314d172e951--s005-l0038` | щечкахъ, глазенки большіе такіе—смотрятъ такъ... и | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_russian__cyrillic__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c080 |
| `ia_russian--d558bd3e803e7865--s003-l0032` | не мудрено добыть, а не хватитъ рыбы—онъ и | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_russian__cyrillic__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c084 |
| `ia_russian--d558bd3e803e7865--s003-l0017` | и не потужитъ. И вынесетъ голодъ его привычный | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/yer_adjudication/table.json`; adjudicated yer slots in the full Google label; c006 |
| `kosmopolis--86098eebf5207e79--s006-l0038` | θεται τὸν κ. Ρουσσὲλ σχετικὰ μὲ τὶς γνῶμες του γιὰ τὴ νεοελληνι- | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/kosmopolis__poly1900__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c009 |
| `kosmopolis--ecc23d7812913d0a--s000-l0042` | μέρη τὸ σαγηνευτικὸ τραγούδι τοῦ Μαλακάση. | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/kosmopolis__poly1900__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c010 |
| `kosmopolis--acb323b6cb8d169d--s000-l0020` | Πιερίδης, νέος καθὼς εἶναι, ἐρχότανε σὰ συνεχιστὴς ἢ συμπληρω- | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/kosmopolis__poly1900__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c013 |
| `kosmopolis--654bf46f6d37c4b4--s003-l0014` | Κάποτε ἀναστεναγμοὶ ἀντίκοφταν τὴ θλιβερὴ σιωπή. | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/kosmopolis__poly1900__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c041 |
| `kosmopolis--86098eebf5207e79--s001-l0002` | κρυά σου παρὰ τὸ γλυκὸ κρασί!... | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/kosmopolis__poly1900__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c051 |
| `kosmopolis--86098eebf5207e79--s006-l0049` | περιοδικοῦ) περιγράφει τὸν ἐκλεκτὸ λόγιο παραθερίζοντα στὴ Ζα- | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/kosmopolis__poly1900__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c068 |
| `kosmopolis--3ccb484c8655e2ec--s003-l0022` | ποιητικὴ περίληψη ἄλλου μεγαλόπνοου ἔπους. Ὁρίστε τη· | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/kosmopolis__poly1900__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c017 |
| `kosmopolis--ecc23d7812913d0a--s001-l0018` | μὰ ποὺ εἶναι στολισμένα μὲ τὴν εἰρωνία καὶ μὲ τὸ χιοῦμορ. | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/kosmopolis__poly1900__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c023 |
| `kosmopolis--8f8439af940ad55b--s006-l0010` | Ἔχουνε βάλει, τοῦ εἶπε ὁ ἄνθρωπος αὐτὸς μὲ | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/kosmopolis__poly1900__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c030 |
| `kosmopolis--654bf46f6d37c4b4--s001-l0007` | Ἆ, αὐτὸς εἶταν τώρα σμιγμένος μὲ τὴ ζωὴ τοῦ Γρη- | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/kosmopolis__poly1900__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c040 |
| `lekythos--456def1ccfc2283e--s003-l0167` | ἔπρεπε σὰν νὰ πίστευαν, παίρνοντας ἅγι | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/lekythos__poly1900__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c005 |
| `lekythos--dd72392a3777225e--s002-l0271` | Ἑλληνικό. Ἤ μήπως τὸ στυλιζάρισμα ἔστειλε | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/lekythos__poly1900__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c031 |
| `lekythos--9447d290d59a2411--s000-l0254` | καταντήσει προβληματική. Ἄς ἀφήσουμε τὶς | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/lekythos__poly1900__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c051 |
| `lekythos--9447d290d59a2411--s000-l0429` | σέχετε περισσότερο στὶς χασμωδίες. Ἔχουμε | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/lekythos__poly1900__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c075 |
| `lekythos--36e76126a4edbc72--s001-l0077` | λόγου ὅτι ὁ λαβὼν τὴν συνέντευξη νεαρὸς συντάκτης ἔχει | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/lekythos__poly1900__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c009 |
| `lekythos--49c082ba27aa27da--s001-l0191` | μασία τοῦ κυβερνητικοῦ ἔργου. Καλὴ πίστη ἔχουνε | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/lekythos__poly1900__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c030 |
| `lekythos--7f67b784930deef5--s000-l0052` | Μὰ τὸ σπουδαιότατο ὅπλο τῆς κάθε πολεμικῆς μὲ ὁπωσδήποτε κοινωνικὸ περιεχό- | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/lekythos__poly1900__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c033 |
| `lekythos--49c082ba27aa27da--s002-l0179` | λοίμονον ὅμως ! Καθαρὸ θεωρητικὸ πνεῦμα | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/lekythos__poly1900__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c035 |
| `lekythos--793fb44fdc7e1aa6--s000-l0302` | κατηγορήσῃς γιὰ τίποτα; Φέρθηκα ποτὲ | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/lekythos__poly1900__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c042 |
| `lekythos--0fc3672826ddd6b3--s003-l0041` | τερη τέχνη θὰ εἶναι δῶρον ἄδωρον, θροφὴ | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/lekythos__poly1900__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c044 |
| `lekythos--25feca8f4ab34ba0--s002-l0095` | ποτὲ νὰ περιγράψῃ | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/lekythos__poly1900__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c054 |
| `lekythos--40ed3fea207e3d94--s002-l0006` | βλέπῃ τὰ παιδιά, τοὺς συγγενεῖς τοὺς φίλους, | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/lekythos__poly1900__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c034 |
| `nlg--3d6bd7bd688acb61--s004-l0027` | Ἰμβραὴμ κατὰ τῆς Μάνης, οἱ δὲ Μανιᾶται διὰ τῆς νί- | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__greek_poly__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c005 |
| `nlg--3d6bd7bd688acb61--s000-l0025` | καὶ ἔβγαλἀν τὰς λέμβσυς ἀπὸ τὰ μέρος τῆς θαλάσσης | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__greek_poly__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c012 |
| `nlg--3d6bd7bd688acb61--s004-l0019` | Ὁ δὲ Ἰμβραὴμ μετὰ τοῦ στρατοῦ του, ὡς εἴπαμεν, | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__greek_poly__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c021 |
| `nlg--3d6bd7bd688acb61--s002-l0014` | τοῦτο εἶχε πολλοὺς μισθωτοὺς στρατιώτας ἀπὸ τὰ διά- | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__greek_poly__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c100 |
| `nlg--3d6bd7bd688acb61--s001-l0031` | ἄλλοι τότε ὠπισθοδρόμησαν, καὶ οὕτως ηὗρε καιρὸν καὶ | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__greek_poly__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c013 |
| `nlg--3d6bd7bd688acb61--s007-l0027` | πως συνέβη ἡ τοιαύτη ἕνωσις. | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__greek_poly__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c087 |
| `nlg--3d6bd7bd688acb61--s000-l0022` | λιάδες Ἕλληνες, χωρὶς νὰ ἔχουν τροφάς. Τὴν δὲ εἰκο- | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__greek_poly__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c083 |
| `nlg--3d6bd7bd688acb61--s003-l0033` | νιστής του, ὥς τινες ἱστορικοὶ λέγουσιν. Ἐπειδὴ δὲ ὁ | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__greek_poly__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c092 |
| `nlg--9aff599c7fffc574--s006-l0013` | Ἡ δευτέρα ἤδη πολιορκία τῶν φρουρίων ἐγένετο τολμηροτέρα παρὰ | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__poly1850__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c007 |
| `nlg--9aff599c7fffc574--s006-l0008` | γιον κτῆνος πάντα τὸν μὴ μουσουλμάνον κόσμον ; Ἀληθὲς τοῦτο· πλὴν | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__poly1850__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c070 |
| `nlg--9aff599c7fffc574--s002-l0015` | καὶ μόνον ἐν τῂ φυγῇ ἐζήτησαν οἱ πάντες προσωπικὴν σωτηρίαν. Ἀνα- | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__poly1850__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c011 |
| `nlg--9aff599c7fffc574--s003-l0007` | ἱκανῶς τοῦ Ἀσκήφου, ἐπέπεσον αἴφνης καὶ ἐκ διαφόρων μερῶν τῇ πρωΐᾳ | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__poly1850__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c066 |
| `nlg--3d71f4f87abea186--s002-l0017` | μάτων, ὡς βαθμηδὸν θέλομεν ἰδεῖ κατωτέρω, ἐν ταῖς πρὸς τὸν | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__poly1850__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c017 |
| `nlg--3d71f4f87abea186--s004-l0011` | τὸν συστηματικὸν ἐκεῖνον χαρακτῆρα ἐν τοῖς καθόλου νὰ | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__poly1850__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c055 |
| `nlg--3d71f4f87abea186--s002-l0032` | 6) Ὀδ. Ρ, 485—488. σημειωτέον ἐνταῦθα τὸ ἐλλιπὲς τῆς θείας | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__poly1850__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c032 |
| `nlg--6146c0455e0103d2--s007-l0016` | —Ὄχι διὰ τὴν κλεψία τοῦ μαγαζιοῦ. | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__poly1850__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c058 |
| `nlg--6146c0455e0103d2--s001-l0025` | —Ἐπαναβλεπόμεθα εἰς τὸ παιγνίδι, διότι | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__poly1850__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c097 |
| `nlg--6146c0455e0103d2--s004-l0009` | πρὸς αὐτὸν κηρὸν ἀνημμένον, καὶ καθ' ἥν στι- | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__poly1850__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c090 |
| `nlg--df6ccc87357b61b6--s001-l0011` | μιαιφονία νὰ περικαλυφθῇ· διό, παρκμορφώσαντες οἱ ἔνοχοι τὴν | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__poly1850__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c018 |
| `nlg--7870403c3df244ea--s000-l0016` | Ὁ Μαρκαντώνιος Ἰουστινιάνης ἐθύμωσε πάλι | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__poly1900__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c007 |
| `nlg--f4b52df5f8130047--s003-l0032` | χιασμα θερμὸ κι αὐτοῦ καὶ ζαλίζανε τὸ νού του. | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__poly1900__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c023 |
| `nlg--f4b52df5f8130047--s005-l0019` | Μονάχα ὁ Γιαννακὸς Πλαστάρας κι ὁ Μάνθος Σακαρέλος | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__poly1900__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c041 |
| `nlg--f4b52df5f8130047--s002-l0030` | τίκρυ. Οἱ ξενύχτηδες τὸν ξέρανε πὼς τοῦ ἀρέσαν οἱ καλὲς φωνὲς | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__poly1900__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c051 |
| `nlg--1144074169f43992--s002-l0003` | Τὰ πράγματα ξετυλίχθηκαν ἀπαράλλακτα σχεδὸν, ὅπως τὰ | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__poly1900__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c086 |
| `nlg--1144074169f43992--s000-l0004` | κήθηκε. Σὲ λίγο ἦταν καθισμένη μὲ τὸ στανιὸ στὰ γόνατα | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__poly1900__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c087 |
| `nlg--7870403c3df244ea--s005-l0015` | ἡ ὡραία γυναῖκα ποῦ ἤξερε νὰ βαστάξῃ δικό της | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__poly1900__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c049 |
| `nlg--7870403c3df244ea--s005-l0016` | ἕναν ἄντρα της μὲ τὲς χάρες τοῦ κορμιοῦ της, μὲ | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__poly1900__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c052 |
| `nlg--1144074169f43992--s002-l0018` | σὲ μιὰ πολυθρόνα, καί, χωρὶς νὰ κοιτάζῃ πιὰ τὴ γυναῖκά του. | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__poly1900__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c065 |
| `serbia--27b182bf4116728f--s001-l0026` | страдални̑ка-мучени̑ка, за четири века; првосвеште- | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/serbia__cyrillic__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c032 |
| `serbia--42fedee06e6cb85a--s000-l0022` | И Зевс је разљућен тиме са чина њенога срино̂, | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/serbia__cyrillic__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c077 |
| `serbia--27b182bf4116728f--s001-l0002` | ову по свету српском: Бе̄лу Гра̑ду с платна град- | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/serbia__cyrillic__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c097 |
| `serbia--27b182bf4116728f--s001-l0035` | краљу од Србије — с госпоштином сјајном | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/serbia__cyrillic__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c058 |
| `serbia--8fd9a36edc06b7f9--s001-l0004` | стојаније — разлике међу словенским језицима постају од | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/serbia__cyrillic__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c073 |
| `serbia--fc66165678b402fe--s001-l0032` | изгуби живот... Добар је Бог — заврши и у- | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/serbia__cyrillic__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c080 |
| `serbia--27b182bf4116728f--s001-l0021` | поклоника̑ праху бесмртника | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/serbia__cyrillic__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c049 |
| `serbia--46c745f49e7507f4--s001-l0015` | казао најкраћи пут. — Али за што сте ви то- | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/serbia__cyrillic__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c018 |
| `serbia--9caa9fc02f50cad6--s001-l0009` | бесмртни живот, — посећавајте у одређене дане св. божје | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/serbia__cyrillic__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c052 |
| `serbia--9f13a55215086cab--s000-l0012` | да ми се хрза не докундише, — па проста | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/serbia__cyrillic__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c060 |
| `bsb_poly1850--1c417ec1fdb5d021--s001-l0022` | ἐρωτῶντες, τί ἐποίησέ σοι; πῶς ἤνοιξέ σου τοὺς ὀφθαλμούς; | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/bsb_poly1850__poly1850__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c090 |
| `bsb_poly1850--2032df1e3e983f1d--s001-l0015` | ἐκείνου ὑπηρετῶ, τί σε δεῖ ἄλλον σατράπην καθιστάναι; ἢν | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/bsb_poly1850__poly1850__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c085 |
| `lekythos--793fb44fdc7e1aa6--s000-l0247` | μένα μάτια τοῦ ἀντρός της, ποὺ δὲν κα- | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/lekythos__poly1900__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c093 |
| `lekythos--e9f314aab488b65f--s001-l0199` | μάτι κάθε ποὺ θὰ στεναγωριόταν. Καὶ τὴ | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/lekythos__poly1900__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c098 |
| `ia_russian--03b43bc5289ad8ce--s003-l0028` | Камзолъ сей изъ того же голубаго гродетура, дли- | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/yer_adjudication/table.json`; adjudicated yer slots in the full Google label; c011 |
| `ia_russian--61f76a57b26f9b13--s003-l0009` | они этого хотятъ, а мы не хотимъ; потому что они | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/yer_adjudication/table.json`; adjudicated yer slots in the full Google label; c024 |
| `ia_russian--3fd32314d172e951--s006-l0010` | неромъ, да сразу и кончитъ всю музыку! | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/yer_adjudication/table.json`; adjudicated yer slots in the full Google label; c034 |
| `ia_russian--03b43bc5289ad8ce--s005-l0011` | „добрыхъ Твоихъ солдатъ на Левенгоуптской баталіи, когда | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/yer_adjudication/table.json`; adjudicated yer slots in the full Google label; c037 |
| `ia_russian--4ce4c0e3183ce075--s004-l0017` | ять кто будешъ, то онъ не почувствуетъ, | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/yer_adjudication/table.json`; adjudicated yer slots in the full Google label; c045 |
| `ia_russian--03b43bc5289ad8ce--s007-l0006` | силъ Константинъ Павловичъ, удивленный ея простотою, | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/yer_adjudication/table.json`; adjudicated yer slots in the full Google label; c049 |
| `kosmopolis--86098eebf5207e79--s004-l0016` | νεκροταφεῖο .. Αὔριο μὲ τὴ χαραυγὴ ερχόμαστε καὶ τὴν | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/kosmopolis__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c052 |
| `kosmopolis--ef37f6cfdd896488--s002-l0036` | Πάλε καταλάβαινε μιὰν ἐπιθυμία, ἔτσι, πὼς σἂ νὰ | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/kosmopolis__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c062 |
| `kosmopolis--ef37f6cfdd896488--s005-l0008` | τους. Ὁ στίχος του ἔχει μιὰ ξεχωριστὴ χάρη, μιὰ ἁπαλότητα, ἡ | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/kosmopolis__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c074 |
| `kosmopolis--3ccb484c8655e2ec--s004-l0015` | Μασσαλία 1928. ‹Patterns from a Grecian Loom | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/kosmopolis__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c029 |
| `kosmopolis--ef37f6cfdd896488--s002-l0041` | παστικὸ στὸ πρόσωπό του, ἕνα κομπαστικό — ἡ λέξη... | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/kosmopolis__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c030 |
| `kosmopolis--654bf46f6d37c4b4--s007-l0020` | Ο ΠΟΛΥ ΓΝΩΣΤΟΣ ἀλεξανδρινὸς καλλιτέχνης κ. Γ. Κεφαλλη- | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/kosmopolis__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c012 |
| `lekythos--e9f314aab488b65f--s001-l0335` | χωμάτινα τραπέζια ὅπου πίνανε τὸ «νέ- | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/lekythos__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c097 |
| `lekythos--9447d290d59a2411--s000-l0388` | τοῦνται μονάχα γνώσεις μετρικῆς, ἀλλὰ κ- | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/lekythos__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c062 |
| `lekythos--3bfc4a385d61b883--s000-l0106` | Ἡ κοντέσσα σώπαινε. Τὰ χείλη της | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/lekythos__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c041 |
| `lekythos--dd72392a3777225e--s000-l0264` | ρίμενε ὣς τὴν Κυριακή, καὶ τότε εἶπε, | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/lekythos__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c071 |
| `lekythos--dd72392a3777225e--s002-l0131` | Ἐλευθέρα Σκηνή : Ζαχαρία Παπαντω- | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/lekythos__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c074 |
| `lekythos--ff539dec2e1680a7--s000-l0214` | γανε τώρα τὸν πύργο—πρὶν ἀρχίσουν | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/lekythos__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c060 |
| `lekythos--1a3def6495932802--s001-l0262` | (*) Δραχμὲς ἀπάνω κάτω τριακόσιες εἴκοσι. | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/lekythos__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c093 |
| `lekythos--1a3def6495932802--s001-l0133` | τυῦ κόμματος γίνουνταν μὲ 5.000 κι' | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/lekythos__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c091 |
| `lekythos--0fc3672826ddd6b3--s000-l0033` | πραγματικὰ τόσο καλὸ αὐτὲς οἱ | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/lekythos__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c006 |
| `lekythos--1a3def6495932802--s000-l0144` | Καθόμουνα κι' ἔτρωγα ξερὸ φαΐ χωρὶς νὰ | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/lekythos__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c015 |
| `lekythos--456def1ccfc2283e--s002-l0041` | τὸ ποίημά του «Στὴν Πρωτομαγιὰ», ποὺ | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/lekythos__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c018 |
| `gazette_modern--c1b2194696b35bb5--s000-l0077` | 3. Νικολαος Πρέντας του Κωνσταντινου, γενν. το ετος 1911 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/gazette_modern__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c073 |
| `gazette_modern--5a173b5ea9cc9922--s000-l0083` | πίνακες προακτέων έτους 1984—85 και συμπλήρωσε ευθό- | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/gazette_modern__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c046 |
| `gazette_modern--b45c6f04968613c9--s000-l0041` | 7.128.941 | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/gazette_modern__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c071 |
| `gazette_modern--5ede709b65bee305--s000-l0098` | ΣΕΛΕΤΕ, που εκδόθηκε σύμφωνα με τις κείμενες διατά- | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/gazette_modern__b.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c097 |

Prefilled: 141. All other Printed fields are empty. Conflicting adjudications are left empty and recorded in `printed_conflicts`.

R0 / print-truth inventory: 0 exact line-id matches. These sets use other namespaces and include word/span truth or reference-only text; no inferred join or partial-line prefill.

## segmentation_failures

| Section | Kept | Added | Re-tagged | Removed |
|---|---:|---:|---:|---:|
| Two or more lines in one crop, label covers one  (8 of 1,400 C1 cards) | 8 | 0 | 8 | 0 |
| Crop shorter than the printed line  (4 of 1,400 C1 cards) | 4 | 0 | 4 | 0 |
| Neighbouring line ink inside the crop  (154 of 1,400 C1 cards) | 12 | 0 | 12 | 0 |
| Crop spans two table columns  (1 of 1,400 C1 cards) | 1 | 0 | 1 | 0 |
| Clipped at the edge  (14 of 1,400 C1 cards) | 13 | 0 | 13 | 0 |
| Vertical line stored rotated  (2.9% of Gazette modern rows, 20% of its headings) | 4 | 0 | 4 | 0 |
| SG2: printed rows with no admitted box (3 strip witnesses) | 0 | 3 | 0 | 0 |

Doc-id continuity: **42/42 kept**. Removed: none.

### Complete old-id continuity ledger

| Old doc id | Original group / section | Result |
|---|---|---|
| `gazette_modern--1f7db88d63c02afa--s000-l0287` | g_merged / g_merged | kept, re-tagged |
| `gazette_modern--0020420cfe156a73--s000-l0039` | g_merged / g_merged | kept, re-tagged |
| `gazette_modern--0020420cfe156a73--s000-l0138` | g_merged / g_merged | kept, re-tagged |
| `gazette_modern--0020420cfe156a73--s000-l0162` | g_merged / g_merged | kept, re-tagged |
| `gazette_modern--0020420cfe156a73--s000-l0228` | g_merged / g_merged | kept, re-tagged |
| `gazette_modern--5af16c5d518d2ebb--s000-l0128` | g_merged / g_merged | kept, re-tagged |
| `gazette_modern--0020420cfe156a73--s000-l0141` | g_merged / g_merged | kept, re-tagged |
| `gazette_modern--2e613d9290dd13d4--s000-l0209` | g_merged / g_merged | kept, re-tagged |
| `ia_poly1850--36dcee7ce4c29f8b--s003-l0110` | g_fragment / g_fragment | kept, re-tagged |
| `lekythos--793fb44fdc7e1aa6--s003-l0012` | g_fragment / g_fragment | kept, re-tagged |
| `lekythos--49c082ba27aa27da--s000-l0317` | g_fragment / g_fragment | kept, re-tagged |
| `nlg--6146c0455e0103d2--s001-l0006` | g_fragment / g_fragment | kept, re-tagged |
| `bsb_poly1850--e18cacecef3b4590--s005-l0076` | g_overrun / g_overrun | kept, re-tagged |
| `bsb_poly1850--e18cacecef3b4590--s007-l0061` | g_overrun / g_overrun | kept, re-tagged |
| `gazette_modern--cf61545b9c4093ec--s000-l0090` | g_overrun / g_overrun | kept, re-tagged |
| `gazette_modern--78abf3276f0df3f0--s000-l0080` | g_overrun / g_overrun | kept, re-tagged |
| `gazette_modern--902a98e0625d6436--s000-l0124` | g_overrun / g_overrun | kept, re-tagged |
| `gazette_modern--be6f8e70cd50bffb--s000-l0062` | g_overrun / g_overrun | kept, re-tagged |
| `gazette_modern--b6928cabb92b6656--s000-l0125` | g_overrun / g_overrun | kept, re-tagged |
| `gazette_modern--9aa572190ac3f790--s000-l0035` | g_overrun / g_overrun | kept, re-tagged |
| `gazette_modern--49b793056935d163--s000-l0112` | g_overrun / g_overrun | kept, re-tagged |
| `gazette_modern--621de52ab8573d81--s000-l0048` | g_overrun / g_overrun | kept, re-tagged |
| `gazette_modern--b66cffb760389957--s000-l0009` | g_overrun / g_overrun | kept, re-tagged |
| `gazette_modern--210af98945a5afbd--s000-l0031` | g_overrun / g_overrun | kept, re-tagged |
| `elstat--df38bce62200e7db--s000-l0191` | g_column / g_column | kept, re-tagged |
| `bsb_poly1850--e18cacecef3b4590--s005-l0077` | g_clipped / g_clipped | kept, re-tagged |
| `gazette_modern--73e4d3191f16b5e2--s000-l0026` | g_clipped / g_clipped | kept, re-tagged |
| `ia_poly1850--f806d3f10b2ecf9c--s003-l0050` | g_clipped / g_clipped | kept, re-tagged |
| `ia_poly1850--f806d3f10b2ecf9c--s004-l0102` | g_clipped / g_clipped | kept, re-tagged |
| `ia_poly1850--a89bd2c9bdb1ca6d--s005-l0083` | g_clipped / g_clipped | kept, re-tagged |
| `ia_poly1850--f806d3f10b2ecf9c--s001-l0070` | g_clipped / g_clipped | kept, re-tagged |
| `ia_russian--61f76a57b26f9b13--s004-l0002` | g_clipped / g_clipped | kept, re-tagged |
| `ia_russian--6cfc00f06e0f7241--s007-l0003` | g_clipped / g_clipped | kept, re-tagged |
| `lekythos--3bfc4a385d61b883--s001-l0194` | g_clipped / g_clipped | kept, re-tagged |
| `lekythos--49c082ba27aa27da--s002-l0081` | g_clipped / g_clipped | kept, re-tagged |
| `nlg--3d6bd7bd688acb61--s006-l0005` | g_clipped / g_clipped | kept, re-tagged |
| `nlg--1144074169f43992--s006-l0032` | g_clipped / g_clipped | kept, re-tagged |
| `nlg--7870403c3df244ea--s007-l0025` | g_clipped / g_clipped | kept, re-tagged |
| `gazette_modern--057ba91578d2becf--s000-l0155` | g_rotated / g_rotated | kept, re-tagged |
| `gazette_modern--057ba91578d2becf--s000-l0178` | g_rotated / g_rotated | kept, re-tagged |
| `gazette_modern--057ba91578d2becf--s000-l0184` | g_rotated / g_rotated | kept, re-tagged |
| `gazette_modern--057ba91578d2becf--s000-l0186` | g_rotated / g_rotated | kept, re-tagged |

### Added ids

- `37120de0c594-p000002-l0028` — g_missing_box
- `5bcf3381-p000024-l0010` — g_missing_box
- `808a6f56ea4d-p000002-l0050` — g_missing_box

### Printed prefills and sources

| Doc id | Printed | Source and method |
|---|---|---|
| `lekythos--793fb44fdc7e1aa6--s003-l0012` | καὶ θυμάρι. Εἶναι ἕνα πνευματικὸ | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/lekythos__poly1900__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c029 |
| `nlg--6146c0455e0103d2--s001-l0006` | ἡ τελευταία πρᾶξις· ἀφήσατε νὰ τελειώσῃ καὶ | `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__poly1850__a.jsonl`; exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded; c042 |

Prefilled: 2. All other Printed fields are empty. Conflicting adjudications are left empty and recorded in `printed_conflicts`.

R0 / print-truth inventory: 0 exact line-id matches. These sets use other namespaces and include word/span truth or reference-only text; no inferred join or partial-line prefill.

## SG2 scope

Three cards, one per existing SG2 strip, follow all original segmentation groups. Each uses the first identified missed row’s actual id, a native crop at its saved locator bounds, the archived raw Google label, Printed, tags, note, and the supplied strip. All eight missed rows remain visible across the three strips; only the three crop rows get note documents. Raw boxes exist on these witnesses: this is missing **admitted** boxes, not zero raw Google detections. Red locators are saved raw extents, not independently fitted row truth.

Sources: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/SG2.md`, `examples.jsonl`, `sg2_validation.json`, `sg2_pilot_selection.json`, `sg2-source-page_adjudication.jsonl`, and `sg2-01-strip.png` through `sg2-03-strip.png`.

The 501/2,624 (19.09%) pilot uses admitted boxes. The later 8.55% raw-box census uses another denominator and criterion. These are archived visual judgments, not new owner adjudication.

## Validation

Run `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/adjudicate -q`. The OS2 tests check exact rendering, baseline continuity, 14-class order, evidence tags, masked hashes, source-bound prefills, SG2 provenance, embedded image pixels and native ratios, no model names or uncertainty placeholders in owner-facing content, and offline operation. The superseded OS1 tests were replaced because they required the abandoned 10-class layout and a disabled SG2 group.

## OS3: Google-row mapping and current coordinator continuity

Recomputed C1 crop SHA-256 joins against W1 `features.jsonl` `crop_sha256`: 5,326 pairs, exactly equal to the coordinator map. Missing / extra / changed pairs: 0 / 0 / 0.

The builder replays `inputs/coordinator_build_sheets_v2.py` with the recomputed map and independently with the coordinator map; complete captured specs agree. Current coordinator continuity: A 133/133 and B 42/42, with identical document ids, original groups, and crops. Explicit coordinator result ids can alias the hash-selected id; checker evidence is attached to both only after verifying byte-identical native crops.

Google text uses `google_text`, then W1 feature text. Blank source cards and excluded sheet cards are listed in `artifacts/owner_sheets/v2/os3_mapping_audit.json`; blank Google rows fail validation. Empty source cards: 0; excluded sheet cards: 0; empty rendered Google rows: 0. Unmapped C1 cards: 549, listed in the same audit.

Re-rendered A 180 cards and B 45 cards, offline with no `.git` writes.

Validation: **35 passed** in 38.94s with `PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m pytest tests/adjudicate -q`. Full log: `artifacts/owner_sheets/v2/pytest.txt`; checksums: `artifacts/owner_sheets/v2/validation.json`.

OS3 READY: map pairs 5326 (= coordinator yes); empty Google rows 0; doc ids identical yes; cards A 180 B 45; tests 35 passed

## OS4: owner re-tags and card-level placement audit

Audited all 180 failure-mode cards and 45 segmentation cards. Owner re-tags: 4; additional audit re-tags: 14. All OS3 line ids and document ids, card order, crops, text, Printed values, notes, and original checker codes are identical. Only classification tags, placement and associated subsection metadata change. Exact OS3 inputs are retained under `inputs/os3_*.json`; the complete transition ledger is `artifacts/owner_sheets/v2/os4_retag_audit.json`.

The three IA cards were already under mark subsections in OS3, with a Mixed Greek + Latin class pill. That pill described the stratum, not a Latin fault; it is removed from these cards and replaced with their specific mark fault. Class sections remain intact. The table records the actual OS3 subsection, rather than inventing a former Latin fault tag.

The renderer supports one placement per note document. The NLG dash witness is placed under clipped edge in A, retains its clipped-edge placement in B, and carries a mark error tag in both. Dashes: **tag only, no track**; retained as tagged examples with no further work.

The audit rejects the Cyrillic р shortcut and checks mark direction on each side of the checker arrow. All six Serbian cards incorrectly grouped as yers and both pure Russian dash cards are listed below, along with reversed or unsupported mark subtype placements. All other cards have a placement supported by their own codes and detail; segmentation geometry and SG2 provenance remain unchanged.

| Card | Old tag | New tag | Evidence |
|---|---|---|---|
| `bsb_poly1850--d7db5a3b1eb289a3--s003-l0018` | grave written as acute | acute written as grave | δέ, → δὲ, |
| `ia_poly1850--a89bd2c9bdb1ca6d--s007-l0016` | mark misnamed | circumflex written as grave | ὧν → ὢν |
| `ia_poly1850--a89bd2c9bdb1ca6d--s005-l0038` | circumflex written as acute | circumflex written as diaeresis | Λαῖτοι → Λαϊτοι |
| `ia_poly1850--41e90f3ba967f920--s006-l0022` | circumflex written as acute | circumflex written as acute | θλῖψις → θλίψις |
| `ia_poly1850--adb0f3293921eb50--s006-l0016` | grave written as acute | acute written as grave | ἀστεῖά → ἀστεῖὰ |
| `ia_poly1850--29e9490734cc1653--s002-l0014` | grave written as acute | acute written as grave | δέ → δὲ |
| `ia_russian--3fd32314d172e951--s001-l0005` | Cyrillic faults: yer and dialogue punctuation (original coordinator group) | em dash dropped or hyphenated | разожгу—любо-дорого!—грозилъ → разожгу - любо-дорого! - грозилъ (em dashes → spaced hyphens) |
| `ia_russian--3fd32314d172e951--s002-l0006` | Cyrillic faults: yer and dialogue punctuation (original coordinator group) | em dash dropped or hyphenated | такихъ?—спросилъ → такихъ? - спросилъ |
| `nlg--3d6bd7bd688acb61--s000-l0025` | grave written as acute | mark misnamed | λέμβσυς → λέμβους; ἔβγαλἀν (breathing on 2nd α) → ἔβγαλὰν |
| `nlg--9aff599c7fffc574--s002-l0015` | iota subscript dropped | mark misnamed | τῂ → τῇ; Ἀνα- → Ανα- |
| `nlg--1144074169f43992--s006-l0032` | em dash dropped or hyphenated | clipped at the edge; mark error | καθὼς → καθώς; left edge: clipped dash stroke before κοιμᾶσαι → (none) |
| `nlg--1144074169f43992--s002-l0018` | circumflex written as acute | circumflex written as diaeresis | γυναῖκά → γυναϊκά |
| `serbia--27b182bf4116728f--s001-l0026` | hard sign ъ flattened to ь | mark dropped | страдални̑ка → страдалника; мучени̑ка → мученика (inverted-breve accent over и omitted) |
| `serbia--42fedee06e6cb85a--s000-l0022` | hard sign ъ flattened to ь | mark dropped | срино̂ → срино |
| `serbia--27b182bf4116728f--s001-l0002` | hard sign ъ flattened to ь | mark misnamed | Бе̄лу → Бёлу; Гра̑ду → Граду |
| `serbia--27b182bf4116728f--s001-l0035` | hard sign ъ flattened to ь | em dash dropped or hyphenated | Србије — с → Србије с |
| `serbia--8fd9a36edc06b7f9--s001-l0004` | hard sign ъ flattened to ь | em dash dropped or hyphenated | стојаније — разлике → стојаније разлике |
| `serbia--fc66165678b402fe--s001-l0032` | hard sign ъ flattened to ь | em dash dropped or hyphenated | Бог — заврши → Бог заврши |

OS4 validation: **41 passed** in `tests/adjudicate` (full suite); the focused owner-sheet/runtime run also passed 18 tests. Both HTML artifacts match the renderer exactly. Tests verify every OS3 line/document id and all non-classification card fields against the saved OS3 inputs. No network calls or `.git` writes.

The Mac has mixed ARM/Intel Python packages. The successful full-suite command uses the installed Intel packages first, without installing or changing packages:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 arch -x86_64 python3 -s -c 'import sys; sys.path.append("/Users/foivoskarounos-zamparloukos/Library/Python/3.11/lib/python/site-packages"); import pytest; raise SystemExit(pytest.main(["tests/adjudicate", "-q"]))'
```

## OS5: What moved in R2a (not adopted)

Added one final group with five held-out slot witnesses. All 180 existing cards, document ids, groups and sections are unchanged. The five new note ids use `line_id:sN`, preserving the reader-errors slot identity. No network calls, model runs, or `.git` writes.

Tuples were verified against `greek-ocr-toolkit-spellcheck-r2prep/docs/labelfix/spellcheck/R2/evidence/r2a/r2rb2_paired_slots.json` and matching entries in `r2rb2_owner_regressions.json`; the last card is a named owner witness. Tuple order and indexes come from `r1_common.HEADS`: breathing, accent, dialytika, subscript.

Native full-line crops and slot geometry come from the R1 `score_3678928_K1c_vsS6/A_mapped_lines.jsonl.gz`, following `R2_evidence/page_builders/build_r1a_errors.py`. Saved detections are outlined in green (above/apostrophe), blue (below), and grey (attached); the selected letter has a red full-height outline. Google words use the same archived seed-0 labels and token mapping. Printed uses the R1 truth word with the verified slot truth applied; Before and After change only that letter’s marks. All source paths, geometry, detections and tuples are retained per card.

| Seed | Note document | Truth / before | After | Change |
|---|---|---|---|---|
| 16 | `384c3f89-p000053-l0021:s8` | `[0, 0, 0, 0]` | `[0, 0, 0, 1]` | subscript invented |
| 17 | `177b717d-p000054-l0004:s4` | `[1, 3, 0, 0]` | `[1, 3, 0, 1]` | subscript invented |
| 17 | `177b717d-p000017-l0012:s24` | `[0, 3, 0, 0]` | `[0, 3, 1, 0]` | dialytika invented |
| 18 | `22fda82b-p000063-l0039:s10` | `[0, 3, 0, 1]` | `[0, 3, 0, 0]` | subscript dropped |
| 18 | `602cc72e-p000167-l0027:s10` | `[0, 2, 0, 0]` | `[1, 2, 0, 0]` | breathing added; owner witness |

Rebuild OS5 only: `python -m scripts.review.build_owner_sheets_v2 --os5-only`. The full builder also appends OS5 after OS4.

Local source availability: W1 crop files were missing during OS5. `scripts/review/recover_owner_sheet_crops.py` preserved the already embedded rasters under `artifacts/owner_sheets/v2/recovered_crops/`, with source-path and SHA-256 entries in `index.json`. The renderer uses these only when the original path is absent. Coordinator replay resolves the same cached paths; duplicate-crop evidence uses the archived feature crop SHA-256 when original PNG bytes are unavailable. Existing card records retain their source paths. The segmentation HTML checksum is unchanged.

OS5 validation: **44 passed** in 56.54s (`tests/adjudicate`); log: `artifacts/owner_sheets/v2/os5_pytest.txt`; receipt: `artifacts/owner_sheets/v2/os5_validation.json`. Exact OS4 replay confirms all 180 original cards and all original groups and sections unchanged. All 271 preserved raster checksums verified. Five native highlighted crops visually inspected.

OS5 READY: group added 5 cards; existing doc ids identical yes; tests 44 passed; html sha 5b595b66692c
