
# Tool-use addendum
Use only relative paths inside your current reader folder. In every view_image call, write the complete relative path as a literal string, for example "zoom/card01-v1.png". Batch several explicit calls together. Do not build file paths in loops, template strings, concatenations, pwd expressions, or store/load expressions.

Create enlargements only inside ./zoom/. Give every new image a fresh filename. Never overwrite or delete an image after viewing it; preserve all zoom versions until the run is complete. Keep image-generation commands separate from commands that read or write answers.jsonl.

These instructions govern tool use only. Apply the label-check protocol above unchanged.
