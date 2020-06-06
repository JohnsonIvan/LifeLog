#!/bin/env bash
set -euo pipefail
#set -x
DIR="$(dirname "$0")"
cd "$DIR"

#git config --local core.hooksPath .GitHooks

REQUIRED_PACKAGES="python python-pip sqlite"

pacman -Qi $REQUIRED_PACKAGES > /dev/null || sudo pacman --needed -Syu $REQUIRED_PACKAGES

ENV_DIR=".venv"
if [ -e "$ENV_DIR" ]; then
	echo "ERROR: $ENV_DIR already exists"
	exit 1
fi
python3 -m venv "$ENV_DIR"

source "${ENV_DIR}/bin/activate"
pip install -e '.[test]'

echo initializing database
bash flask.bash reinit-dev && echo database initialization successful

echo running tests now
bash test.bash --coverage
