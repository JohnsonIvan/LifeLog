#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

sudo mkdir -p /srv/LifeLog
sudo cp lifelog.conf /etc/nginx/servers/
sudo certbot --noninteractive --agree-tos --nginx --domain lifelog.ivanjohnson.net --quiet
sudo systemctl restart nginx || (systemctl status nginx.service; exit 1)
