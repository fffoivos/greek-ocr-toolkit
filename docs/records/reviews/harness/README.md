# Launcher records

These are byte-identical scratchpad copies. Neither launcher was executed.

- `run_wt_medium_git.sh`: explicit writable roots; failed because Codex still kept `.git` read-only.
- `run_wt_medium_gitfull.sh`: `danger-full-access`; NOT used, blocked by this session's permission policy. Record only.

Both preserve their original network argument and search setting; these are historical records, not merge commands.

Baseline: `/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/logs/run_wt.sh`. Exact diffs against that shared copy:

```diff
--- shared/run_wt.sh
+++ run_wt_medium_git.sh
@@ -8,8 +8,8 @@
 if [ "$ANEMI" = anemi ]; then export ANEMI_USER="$(security find-generic-password -a "$USER" -s codex-anemi-username -w)"; export ANEMI_PASS="$(security find-generic-password -a "$USER" -s codex-anemi-password -w)"; fi
 for i in 1 2 3 4 5 6 7 8; do
   BEFORE=$(date +%s); echo "[$(date '+%H:%M:%S')] $T START attempt $i model=$MODEL net=$NETV brief=$BRIEF"
-  codex exec -m "$MODEL" -c "model_reasoning_effort=xhigh" -c approval_policy=never -c project_doc_max_bytes=0 -c features.multi_agent=false \
-    -c features.remote_plugin=false -c features.apps=false -c sandbox_workspace_write.network_access=$NETV -c 'web_search="live"' \
+  codex exec -m "$MODEL" -c "model_reasoning_effort=medium" -c approval_policy=never -c project_doc_max_bytes=0 -c features.multi_agent=false \
+    -c features.remote_plugin=false -c features.apps=false -c sandbox_workspace_write.network_access=$NETV -c 'sandbox_workspace_write.writable_roots=["/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.git","/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/merge_rehearsal"]' -c 'web_search="live"' \
     --sandbox workspace-write --skip-git-repo-check -C "$R" -o "$OUT" - < "$R/docs/briefs/$BRIEF" > "$LOG" 2>&1
   RC=$?
   if grep -q "429 Too Many Requests" "$LOG"; then echo "[$(date '+%H:%M:%S')] $T 429; waiting 5 min"; sleep 300; continue; fi
```

```diff
--- shared/run_wt.sh
+++ run_wt_medium_gitfull.sh
@@ -8,9 +8,9 @@
 if [ "$ANEMI" = anemi ]; then export ANEMI_USER="$(security find-generic-password -a "$USER" -s codex-anemi-username -w)"; export ANEMI_PASS="$(security find-generic-password -a "$USER" -s codex-anemi-password -w)"; fi
 for i in 1 2 3 4 5 6 7 8; do
   BEFORE=$(date +%s); echo "[$(date '+%H:%M:%S')] $T START attempt $i model=$MODEL net=$NETV brief=$BRIEF"
-  codex exec -m "$MODEL" -c "model_reasoning_effort=xhigh" -c approval_policy=never -c project_doc_max_bytes=0 -c features.multi_agent=false \
+  codex exec -m "$MODEL" -c "model_reasoning_effort=medium" -c approval_policy=never -c project_doc_max_bytes=0 -c features.multi_agent=false \
     -c features.remote_plugin=false -c features.apps=false -c sandbox_workspace_write.network_access=$NETV -c 'web_search="live"' \
-    --sandbox workspace-write --skip-git-repo-check -C "$R" -o "$OUT" - < "$R/docs/briefs/$BRIEF" > "$LOG" 2>&1
+    --sandbox danger-full-access --skip-git-repo-check -C "$R" -o "$OUT" - < "$R/docs/briefs/$BRIEF" > "$LOG" 2>&1
   RC=$?
   if grep -q "429 Too Many Requests" "$LOG"; then echo "[$(date '+%H:%M:%S')] $T 429; waiting 5 min"; sleep 300; continue; fi
   SID=$(LC_ALL=C sed $'s/\x1b\\[[0-9;]*m//g' "$LOG" | grep -m1 -oE 'session id: [0-9a-f-]+' | awk '{print $3}')
```
