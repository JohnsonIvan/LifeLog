#!/bin/env bash
set -euo pipefail
#set -x
DIR="$(dirname "$0")"
cd "$DIR"
cd $(git rev-parse --show-toplevel)

APP_NAME="lifelogserver"
USER="lifelogserver"
GROUP="$USER"
SCRIPTS_DIR="$(pwd)/Scripts"
DEV_ENV_DIR="$(pwd)/.venv"
WEBSTATIC_DIR="$(pwd)/WebStatic"
PROD_DIR='/srv/LifeLog'
CODE_DIR="${PROD_DIR}/Code" #TODO: needs a better name. Backend?
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

id -u "$USER" || (echo creating the user "\"${USER}\""; sudo useradd -r -s /usr/bin/nologin "$USER")

sudo rm -f "$CODE_DIR/$APP_NAME-"*

# ~sudo cp $WEBSTATIC_DIR $PROD_DIR
(cd "${WEBSTATIC_DIR}"; find . -type f -exec sudo install -D "--mode=${CHMOD_PERMISSIONS}" "{}" "${PROD_DIR}/WebStatic/{}" \;)

sudo install -D "--mode=${CHMOD_PERMISSIONS}" --owner "root" --group "$GROUP" "dist/$APP_NAME-"*".whl"                    "$CODE_DIR" # TODO: is it possible for there to be multiple versions?
sudo install -D "--mode=${CHMOD_PERMISSIONS}" --owner "root" --group "$GROUP" "$SCRIPTS_DIR/launch.bash"                  "$CODE_DIR"
sudo install -D "--mode=${CHMOD_PERMISSIONS}" --owner "root" --group "$GROUP" "$SCRIPTS_DIR/lifelogserver.service"        "/etc/systemd/system/"
sudo install -D "--mode=${CHMOD_PERMISSIONS}" --owner "root" --group "$GROUP" "$SCRIPTS_DIR/net.ivanjohnson.lifelog.conf" "/etc/nginx/servers/"

sudo systemctl daemon-reload
sudo systemctl restart lifelogserver
sudo systemctl reload nginx

cat << delimiter
Launch LifeLogServer, wait until loaded then stop it:
	sudo systemctl start lifelogserver
	sudo watch systemctl status lifelogserver # Ctrl-C once finished
	sudo systemctl stop lifelogserver
Purge/reinitialize the database if necessary (automatic migrations have not yet been implemented, as of 2022-09-19):
	purge:
		sudo trash "${CODE_DIR}/${PROD_ENV_DIR_NAME}/var/LifeLogServer-instance/lifelog.sqlite"
	Restore backup:
		# UNTESTED
		sudo install --owner "$USER" --group "$GROUP" -d ./path/to/backup/${PROD_ENV_DIR_NAME}_var_LifeLogServer-instance.bak -t "${CODE_DIR}/${PROD_ENV_DIR_NAME}/var/LifeLogServer-instance"
	(Re-)initialize:
		sudo -u "$USER" bash -c 'cd "$CODE_DIR"; source ./${PROD_ENV_DIR_NAME}/bin/activate; export FLASK_APP=LifeLogServer; flask init-db'
Set a secret key for doing secure stuff like signing session:
	sudo -u "$USER" bash << DELIMITER
	mkdir -p "${CODE_DIR}/${PROD_ENV_DIR_NAME}/var/flaskr-instance/"
	python -c 'import os; print(f"SECRET_KEY = {os.urandom(16)}")' > ${CODE_DIR}/${PROD_ENV_DIR_NAME}/var/flaskr-instance/config.py
	chmod 600 ${CODE_DIR}/${PROD_ENV_DIR_NAME}/var/flaskr-instance/config.py
	DELIMITER
Enable/start LifeLogServer:
	sudo systemctl enable --now "$APP_NAME"
Check for warnings/errors:
	journalctl -eu "$APP_NAME"
delimiter
