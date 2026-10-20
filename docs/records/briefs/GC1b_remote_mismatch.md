# GC1b: fix the sf7 remote file mismatch (gpt-6.1-sol, medium; network ON for Clariden only; no .git writes; NEVER submit)

The coordinator's verify_deploy (`docs/records/labelfix/spellcheck/SF7_evidence/VERIFY_CMD.sh`, commit 26d64e8a6+) failed:
`remote mismatch: scripts/labelfix/clariden/l1r_recompose_ext.py`.
- Local, committed and `SF7_DEPLOY_SHA256.txt` all agree: 33c40cb3…f6730893.
- The copy under `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_sf7_20261017` differs.

**Do:**
1. Read the remote file's sha and mtime, and diff it against local (read-only first). Report what it is and why it differs: a
   stale deploy, an edit after deploy, or a symlink into a shared root.
2. Re-rsync ONLY that file from the committed local copy.
3. Re-check the remote sha of ALL 367 files against `SF7_DEPLOY_SHA256.txt`.
4. Run `sbatch --test-only` again.
5. If anything else differs, STOP.

Never refresh the cert.

Last line: `GC1b READY: cause <...>; remote sha <n>/<n>; test-only ok`.
