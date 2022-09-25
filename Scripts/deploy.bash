#!/bin/env bash
set -euo pipefail
#set -x
DIR="$(dirname "$0")"
cd "$DIR"
cd $(git rev-parse --show-toplevel)

APP_NAME="lifelogserver"
USERNAME="lifelogserver"
SCRIPTS_DIR="$(pwd)/Scripts/"
DEV_ENV_DIR="$(pwd)/.venv"
PROD_DIR='/srv/LifeLog/Code'
PROD_ENV_DIR_NAME="venv"
CHMOD_PERMISSIONS=750

if ! [ -e "$DEV_ENV_DIR" ]; then
	echo "dev is not setup; doing now"
	"$SCRIPTS_DIR/setup_dev.bash" || (echo SETUP_DEV SCRIPT FAILED; exit 1)
fi

echo activating venv
set +euo pipefail
source "${DEV_ENV_DIR}/bin/activate"
set -euo pipefail

pip install wheel

echo 'Doing an interactive `git clean` before the build.' "You're in charge."
git clean -di

python setup.py bdist_wheel

id -u "$USERNAME" || (echo creating the user "\"${USERNAME}\""; sudo useradd -r -s /usr/bin/nologin "$USERNAME")

# Create top-level production directory
sudo mkdir -p "$PROD_DIR"
sudo chown "$USERNAME:$USERNAME" "/srv/LifeLog"
sudo chmod "$CHMOD_PERMISSIONS" "/srv/LifeLog"
sudo chown "$USERNAME:$USERNAME" "$PROD_DIR"
sudo chmod "$CHMOD_PERMISSIONS" "$PROD_DIR"

sudo rm -f "$PROD_DIR/$APP_NAME-"*

sudo install "--mode=${CHMOD_PERMISSIONS}" "dist/$APP_NAME-"*".whl"             "$PROD_DIR"
sudo install "--mode=${CHMOD_PERMISSIONS}" "$SCRIPTS_DIR/launch.bash"           "$PROD_DIR"
sudo install "--mode=${CHMOD_PERMISSIONS}" "$SCRIPTS_DIR/lifelogserver.service" "/etc/systemd/system/"

sudo systemctl daemon-reload

cat << delimiter
Launch LifeLogServer, wait until loaded then stop it:
	sudo systemctl start lifelogserver
	sudo watch systemctl status lifelogserver # Ctrl-C once finished
	sudo systemctl stop lifelogserver
Purge/reinitialize the database if necessary (automatic migrations have not yet been implemented, as of 2022-09-19):
	purge:
		sudo trash "${PROD_DIR}/${PROD_ENV_DIR_NAME}/var/LifeLogServer-instance/lifelog.sqlite"
	Restore backup:
		# UNTESTED
		sudo install --owner "$USERNAME" --group "$USERNAME" -d ./path/to/backup/${PROD_ENV_DIR_NAME}_var_LifeLogServer-instance.bak -t "${PROD_DIR}/${PROD_ENV_DIR_NAME}/var/LifeLogServer-instance"
	(Re-)initialize:
		sudo -u "$USERNAME" bash -c 'cd "$PROD_DIR"; source ./${PROD_ENV_DIR_NAME}/bin/activate; export FLASK_APP=LifeLogServer; flask init-db'
Set a secret key for doing secure stuff like signing session:
	sudo -u "$USERNAME" bash << DELIMITER
	mkdir -p "${PROD_DIR}/${PROD_ENV_DIR_NAME}/var/flaskr-instance/"
	python -c 'import os; print(f"SECRET_KEY = {os.urandom(16)}")' > ${PROD_DIR}/${PROD_ENV_DIR_NAME}/var/flaskr-instance/config.py
	chmod 600 ${PROD_DIR}/${PROD_ENV_DIR_NAME}/var/flaskr-instance/config.py
	DELIMITER
Enable/start LifeLogServer:
	sudo systemctl enable --now "$APP_NAME"
Check for warnings/errors:
	journalctl -eu "$APP_NAME"
delimiter
