#!/bin/bash
# After an edit to a source file: run the fast check and hand errors back to Claude (exit 2).
# Adapt the file pattern and CHECK to the repo; keep it under a few seconds.
CHECK="npx --no-install tsc --noEmit"
input=$(cat)
file=$(echo "$input" | jq -r '.tool_input.file_path // empty')
case "$file" in *.ts|*.tsx) ;; *) exit 0 ;; esac
cd "$CLAUDE_PROJECT_DIR" || exit 0
[ -d node_modules ] || exit 0
out=$($CHECK 2>&1)
if [ $? -ne 0 ]; then
  echo "Check failed after editing $file:" >&2
  echo "$out" | head -30 >&2
  exit 2
fi
exit 0
