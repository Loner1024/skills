#!/usr/bin/env bash
# Sync skills/ from this repository into the maintainer's Amp personal skills repository.
#
# Why this exists: Amp serves personal skills from its own hosted Git repository
# (https://ampcode.com/docs/customize/skills), so a change published here is not live in Amp until
# it is copied there. This script is that copy, in one deterministic step.
#
#   scripts/sync-to-amp-skills.sh              sync, commit, and push when something changed
#   scripts/sync-to-amp-skills.sh --dry-run    report what would change, commit nothing
#
# Behaviour:
#   - the source is origin/main, never this checkout: a checkout can be behind (another orb
#     pushed), and copying a stale tree would revert newer content in the personal repository;
#   - text files only: Amp serves no binaries, so *.png and friends stay here (the example renders);
#   - add and update only: a skill that exists only in the personal repository is reported, never
#     deleted, so a skill created in Amp by hand survives a sync;
#   - aborts rather than discarding uncommitted work in the personal skills clone.
#
# Requires the `amp` CLI signed in (or AMP_API_KEY set for CI). The clone path can be overridden
# with AMP_SKILLS_REPO_DIR.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CACHE_DIR="${AMP_SKILLS_REPO_DIR:-$HOME/.cache/amp/repositories/ampcode.com-user-skills}"
DRY_RUN=""
[ "${1:-}" = "--dry-run" ] && DRY_RUN=1

command -v amp >/dev/null 2>&1 || { echo "amp CLI not found; see https://ampcode.com/docs/cli" >&2; exit 3; }

# Read the published revision, not the working tree.
git -C "$REPO_ROOT" fetch --quiet origin main
SOURCE_REV_FULL="$(git -C "$REPO_ROOT" rev-parse origin/main)" || {
  echo "cannot resolve origin/main in $REPO_ROOT" >&2; exit 3; }
SOURCE_REV="$(git -C "$REPO_ROOT" rev-parse --short origin/main)"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/amp-skills-sync.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
git -C "$REPO_ROOT" archive "$SOURCE_REV_FULL" skills | tar -xf - -C "$WORK"
SKILLS_DIR="$WORK/skills"
[ -d "$SKILLS_DIR" ] || { echo "origin/main carries no skills/ directory" >&2; exit 3; }

# Reuse the canonical clone when it exists (amp clone also installs the credential helper the later
# push needs), otherwise clone it.
if [ -d "$CACHE_DIR/.git" ]; then
  git -C "$CACHE_DIR" fetch --quiet origin main
  git -C "$CACHE_DIR" checkout --quiet main
else
  mkdir -p "$(dirname "$CACHE_DIR")"
  amp clone user-skills "$CACHE_DIR" >/dev/null
fi

if [ -n "$(git -C "$CACHE_DIR" status --porcelain)" ]; then
  echo "the personal skills clone has uncommitted changes; commit or discard them first:" >&2
  git -C "$CACHE_DIR" status --short >&2
  exit 1
fi
git -C "$CACHE_DIR" merge --quiet --ff-only origin/main

# Copy each skill directory, text files only. The exclusion list is extensions, because a hosted
# skill that contains one binary file is not served at all.
BINARY='! -name *.png ! -name *.jpg ! -name *.jpeg ! -name *.gif ! -name *.webp ! -name *.ico
        ! -name *.pdf ! -name *.zip ! -name *.gz ! -name *.woff ! -name *.woff2 ! -name *.ttf
        ! -name *.otf ! -name *.mp4 ! -name *.mov ! -name *.webm ! -name *.pyc'
for dir in "$SKILLS_DIR"/*/; do
  name="$(basename "$dir")"
  [ -f "$dir/SKILL.md" ] || continue
  mkdir -p "$CACHE_DIR/$name"
  # shellcheck disable=SC2086  # $BINARY is a list of find predicates, on purpose
  (cd "$dir" && find . -type f $BINARY -print0 | tar --null -cf - -T -) | tar -xf - -C "$CACHE_DIR/$name"
done

# Report, never delete: a skill that lives only in the personal repository stays.
for dir in "$CACHE_DIR"/*/; do
  name="$(basename "$dir")"
  [ -d "$SKILLS_DIR/$name" ] || echo "note: $name exists only in the personal skills repository; left alone"
done

cd "$CACHE_DIR"
if [ -z "$(git status --porcelain)" ]; then
  echo "up to date: origin/main and the personal skills repository agree"
  exit 0
fi

echo "--- changes ---"
git status --short
if [ -n "$DRY_RUN" ]; then
  git checkout --quiet -- . && git clean --quiet -fd
  echo "(dry run: nothing committed)"
  exit 0
fi

SOURCE_REV="$(git -C "$REPO_ROOT" rev-parse --short HEAD 2>/dev/null || echo unknown)"
git add -A
git commit --quiet -m "Sync skills from Loner1024/skills@$SOURCE_REV"
git push --quiet origin main
echo "pushed: skills from Loner1024/skills@$SOURCE_REV are live in the personal skills repository"
