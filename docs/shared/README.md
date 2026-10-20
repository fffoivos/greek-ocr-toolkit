# Shared infrastructure

Navigation: [documentation index](DOCUMENTATION_INDEX.md), [repository organization](REPOSITORY_ORGANIZATION.md), and [web rendering](WEB_RENDER.md).

These components support both [OCR development](../A_ocr_development/README.md) and [training-data creation](../B_training_data/README.md). Their code and import paths stay in their existing homes.

| Surface | Code and documentation |
|---|---|
| Deploy | `greekocr/deploy/`: environment plans, explicit worker operations and the Docling plugin; contracts and examples in the [API](../API.md). |
| Operations | `greekocr/ops/` and [operational records](../records/ops/): atomic receipts, hashing, injected credentials, rate locks and bounded liveness. |
| Verification | `greekocr/verify/`, [verification guide](../VERIFY.md), [validation](../records/verify_20261008/VALIDATION.md) and [verification evidence](../verify/). |
| Types and contracts | `greekocr/types.py`; [STANDARD.md](../STANDARD.md) defines the typed API, provenance and testing requirements. |
| CLI | `greekocr/cli.py`; use the [repository setup](../../README.md#toolkit-setup) and [API reference](../API.md). |
| Vendor custody | `greekocr/_vendor/`, unchanged [origins](../origins/), and [INVENTORY.md](../INVENTORY.md). Origin files retain exact bytes; relocation does not rewrite historical hashes or receipts. |
| Clariden scripts | `scripts/harvest/clariden/`, `scripts/labelfix/clariden/`; the [B.c runbook](../B_training_data/c_pipeline/RUNBOOK_CLARIDEN.md) distinguishes builds, job kinds and verify → smoke → full boundaries. The live [deployment package](../harvest/seg_census/package/) remains in place. |

The [records index](../records/INDEX.md) separates historical track evidence from these shared services. Commands in runbooks are operational references and do not themselves authorise a launch.
