#!/usr/bin/env bash
set -euo pipefail
tag=$(gh api repos/robbietilton/Compositor/releases/latest --jq .tag_name)
[[ "$tag" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]
branch="sync/upstream-$tag"
git remote add upstream https://github.com/robbietilton/Compositor.git
git fetch upstream "refs/tags/$tag:refs/tags/$tag"
if git merge-base --is-ancestor "$tag" HEAD; then
  echo 'Latest release is already incorporated.'
  exit 0
fi
# A network failure must fail the run, rather than look like a missing branch.
existing=$(git ls-remote origin "refs/heads/$branch")
git config user.name github-actions[bot]
git config user.email 41898282+github-actions[bot]@users.noreply.github.com
if [[ -n "$existing" ]]; then
  git fetch origin "refs/heads/$branch"
  git checkout -b "$branch" FETCH_HEAD
  git merge-base --is-ancestor "$tag" HEAD
else
  git checkout -b "$branch"
  if ! git merge --no-edit "$tag"; then
    git merge --abort
    echo "Merge conflicts for $tag; manual port required." >> "${GITHUB_STEP_SUMMARY:-/dev/stderr}"
    exit 1
  fi
fi
python3 scripts/generate-localization.py
python3 scripts/audit-localization.py
git add Compositor/Resources
git diff --cached --quiet || git commit -m "Regenerate Chinese resources for $tag"
git push origin "$branch"
# GITHUB_TOKEN pushes and PRs do not trigger normal push/PR workflow runs.
# Dispatch both builds and upstream tests explicitly, including retries after interruption.
gh workflow run chinese.yml --ref "$branch"
gh workflow run verify.yml --ref "$branch"
pr=$(gh pr list --base zh-Hans --head "$branch" --state open --json number --jq '.[0].number // empty')
if [[ -z "$pr" ]]; then
  gh pr create --draft --base zh-Hans --head "$branch" \
    --title "Review Chinese support for upstream $tag" \
    --body 'Upstream release merged. Require successful Chinese build AND Verify runs on this branch head; review dynamic labels, secondary menus, and project round trips before merging. No automatic release or app replacement is performed.'
fi
