# LifeLog

LifeLog is a DIY system for tracking metrics about your life, such as how much
you weigh, how often you exersise, or how you spend your time. This repository
contains the server side components that implement the web API; as the API
develops, client-side projects using LifeLogServer will be made.

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

# Basic Developer Workflow

1. Each time you open a terminal, run `nix-shell path/to/this/repo/default.nix`.

1. When you are setting up your development environment for the first time,
   consider running these commands:

   * `git config --local core.hooksPath ".GitHooks"`: configure git to
     automatically run tests when creating new commits.

   * `flask.bash reinit-dev`: Initialize the development database with default
     values.

1. While you are working, leave this command running in the background:

   ```
   flask.bash run
   ```

1. You should now be able to query the server using your choince of REST
   clients. For example:

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

## Misc Helpful commands

Interacting with the database directly:

* Open a shell in the dev database: `flask.bash dev-db`

* Open a shell in the prod databse: `flask.bash prod-db`

* To just run a single command: `flask.bash *-db 'SELECT * FROM USERS'`

* Reset the dev database: `flask.bash reinit-dev`
