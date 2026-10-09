#!/bin/bash
# Before Claude ends a turn with uncommitted changes: run the tests.
# A failure sends Claude back to fix it, once per turn (stop_hook_active guard).
# Adapt TESTS to the repo.
TESTS="npm test --silent"
input=$(cat)
[ "$(echo "$input" | jq -r '.stop_hook_active')" = "true" ] && exit 0
cd "$CLAUDE_PROJECT_DIR" || exit 0
[ -d node_modules ] || exit 0
[ -z "$( { git diff --name-only HEAD; git ls-files --others --exclude-standard; } 2>/dev/null )" ] && exit 0
out=$($TESTS 2>&1)
if [ $? -ne 0 ]; then
  echo "Tests fail with the current changes. Fix them before finishing:" >&2
  echo "$out" | tail -30 >&2
  exit 2
fi
exit 0
