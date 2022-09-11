#!/bin/env bash
set -euo pipefail
#set -x
DIR="$(dirname "$0")"
cd "$DIR"
cd "$(git rev-parse --show-toplevel)"

SCRIPTS_DIR="$(pwd)/Scripts"

#git config --local core.hooksPath .GitHooks

git config --local core.hooksPath .GitHooks

REQUIRED_PACKAGES=("python" "python-pip" "sqlite")

pacman -Qi "${REQUIRED_PACKAGES[@]}" > /dev/null || sudo pacman --needed -Syu "${REQUIRED_PACKAGES[@]}"

ENV_DIR=".venv"
if [ -e "$ENV_DIR" ]; then
	echo "ERROR: $ENV_DIR already exists"
	exit 1
fi
python3 -m venv --prompt "LLS" "$ENV_DIR"

source "${ENV_DIR}/bin/activate"
pip install -e '.[test]'
pip install -r './Docs/requirements.txt'

echo initializing database
bash "$SCRIPTS_DIR/flask.bash" reinit-dev && echo database initialization successful

echo running tests now
bash "$SCRIPTS_DIR/test.bash" --coverage
