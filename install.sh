#!/usr/bin/env bash
#
# semantic-audio-loom installer
#
# 音声素材エンジン（semantic-audio-loom）の facade スキルを Claude Code の検出場所へ
# インストールする。スキルは1つ（skills/semantic-audio-loom）。
#
# Usage:
#   ./install.sh            # Global: ~/.claude/skills/（どのプロジェクトからも呼べる）
#   ./install.sh --local    # Project: .claude/skills/（このリポジトリのみ）
#   ./install.sh --uninstall
#
# インストールは symlink：正本は ./skills/ のまま。リポジトリへの編集が即反映される。
#
# 注意: semantic-audio-loom はサブエージェントを持たない（声の生成は CLI で行うため
# agents/ は不要）。facade スキルはワークフロー（参照音声→キャラ→演技→生成）を案内し、
# 実際の合成は本リポジトリの bin/ と Tsukasa_Speech（~5GB・外部）で行う。

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$REPO_DIR/skills/semantic-audio-loom"

MODE="global"
ACTION="install"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --local)    MODE="local" ;;
    --global)   MODE="global" ;;
    --uninstall) ACTION="uninstall" ;;
    -h|--help)
      echo "Usage: ./install.sh [--local|--global] [--uninstall]"
      echo ""
      echo "  --local      Install to .claude/ (this project only)"
      echo "  --global     Install to ~/.claude/ (default; callable from anywhere)"
      echo "  --uninstall  Remove the installed skill (default: global target)"
      exit 0
      ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
  shift
done

if [[ "$MODE" == "local" ]]; then
  TARGET_DIR="$REPO_DIR/.claude/skills"
else
  TARGET_DIR="$HOME/.claude/skills"
fi

NAME="semantic-audio-loom"
TARGET="$TARGET_DIR/$NAME"

if [[ "$ACTION" == "uninstall" ]]; then
  echo "==> Uninstalling $NAME from: $TARGET_DIR"
  if [[ -L "$TARGET" || -e "$TARGET" ]]; then
    rm -rf "$TARGET"
    echo "    ✓ removed $NAME"
  else
    echo "    (not installed)"
  fi
  exit 0
fi

echo "==> Installing $NAME to: $TARGET_DIR"
mkdir -p "$TARGET_DIR"
rm -rf "$TARGET"              # 前回のインストール（symlink かファイル）を除去
ln -s "$SKILL_DIR" "$TARGET"
echo "    ✓ skill $NAME"

if [[ -f "$TARGET/SKILL.md" ]]; then
  echo ""
  echo "==> Done."
  echo "    Callable as: /semantic-audio-loom"
  echo ""
  echo "    実際の音声合成は本リポジトリの bin/ で行う（Tsukasa_Speech が必要）。"
  echo "    Note: restart Claude Code or run /skills once to reload the listing."
else
  echo "    ✗ broken: $TARGET"
  exit 1
fi
