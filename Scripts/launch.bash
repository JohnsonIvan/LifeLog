#!/bin/env bash
set -euo pipefail
#set -x
DIR="$(dirname "$0")"
cd "$DIR"

ENV_DIR=".venv"
PKG_NAME="lifelogserver"
APP_NAME="LifeLogServer"

if ! [ -e "$ENV_DIR" ]; then
	echo "Could not detect virtual environment; making a new one."
	python3 -m venv "$ENV_DIR"
fi


source "${ENV_DIR}/bin/activate"

echo "Installing LLS in the venv"
pip install "${PKG_NAME}-"*".whl"

waitress-serve --call "${APP_NAME}:create_app"
