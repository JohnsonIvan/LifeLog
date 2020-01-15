#!/bin/bash
cd "$(dirname "$0")"

FLASK_APP=./Src/test.py FLASK_ENV=development flask run
