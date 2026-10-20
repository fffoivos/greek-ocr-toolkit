# Prompting-guide notes for the Sol reader prompts (read 17 Oct 2026, 12:2x Athens)

## Sources read
1. OpenAI, **Using GPT-6** (https://developers.openai.com/api/docs/guides/latest-model) and its GPT-6 Astra page
   (https://developers.openai.com/api/docs/guides/latest-model/gpt-6-astra.md). Both cover the Astra, 6.1 Sol and Luna family.
2. OpenAI cookbook, **Codex Prompting Guide** (https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide).
3. OpenAI, **Images and vision** (https://developers.openai.com/api/docs/guides/images-vision).

The official pages were fetched. The third-party summaries that came up in search were not used.

## What the guides say that bears on blind reading

| Guide point | Applied in the prompts |
|---|---|
| Infer intent, persist until the goal is complete, and avoid unnecessary clarifying questions. The family asks more questions than earlier models. (1) For evals, prompt for a non-interactive mode. (2) | A header says the run is non-interactive, asks no questions, and finishes in this turn. |
| Lean prompts: state each instruction once, and audit context for conflicting instructions. The model is more sensitive to context. (1) | Each protocol is kept verbatim, because comparability with Opus is the experiment. The one conflict was removed (yer "absolute path" vs relative packs). `project_doc_max_bytes=0`, so no AGENTS.md reaches the reader. |
| Clear completion criteria; run checks once, and repeat them only when something changed. (1) | Each prompt adds a "Done when" block: count, order and coverage, checked once by a command. |
| Default effort is `medium`; `none` is not supported. (1) | Reading runs use `model_reasoning_effort=medium`. |
| Maximise parallelism and batch reads; do not read files one by one. (2) | View about 5–10 images per tool call. This also cuts the per-turn re-send of the context, which made the tool probe cost 78k input tokens for 2 cards. |
| Images come in through the `view_image` tool, which attaches a local file. (2) | "Read tool" → `view_image`. |
| Final answers should be very concise. (2) | The protocol's own short summary reply is kept. "Plain text" is added. |
| Expose only the tools the task needs. (1) | No network, no web search (`web_search="disabled"`), no multi-agent, no plugins or apps. Writes are limited to the reader folder. |
| Enlarge small text to improve readability; use `original` detail for OCR. Non-Latin alphabets may be weaker. (3) | The protocol's ImageMagick zoom is kept and made explicit. Codex does not expose a `detail` setting in exec mode. The non-Latin caveat is a stated risk for Greek polytonic and old Cyrillic, and is measured by this experiment. |

## Not applied
- **Delegation to subagents** (1): the task needs one independent reader per context, so `features.multi_agent=false`.
- **Writing-style / banned-phrase list** (1): reader output is JSON; there is no prose to style.
- **Planning tool** (2): the guide says to skip it for straightforward tasks, and the prompts do not ask for a plan.
