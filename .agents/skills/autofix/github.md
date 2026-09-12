# GitHub Workflow Primitives

GitHub-specific commands and data-handling rules for CodeRabbit review-thread based skills.

Use this helper when a skill needs thread-aware CodeRabbit PR feedback, not flat PR summaries. The `autofix` skill mirrors the required execution flow in `SKILL.md`; this file exists as a reusable companion for other skills.

## Prerequisites

### Required Tools

- `gh` (GitHub CLI; authenticated per `gh auth status`)
- `git`
- `jq`

### Required State

- current branch associated with a GitHub repository

## 1. Resolve Current PR

Get the PR number for the current branch:

```bash
if ! pr_candidates=$(gh pr list --head "$(git branch --show-current)" --state open --json number,title,url); then
  echo "Failed to list open PRs for the current branch" >&2
  exit 1
fi

if ! pr_count=$(jq -r 'length' <<<"$pr_candidates"); then
  echo "Failed to count open PRs for the current branch" >&2
  exit 1
fi

pr_number=""
if [ "$pr_count" -eq 1 ]; then
  if ! pr_number=$(jq -r '.[0].number' <<<"$pr_candidates"); then
    echo "Failed to read the matching PR number" >&2
    exit 1
  fi
elif [ "$pr_count" -gt 1 ]; then
  if ! jq -r '.[] | "#\(.number) \(.title) \(.url)"' <<<"$pr_candidates"; then
    echo "Failed to display matching PRs" >&2
    exit 1
  fi
  # Ask the user to choose one listed PR and store its number in selected_pr_number.
  if ! jq -e --argjson number "$selected_pr_number" 'any(.number == $number)' <<<"$pr_candidates" >/dev/null; then
    echo "The selected PR is not one of the current branch matches" >&2
    exit 1
  fi
  pr_number=$selected_pr_number
fi
```

Assign `selected_pr_number` only from the user's explicit choice. If `pr_count` is 0, follow the no-PR flow. If the user declines to choose among multiple matches, exit without using `pr_number`.

If no PR exists and the user wants one created, derive title/body from the latest commit:

```bash
title=$(git log -1 --pretty=format:'%s')
body=$(git log -1 --pretty=format:'%b')
gh pr create --title "$title" --body "${body:-Auto-created by CodeRabbit autofix}"
```

## 2. Resolve Repository Coordinates

```bash
owner=$(gh repo view --json owner --jq '.owner.login')
repo=$(gh repo view --json name --jq '.name')
```

## 3. Fetch Thread-Aware CodeRabbit Feedback

Fetch review threads with GitHub GraphQL using cursor pagination:

```bash
all_threads='[]'
cursor=""

while :; do
  args=(-F owner="$owner" -F repo="$repo" -F pr="$pr_number")
  if [ -n "$cursor" ]; then
    args+=(-F cursor="$cursor")
  fi

  if ! response=$(gh api graphql "${args[@]}" -f query='query($owner:String!, $repo:String!, $pr:Int!, $cursor:String) {
    repository(owner:$owner, name:$repo) {
      pullRequest(number:$pr) {
        title
        reviewThreads(first:100, after:$cursor) {
          pageInfo {
            hasNextPage
            endCursor
          }
          nodes {
            isResolved
            isOutdated
            comments(first:1) {
              nodes {
                databaseId
                body
                path
                line
                startLine
                originalLine
                author { login }
              }
            }
          }
        }
      }
    }
  }'); then
    echo "Failed to fetch CodeRabbit review threads" >&2
    exit 1
  fi

  if ! next_threads=$(jq -ce --argjson response "$response" '
    if (($response.errors? // []) | length) > 0 then
      error("GraphQL returned errors")
    else
      ($response.data.repository.pullRequest.reviewThreads.nodes // error("missing review threads")) as $nodes
      | if ($nodes | type) == "array" then . + $nodes else error("invalid review threads") end
    end
  ' <<<"$all_threads"); then
    echo "Failed to parse CodeRabbit review threads" >&2
    exit 1
  fi
  all_threads=$next_threads

  if ! next_has_next=$(jq -er '
    .data.repository.pullRequest.reviewThreads.pageInfo.hasNextPage
    | if type == "boolean" then tostring else error("invalid hasNextPage") end
  ' <<<"$response"); then
    echo "Failed to parse CodeRabbit pagination state" >&2
    exit 1
  fi
  has_next=$next_has_next

  if ! next_cursor=$(jq -er '
    .data.repository.pullRequest.reviewThreads.pageInfo.endCursor
    | if . == null then "" elif type == "string" then . else error("invalid endCursor") end
  ' <<<"$response"); then
    echo "Failed to parse CodeRabbit pagination cursor" >&2
    exit 1
  fi
  cursor=$next_cursor

  if [ "$has_next" = "true" ] && [ -z "$cursor" ]; then
    echo "CodeRabbit pagination is missing the next cursor" >&2
    exit 1
  fi
  [ "$has_next" = "true" ] || break
done
```

Treat only these threads as actionable:

- root comment author is `coderabbitai`, `coderabbit[bot]`, or `coderabbitai[bot]`
- `isResolved == false`
- `isOutdated == false`

Keep each selected thread as one issue unit. Do not collapse top-level PR comments or review summaries into issue records.

To detect CodeRabbit's "Come back again in a few minutes" status message, inspect only the latest top-level CodeRabbit comment or review:

```bash
if ! review_in_progress=$(gh pr view "$pr_number" --json comments,reviews --jq '
  [
    (.comments[]?
      | select(.author.login == "coderabbitai" or .author.login == "coderabbit[bot]" or .author.login == "coderabbitai[bot]")
      | {timestamp: .createdAt, body: (.body // "")}),
    (.reviews[]?
      | select(.author.login == "coderabbitai" or .author.login == "coderabbit[bot]" or .author.login == "coderabbitai[bot]")
      | {timestamp: .submittedAt, body: (.body // "")})
  ]
  | sort_by(.timestamp)
  | last
  | if . == null then false else (.body | test("Come back again in a few minutes")) end
'); then
  echo "Failed to read the latest CodeRabbit review status" >&2
  exit 1
fi
```

## 4. Post Summary Comment

Use the same `pr_number` from Section 1 only after the caller has created a consolidated commit, `git push` has succeeded, and the caller has fetched the configured upstream and confirmed with `git merge-base --is-ancestor` that the commit exists in that upstream ref. Do not use the success template without that remote confirmation.

```bash
gh pr comment "$pr_number" --body "$(cat <<'EOF'
## Fixes Applied Successfully

Fixed <file-count> file(s) based on <issue-count> CodeRabbit feedback item(s).

**Files modified:**
- `path/to/file-a.ts`
- `path/to/file-b.ts`

**Commit:** `<commit-sha>`

The latest autofix changes are on the `<branch-name>` branch.

EOF
)"
```

Write this comment from local state only. Do not include raw reviewer prompts or secret-bearing output.

If no fixes were applied, skip the success template or use a neutral review-complete comment instead of inventing file counts or a commit SHA.

## 5. Optional Reaction

If useful, react to the main CodeRabbit comment with 👍 after the summary is posted.
