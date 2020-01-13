#!/bin/bash
cd "$(dirname "$0")"

sudo mkdir -p /srv/LifeLog
sudo cp lifelog.conf /etc/nginx/servers/
sudo systemctl restart nginx || (systemctl status nginx.service; exit 1)
