#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

DIR_OUT=/srv/LifeLog/
DIR_SYSTEMD=/etc/systemd/system/

sudo mkdir -p "$DIR_OUT"

#nginx
echo "Copying nginx files"
sudo cp -r WebStatic "$DIR_OUT"
sudo cp Config/nginx.conf /etc/nginx/servers/net.ivanjohnson.lifelog.conf
echo "Using certbot to upgrade to https"
sudo certbot --noninteractive --agree-tos --nginx --domain lifelog.ivanjohnson.net --quiet
echo "Restarting nginx"
sudo systemctl enable nginx
sudo systemctl restart nginx || (systemctl status nginx; exit 1)

#uwsgi
echo "Copying uwsgi files"
sudo cp Config/wsgi_config.ini "$DIR_OUT"
sudo cp Src/test.py "$DIR_OUT"
sudo cp Config/lifelog_uwsgi.service "$DIR_SYSTEMD"
echo "Restarting uwsgi"
sudo systemctl daemon-reload
sudo systemctl enable lifelog_uwsgi
sudo systemctl restart lifelog_uwsgi || (sudo systemctl status lifelog_uwsgi; exit 1)
