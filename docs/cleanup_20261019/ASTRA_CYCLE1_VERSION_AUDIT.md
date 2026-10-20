# Current documentation version audit

Scope: every Markdown, Mermaid and HTML file in `docs/A_ocr_development` and `docs/B_training_data`, plus root README and AGENTS. [Complete version-like token inventory](ASTRA_CYCLE1_VERSION_STRINGS.tsv) records file/line and namespace; numeric thresholds, scores, costs, package/model and CLI versions are not B tool identities. Base64 bitmap payloads are excluded from text scanning.

Authority: `greekocr/harvest/line_pipeline.py` (`PIPELINE_VERSION=0.3.2`) and `docs/harvest/line_pipeline/tool_versions.json`: segmentation **0.13**, label **0.9-s5**, common band **0.30–2.00**; numerics **0.3**, census **0.7**, composer **0.3**, content gate/final eligibility **0.3**; inventory/dashes **0.1**, polytonic **0.7**, Cyrillic **0.3**, content repair **0.2**. Component hashes identify exact source patches, not accuracy.

| Documents checked | Disposition |
|---|---|
| Root README / AGENTS; A README / MODEL_GENERATIONS / RECOGNISER_AND_TRAINING / NEXT_GEN_R8; B README / d_review README | Current B cross-references synchronized. Package 0.1.0, model R7/R8 and historical scanner/CLI releases remain separate namespaces. Baseline byte equality corrected; executable AST equality checked separately. |
| B.b README / SEGMENTATION_FILTER / NUMERICS_N1 / CONTENT_GATE | Current version, band and numeric-adjacency integration corrected. S1–S4 and older numeric releases remain labelled history. Saved score denominators and SEG10 false-negative increases retained. |
| B.c README / RUNBOOK / Mermaid graph; B.a SOURCES | Current pipeline 0.3.2, scope evidence and configured held-out union described; obsolete pre-SEG10 integration limitations labelled historical. Census04 0.8/gate 0.2 remains a distinct frozen package. |
| POLYTONIC_SF7 / CYRILLIC_RU1 / DASHES / LABEL_QUALITY_BENCHMARK / CONTENT_GATE histories; d_review PUBLISHING and demo HTML | Current identities match the manifest; tool histories, saved sheet versions and fitted-score reports retain original labels. Demo history is explicitly identified in d_review README without altering immutable HTML evidence. |
| A reference guides; B.a reader guides; remaining B.d protocols | Their numerical values are model/recipe/API/algorithm parameters, historic runs or sheet protocol settings, not competing current B tool identities. No blanket replacement applied. |

Both canonical and compatibility Mermaid graphs are synchronized. The compatibility README already contains PIPE032's current version table and release-scope semantics; it is preserved. The historical `docs/records` tree and source-capture packages retain their original versions.
