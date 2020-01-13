#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"


./Nginx/apply.bash

DIR_OUT=/srv/http/LifeLog/
DIR_SYSTEMD=/etc/systemd/system/

sudo mkdir -p "$DIR_OUT"

#TODO: only do copies when diff detects change. Or just `make deploy`...
sudo cp Uwsgi/wsgi_config.ini "$DIR_OUT"
sudo cp Src/test.py "$DIR_OUT"
sudo cp Uwsgi/lifelog_uwsgi.service "$DIR_SYSTEMD"


sudo systemctl daemon-reload
sudo systemctl restart lifelog_uwsgi || (sudo systemctl status lifelog_uwsgi; exit 1)
