#!/usr/bin/env zsh
set -euo pipefail

examples_dir="${0:A:h}/examples"

function ensure_profiles() {
  local missing=0
  for profile in "$@"; do
    if ! uv run dspy-profiles show "$profile" >/dev/null 2>&1; then
      echo "  └── missing profile '$profile'; skipping."
      missing=1
    fi
  done
  return $missing
}

function run_example() {
  local label=$1; shift
  echo ""
  echo "=== ${label} ==="
  ( "$@" )
}

declare -A base_profiles=(
  [hello_world.py]="${DSPY_DEFAULT_PROFILE:-default}"
  [hello_decorator.py]="${DSPY_DEFAULT_PROFILE:-default}"
  [decorator_usage.py]="${DSPY_DEFAULT_PROFILE:-default}"
  [profile_overrides.py]="${DSPY_DEFAULT_PROFILE:-default}"
  [multiple_profiles.py]="${DSPY_MULTI_PROFILES:-default creative}"
  [extended_profiles.py]="${DSPY_EXTENDED_PROFILE:-creative_child}"
  [retrieval_example.py]="${DSPY_RETRIEVAL_PROFILE:-search}"
  [adaptive_agent.py]="${DSPY_AGENT_PROFILES:-creative_agent technical_agent}"
  [hello_runner.py]="${DSPY_RUNNER_PROFILE:-default}"
)

for example in ${^examples_dir}/*.py; do
  file=${example:t}

  local_profiles="${base_profiles[$file]-}"
  required=()
  if [[ -n "$local_profiles" ]]; then
    required=(${=local_profiles})
  fi

  if (( $#required )) && ! ensure_profiles "${required[@]}"; then
    continue
  fi

  case $file in
    hello_runner.py)
      run_example "$file" uv run dspy-run --profile "${required[1]}" -- "$example"
      ;;
    adaptive_agent.py)
      run_example "$file" uv run dspy-run --profile "${required[1]}" -- "$example"
      ;;
    *)
      run_example "$file" uv run python "$example"
      ;;
  esac
done
