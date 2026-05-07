#!/usr/bin/env bash
# Installs git hooks from scripts/hooks/ into .git/hooks/.
# Run once per fresh clone: ./scripts/install-hooks.sh

set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
src_dir="$repo_root/scripts/hooks"
dst_dir="$repo_root/.git/hooks"

for src in "$src_dir"/*; do
  name="$(basename "$src")"
  cp "$src" "$dst_dir/$name"
  chmod +x "$dst_dir/$name"
  echo "installed $name"
done
