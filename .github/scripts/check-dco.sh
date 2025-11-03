#!/bin/bash

# DCO Verification Script
# Checks all commits in a PR or push for DCO sign-off (Signed-off-by line)

set -e

echo "🔍 Checking DCO sign-off for commits..."

# Get the base and head commits
if [ "$GITHUB_EVENT_NAME" == "pull_request" ]; then
  if [ -n "$GITHUB_BASE_SHA" ] && [ -n "$GITHUB_HEAD_SHA" ]; then
    BASE_SHA="$GITHUB_BASE_SHA"
    HEAD_SHA="$GITHUB_HEAD_SHA"
    echo "PR: $GITHUB_PR_NUMBER - Checking commits from $BASE_SHA to $HEAD_SHA"
  else
    echo "⚠️  PR event but missing SHA information"
    exit 1
  fi
else
  # For push events, check commits since the previous commit on this branch
  if [ -n "$GITHUB_BEFORE" ] && [ "$GITHUB_BEFORE" != "0000000000000000000000000000000000000000" ]; then
    BASE_SHA="${GITHUB_BEFORE}"
    HEAD_SHA="${GITHUB_SHA}"
    echo "Push: Checking commits from $BASE_SHA to $HEAD_SHA"
  else
    # For new branch or force push, check only the latest commit
    BASE_SHA=""
    HEAD_SHA="${GITHUB_SHA}"
    echo "Push: New branch/force push, checking only latest commit $HEAD_SHA"
  fi
fi

# If BASE_SHA is empty or "0000000...", check all commits
if [ -z "$BASE_SHA" ] || [ "$BASE_SHA" == "0000000000000000000000000000000000000000" ]; then
  echo "⚠️  Base SHA not available, checking only the latest commit"
  COMMITS_TO_CHECK="$HEAD_SHA"
else
  # Get all commits between base and head (exclusive of base, inclusive of head)
  COMMITS_TO_CHECK=$(git rev-list --no-merges "${BASE_SHA}..${HEAD_SHA}")
fi

if [ -z "$COMMITS_TO_CHECK" ]; then
  echo "ℹ️  No commits to check (possibly merge commits only)"
  exit 0
fi

# Track failed commits
FAILED_COMMITS=()
SUCCESS_COUNT=0

# Check each commit
while IFS= read -r commit_sha; do
  if [ -z "$commit_sha" ]; then
    continue
  fi
  
  # Get commit message
  commit_msg=$(git log -1 --format=%B "$commit_sha")
  
  # Get commit author info for reference
  commit_author=$(git log -1 --format="%an <%ae>" "$commit_sha")
  commit_subject=$(git log -1 --format="%s" "$commit_sha")
  
  # Check if commit message contains Signed-off-by line
  # Match "Signed-off-by:" at the start of a line (allowing whitespace)
  if echo "$commit_msg" | grep -qiE "^[[:space:]]*Signed-off-by:"; then
    echo "✅ Commit $commit_sha: DCO signed off"
    echo "   Author: $commit_author"
    echo "   Subject: $commit_subject"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
  else
    echo "❌ Commit $commit_sha: Missing DCO sign-off"
    echo "   Author: $commit_author"
    echo "   Subject: $commit_subject"
    FAILED_COMMITS+=("$commit_sha")
  fi
done <<< "$COMMITS_TO_CHECK"

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "DCO Check Summary:"
echo "  ✅ Signed off: $SUCCESS_COUNT"
echo "  ❌ Missing sign-off: ${#FAILED_COMMITS[@]}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Fail if any commits are missing sign-off
if [ ${#FAILED_COMMITS[@]} -gt 0 ]; then
  echo ""
  echo "❌ DCO Check Failed!"
  echo ""
  echo "The following commits are missing DCO sign-off:"
  for commit in "${FAILED_COMMITS[@]}"; do
    author=$(git log -1 --format="%an <%ae>" "$commit")
    subject=$(git log -1 --format="%s" "$commit")
    echo "  - $commit ($author): $subject"
  done
  echo ""
  echo "To fix unsigned commits, run:"
  echo "  git commit --amend --signoff --no-edit"
  echo ""
  echo "Or for multiple commits, use interactive rebase:"
  echo "  git rebase -i HEAD~n  # where n is the number of commits"
  echo "  # Then for each commit, run: git commit --amend --signoff --no-edit"
  echo ""
  exit 1
else
  echo ""
  echo "✅ All commits are properly signed off!"
  echo ""
  exit 0
fi

