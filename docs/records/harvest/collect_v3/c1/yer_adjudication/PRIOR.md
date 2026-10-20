You are an expert in Russian historical orthography (pre-1918, before the reform that removed word-final ъ). Each item is one line of Russian text in which some word-final letters are hidden as ⟦1⟧, ⟦2⟧, … Each hidden letter was either ъ or ь.

For each hidden slot, using only spelling, morphology and context (there is no image), say which completions give a valid word form in pre-1918 orthography in this context:
- "ъ_only": only the ъ form is a valid word here (for example Камзол⟦1⟧ → Камзолъ; Камзоль is not a word);
- "ь_only": only the ь form is valid (for example мат⟦1⟧ meaning mother → мать);
- "both": both are valid forms and the context does not settle it (for example потужит⟦1⟧: потужитъ, 3rd person, vs потужить, infinitive), with the reading you consider more likely given the context;
- "neither": neither gives a word (the line may be misread).

Input: ITEMS, a JSONL file with `item_id`, `masked_text`, `slots`. Output: write one JSON object per item to OUT (Write tool; overwrite):

{"item_id":"a001","slots":{"1":{"prior":"ъ_only","word":"Камзолъ"},"2":{"prior":"both","likelier":"ъ","why":"3rd person after subject"}}}

Then reply with the counts of ъ_only, ь_only, both and neither. Open only ITEMS; never open any other file.
