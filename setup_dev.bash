#!/bin/env bash
set -euo pipefail
#set -x
DIR="$(dirname "$0")"
cd "$DIR"

sudo pacman --needed -Syu python python-pip sqlite

ENV_DIR="VEnv"
if [ -e "$ENV_DIR" ]; then
	echo "ERROR: $ENV_DIR already exists"
	exit 1
fi
python3 -m venv "$ENV_DIR"

source "${ENV_DIR}/bin/activate"
pip install Flask
echo "Remember to source \"$(DIR)/$ENV_DIR/bin/activate\""

pip install -e .
