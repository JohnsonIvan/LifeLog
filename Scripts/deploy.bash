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

PROD_DIR='/srv/LifeLog/Code/'
sudo mkdir -p "$PROD_DIR"
sudo chown "$USERNAME:$USERNAME" "$PROD_DIR"

sudo rm -f "$PROD_DIR/$APP_NAME-"*

sudo cp "dist/$APP_NAME-"* "$PROD_DIR"

sudo cp "$SCRIPTS_DIR/launch.bash" "$PROD_DIR"
sudo chmod 755 "$PROD_DIR/launch.bash"

sudo cp "$SCRIPTS_DIR/lifelogserver.service" "/etc/systemd/system/"

sudo systemctl daemon-reload

echo 'Launch LifeLogServer, wait until loaded then stop it'
echo -e '\tsudo systemctl start lifelogserver'
echo 'Purge/reinitialize the database if necessary (automatic migrations have not yet been implemented, as of v0.5.0):'
echo -e "\tpurge: sudo trash /srv/LifeLog/Code/.venv/var/LifeLogServer-instance/lifelog.sqlite"
echo -e "\treinitialize: sudo -u lifelogserver bash -c 'cd /srv/LifeLog/Code; source ./.venv/bin/activate; export FLASK_APP=LifeLogServer; flask init-db'"
echo 'Set a secret key for doing secure stuff like signing session'
echo -e '\tSee https://flask.palletsprojects.com/en/1.1.x/tutorial/deploy/#configure-the-secret-key for instructions'
echo 'Enable/start LifeLogServer:'
echo -e '\tsudo systemctl enable --now lifelogserver'
echo 'Check for warnings/errors:'
echo -e '\tjournalctl -eu lifelogserver'
