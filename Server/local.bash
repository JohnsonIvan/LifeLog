#!/bin/bash
cd "$(dirname "$0")"

FLASK_APP=./Src/test.py FLASK_DEBUG=1 flask run
