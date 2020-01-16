#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

DIR_OUT=/srv/LifeLog
DIR_SYSTEMD=/etc/systemd/system
DIR_CODE="${DIR_OUT}/Code"
DIR_INSTANCE="${DIR_CODE}/instance"

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
sudo systemctl stop lifelog_uwsgi
sudo cp Config/wsgi_config.ini "$DIR_OUT"

#TL;DR: sudo cp -r Code "$DIR_CODE", but preserve the existing subdir "instance"
[ -e "${DIR_OUT}/instance" ] && exit 1 # fail if exists
[ -d "${DIR_CODE}/instance" ] && sudo mv "${DIR_CODE}/instance" "${DIR_OUT}"
sudo rm -rf "$DIR_CODE"
sudo cp -r Code "$DIR_CODE"
sudo rm -rf "${DIR_CODE}/instance"
[ -d "${DIR_OUT}/instance" ] && sudo mv "${DIR_OUT}/instance" "${DIR_CODE}"


sudo cp Config/lifelog_uwsgi.service "$DIR_SYSTEMD"

sudo mkdir -p "${DIR_INSTANCE}"
sudo chown root:http "${DIR_INSTANCE}"
sudo chmod 775 "${DIR_INSTANCE}"


echo "Restarting uwsgi"
sudo systemctl daemon-reload
sudo systemctl enable lifelog_uwsgi
sudo systemctl start lifelog_uwsgi || (sudo systemctl status lifelog_uwsgi; exit 1)


#database
ans=""
while [ "$ans" != "y" ] && [ "$ans" != "n" ] ; do
	echo "Would you like to reinitialize the PROD database?"
	echo "THIS WILL DESTROY ALL DATA CURRENTLY IN THE ###PROD### DATABASE"
	echo -n "(y/n) "
	read ans
done
if [ "$ans" = "y" ] ; then
	cd "$DIR_CODE"
	sudo -u http FLASK_APP=launcher:app flask init-db
	cd -
fi
