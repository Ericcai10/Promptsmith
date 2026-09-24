#!/usr/bin/env bash
# Promptsmith installer (macOS / Linux / Git Bash)
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="${1:-all}"   # all | claude | codex

if [[ "$TARGET" == "all" || "$TARGET" == "claude" ]]; then
  mkdir -p "$HOME/.claude/commands"
  cp "$DIR/commands/claude/promptsmith.md" "$HOME/.claude/commands/promptsmith.md"
  echo "✔ Claude Code: /promptsmith installed -> ~/.claude/commands/promptsmith.md"
fi
if [[ "$TARGET" == "all" || "$TARGET" == "codex" ]]; then
  CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
  mkdir -p "$CODEX_HOME/prompts"
  cp "$DIR/commands/codex/promptsmith.md" "$CODEX_HOME/prompts/promptsmith.md"
  echo "✔ Codex CLI: /prompts:promptsmith installed -> $CODEX_HOME/prompts/promptsmith.md"
fi
echo "Restart your CLI session to pick up the new command."
