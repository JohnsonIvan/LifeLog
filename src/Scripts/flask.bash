#!/usr/bin/env bash
set -euo pipefail
#set -x
DIR="$(dirname "$0")"
cd "$DIR"
this="$(pwd)/$(basename "$0")"
#GIT="$(git rev-parse --show-toplevel)"
cd ~/Workspaces/4/LLS/

cd src
export FLASK_APP=./LifeLogServer
export FLASK_DEBUG=1

F_DB="lifelog.sqlite"

DEV_DB_DIR="instance"
PROD_DB_DIR="/srv/LifeLog/venv/var/LifeLogServer-instance"

DEV_DB="$DEV_DB_DIR/$F_DB"
PROD_DB="$PROD_DB_DIR/$F_DB"

if [ "${1:-}" = "reinit-dev" ] ; then
	rm -f "$DEV_DB"
	flask init-db
	USER_ID="dev-user-id"
	KEY="dev-key"
	"$this" dev-db "INSERT INTO users (userid) VALUES ('$USER_ID')"
	"$this" dev-db "INSERT INTO tokens (token, userid, description) VALUES ('$KEY', '$USER_ID', 'Dev key')"
	"$this" dev-db "INSERT INTO token_perms (token, permission) VALUES ('$KEY', 'ultimate')"

	"$this" dev-db "INSERT INTO weight_goal (userid, datetime_start, weight_kg_start, weight_change_kg_per_year) VALUES ('$USER_ID', 1450396800, 70.0, 60)" # 2015-12-18T00:00:00Z
	"$this" dev-db "INSERT INTO weight (id, userid, datetime, weight_kg) VALUES ('fec46a2e-cf9c-4dea-b5ef-5bc1aef34d8a', '$USER_ID', 1450483200, 70.5)"      # 2015-12-19T00:00:00Z
	"$this" dev-db "INSERT INTO weight (id, userid, datetime, weight_kg) VALUES ('9c4cfa98-2c09-4897-a0af-ab0503c6af72', '$USER_ID', 1450656000, 69.9)"      # 2015-12-21T00:00:00Z
	"$this" dev-db "INSERT INTO weight_goal (userid, datetime_start, weight_kg_start, weight_change_kg_per_year) VALUES ('$USER_ID', 1451606400, 71.0, -6)"	 # 2016-01-01T00:00:00Z
	"$this" dev-db "INSERT INTO weight (id, userid, datetime, weight_kg) VALUES ('20db843d-b349-4589-8e8d-7e4b2d3d588d', '$USER_ID', 1452988800, 73.0)"      # 2016-01-17T00:00:00Z
	"$this" dev-db "INSERT INTO weight (id, userid, datetime, weight_kg) VALUES ('932bd88c-9184-46b9-b59b-e4c0b0bef214', '$USER_ID', 1455840000, 69.2)"      # 2016-02-19T00:00:00Z
elif [ "${1:-}" = "dev-db" ] ; then
	shift
	sqlite3 "${DEV_DB}" "$@"
elif [ "${1:-}" = "prod-db" ] ; then
	shift
	sudo -u lifelogserver sqlite3 "${PROD_DB}" "$@"
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
