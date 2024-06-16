#!/usr/bin/env bash
set -euo pipefail
set -x

SCRIPTS_DIR="$(dirname "$0")"

cd "$(git rev-parse --show-toplevel)"

git config --local core.hooksPath ".GitHooks"

source "${ENV_DIR}/bin/activate"

echo initializing database
"$SCRIPTS_DIR/flask.bash" reinit-dev

echo running tests now
"$SCRIPTS_DIR/test.bash" --coverage
