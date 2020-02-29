#!/bin/env bash
set -euo pipefail
#set -x
DIR="$(dirname "$0")"
cd "$DIR"

export FLASK_APP=./
export FLASK_ENV=development

if [ "${1:-}" = "--reinit" ] ; then
	flask init-db
fi

flask run --host=0.0.0.0
