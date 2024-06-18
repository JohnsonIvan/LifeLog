# LifeLog

LifeLog is a DIY system for tracking metrics about your life, such as how much
you weigh, how often you exersise, or how you spend your time. This repository
contains the server side components that implement the web API; as the API
develops, client-side projects using LifeLogServer will be made.

At present, Arch Linux is the only supported platform for running the server.

# Notable Features

* Extensive test suite

* Token-based authentication

* Makes heavy use of GitHub
  [issues](https://github.com/Ivan-Johnson/LifeLogServer/issues) and
  [milestones](https://github.com/Ivan-Johnson/LifeLogServer/milestones) to plan
  future development

# Documentation

Documentation can be found online:
https://life-log-server.readthedocs.io/en/master/

# Installation

Run `Scripts/deploy.bash`. This will generate a python package and install it
and any other necessary files for running LLS.

# Development

## NixOS

TODO port the rest of this section to NixOS

Setup:

1. Run `nix-shell default.nix`

2. Run `src/Scripts/flask.bash run`?

    FLASK_APP=./src/LifeLogServer/  FLASK_DEBUG=1 /nix/store/iaj1sn0kq6ij088ra94mns3v40imw8ml-python3.11-flask-2.3.3/bin/flask run --host=0.0.0.0

2. ???

3. Profit!

## Setup

Run this when setting up a new development environment:

    ./Scripts/setup_dev.bash

This script will use `pacman` to install dependencies to your host, then setup a
python virtual environment ("venv") and install further python dependencies
there.

## Basic Developer Workflow

Use this to run the server; it will automatically restart the server after you modify any files:

    ./Scripts/flask.bash run

Then you can use a REST client of your choice to actually call LLS's endpoints. For example:

* Graphical tools:

    * insomnia

    * postman

* CLI:

    * httpie

        $ http POST '127.0.0.1:5000/api/v1/weight/entry?datetime=1671905744&weight=100&units=kilograms' token:dev-key

        HTTP/1.1 201 CREATED
        Connection: close
        Content-Length: 36
        Content-Type: text/html; charset=utf-8
        Date: Sat, 24 Dec 2022 18:21:57 GMT
        Server: Werkzeug/2.2.2 Python/3.10.8

        c15ccf2c-6938-41c8-897d-ce686d997f0a

    * You could also use standard Linux commands, but they aren't optimized for
      this usecase; they have a steeper learning curve and typically require
      more typing:

        * curl

            $ curl -i -X POST --header token:dev-key '127.0.0.1:5000/api/v1/weight/entry?datetime=1671905744&weight=100&units=kilograms'
            HTTP/1.1 201 CREATED
            Server: Werkzeug/2.2.2 Python/3.10.8
            Date: Sat, 24 Dec 2022 18:17:03 GMT
            Content-Type: text/html; charset=utf-8
            Content-Length: 36
            Connection: close

            65727f6e-09c1-452d-8663-a9edd4a589cc


        * wget

            $ wget --method=POST '127.0.0.1:5000/api/v1/weight/entry?datetime=1671905744&weight=100&units=kilograms' --header=token:dev-key -qO -
            4e2c2321-c578-48d6-8221-3d2e523a14f3

## Automated Tests

    Scripts/test.bash

## Misc Helpful commands

Interacting with the database directly:

* Open a shell in the dev database: `./Scripts/flask.bash dev-db`

* Open a shell in the prod databse: `./Scripts/flask.bash prod-db`

* To just run a single command: `./Scripts/flask.bash *-db 'SELECT * FROM USERS'`

Reset the dev database: `./Scripts/flask.bash reinit-dev`
