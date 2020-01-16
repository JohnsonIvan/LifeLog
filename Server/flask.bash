#!/bin/bash
cd "$(dirname "$0")"

if [ "$1" = "--reinit" ] ; then
	FLASK_APP=./Code/LifeLog/ FLASK_ENV=development flask init-db
fi

FLASK_APP=./Code/LifeLog/ FLASK_ENV=development flask run --host=0.0.0.0
