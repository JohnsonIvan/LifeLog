#!/bin/env bash
set -euo pipefail
#set -x
DIR="$(dirname "$0")"
cd "$DIR"
cd $(git rev-parse --show-toplevel)

APP_NAME="lifelogserver"
USERNAME="lifelogserver"
SCRIPTS_DIR="$(pwd)/Scripts/"
ENV_DIR="$(pwd)/.venv"

# TODO: should we apply these permissions recursively? Realistically, it should
# be sufficient to apply them to the prod directory?
CHMOD_PERMISSIONS=750

if ! [ -e "$ENV_DIR" ]; then
	echo "dev is not setup; doing now"
	"$SCRIPTS_DIR/setup_dev.bash" || (echo SETUP_DEV SCRIPT FAILED; exit 1)
fi

echo activating venv
set +euo pipefail
source "${ENV_DIR}/bin/activate"
set -euo pipefail

pip install wheel

echo 'Doing an interactive `git clean` before the build.' "You're in charge."
git clean -di

python setup.py bdist_wheel

id -u "$USERNAME" || (echo creating the user "\"${USERNAME}\""; sudo useradd -r -s /usr/bin/nologin "$USERNAME")

# Create top-level production directory
PROD_DIR='/srv/LifeLog/Code'
sudo mkdir -p "$PROD_DIR"
sudo chown "$USERNAME:$USERNAME" "/srv/LifeLog"
sudo chmod "$CHMOD_PERMISSIONS" "/srv/LifeLog"
sudo chown "$USERNAME:$USERNAME" "$PROD_DIR"
sudo chmod "$CHMOD_PERMISSIONS" "$PROD_DIR"

sudo rm -f "$PROD_DIR/$APP_NAME-"*

sudo install "dist/$APP_NAME-"*".whl" "$PROD_DIR"

sudo cp "$SCRIPTS_DIR/launch.bash" "$PROD_DIR"
sudo chmod 755 "$PROD_DIR/launch.bash"

sudo cp "$SCRIPTS_DIR/lifelogserver.service" "/etc/systemd/system/"

sudo systemctl daemon-reload

cat << delimiter
Launch LifeLogServer, wait until loaded then stop it:
	sudo systemctl start lifelogserver
	sudo watch systemctl status lifelogserver # Ctrl-C once finished
	sudo systemctl stop lifelogserver
Purge/reinitialize the database if necessary (automatic migrations have not yet been implemented, as of 2022-09-19):
	purge:
		sudo trash "${PROD_DIR}/.venv/var/LifeLogServer-instance/lifelog.sqlite"
	Restore backup:
		# UNTESTED
		sudo install --owner "$USERNAME" --group "$USERNAME" -d ./path/to/backup/venv_var_LifeLogServer-instance.bak -t "${PROD_DIR}/.venv/var/LifeLogServer-instance"
	(Re-)initialize:
		sudo -u "$USERNAME" bash -c 'cd "$PROD_DIR"; source ./.venv/bin/activate; export FLASK_APP=LifeLogServer; flask init-db'
Set a secret key for doing secure stuff like signing session:
	sudo -u "$USERNAME" bash << DELIMITER
	mkdir -p "${PROD_DIR}/.venv/var/flaskr-instance/"
	python -c 'import os; print(f"SECRET_KEY = {os.urandom(16)}")' > /srv/LifeLog/Code/.venv/var/flaskr-instance/config.py
	chmod 600 /srv/LifeLog/Code/.venv/var/flaskr-instance/config.py
	DELIMITER
Enable/start LifeLogServer:
	sudo systemctl enable --now "$APP_NAME"
Check for warnings/errors:
	journalctl -eu "$APP_NAME"
delimiter
