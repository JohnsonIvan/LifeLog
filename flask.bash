#!/bin/env bash
set -euo pipefail
#set -x
DIR="$(dirname "$0")"
cd "$DIR"
this="./$(basename "$0")"

export FLASK_APP=./
export FLASK_ENV=development

DEV_DB="instance/lifelog.sqlite"

if [ "${1:-}" = "reinit-dev" ] ; then
	rm -f "$DEV_DB"
	flask init-db
	"$this" dev-db 'INSERT INTO users (userid, token) VALUES ("ee1fa47a-9a1b-4fed-a074-5af9915440fd", "dev-key")'
elif [ "${1:-}" = "dev-db" ] ; then
	shift
	sqlite3 "${DEV_DB}" "$@"
elif [ "${1:-}" = "run" ] ; then
	flask run --host=0.0.0.0
else
	ecode=0
	if [ "${1:-}" != "help" ]; then
		echo "No valid subcommand recognized. Defaulting to \"help\""
		ecode=1
	fi
	echo "The syntax for using this command is \"$(basename "$0") \${subcommand}\"."
	echo "Valid subcommands are:"
	echo -e "\tdev-db: functions as an alias for \"sqlite3\"; it is configured to use the dev database"
	echo -e "\thelp: show this menu"
	echo -e "\treinit-dev: reset the dev database to a known good state"
	echo -e "\trun: run the flask server locally"
	exit $ecode
fi
