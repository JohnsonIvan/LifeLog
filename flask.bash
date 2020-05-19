#!/bin/env bash
set -euo pipefail
#set -x
DIR="$(dirname "$0")"
cd "$DIR"

export FLASK_APP=./
export FLASK_ENV=development

DEV_INSTANCE=instance

if [ "${1:-}" = "reinit-dev" ] ; then
	flask init-db
	"$0" dev-db 'INSERT INTO auth_token (token) VALUES ("dev-key")'
elif [ "${1:-}" = "dev-db" ] ; then
	shift
	sqlite3 "${DEV_INSTANCE}/lifelog.sqlite" "$@"
elif [ "${1:-}" = "run" ] ; then
	flask run --host=0.0.0.0
else
	if [ "${1:-}" != "help" ]; then
		echo "No valid subcommand recognized. Defaulting to \"help\""
	fi
	echo "The syntax for using this command is \"$0 \${subcommand}\"."
	echo "Valid subcommands are:"
	echo -e "\tdev-db: a convenient alias for \"sqlite3\" configured to use the dev database"
	echo -e "\thelp: show this menu"
	echo -e "\treinit-dev: reset the dev database to a known good state"
	echo -e "\trun: run the flask server locally"
	exit 1
fi
