#!/usr/bin/env bash
# Cross-platform Python launcher for AI log hooks.
# Tries the project's .venv first, then python3 / python / py -3 on PATH,
# then standard Windows install locations. Hooks must never block the AI
# tool, so if no Python is found the script exits 0 silently.
# Designed to be called as: bash scripts/_pyrun.sh <script> [args...]
set -u

# Force UTF-8 stdout/stderr so emoji / non-ASCII in log messages don't crash
# the cp1252 console on Windows (Python raises UnicodeEncodeError otherwise).
export PYTHONIOENCODING=utf-8
export PYTHONUTF8=1

# Detect repo root: parent of this script's directory.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 1) Prefer the project's .venv. Git Bash launched by git hooks often
#    inherits a stripped PATH where neither the venv nor a real Python is
#    visible, and `python` resolves to the Microsoft Store alias.
for cand in \
  "$REPO_ROOT/.venv/Scripts/python.exe" \
  "$REPO_ROOT/.venv/bin/python3" \
  "$REPO_ROOT/.venv/bin/python"; do
  if [ -x "$cand" ]; then PY="$cand"; break; fi
done

# 2) Fall back to PATH lookup.
if [ -z "${PY-}" ]; then
  if command -v python3 >/dev/null 2>&1; then
    PY=python3
  elif command -v python >/dev/null 2>&1; then
    PY=python
  elif command -v py >/dev/null 2>&1; then
    PY="py -3"
  else
    # 3) Probe standard Windows install locations.
    PY=""
    shopt -s nullglob 2>/dev/null || true
    for cand in \
      /c/Users/*/AppData/Local/Programs/Python/Python*/python.exe \
      "/c/Program Files/Python"*/python.exe \
      "/c/Program Files (x86)/Python"*/python.exe \
      /c/Python*/python.exe; do
      if [ -x "$cand" ]; then PY="$cand"; break; fi
    done
    shopt -u nullglob 2>/dev/null || true
    [ -n "$PY" ] || exit 0
  fi
fi

# shellcheck disable=SC2086
exec $PY "$@"
