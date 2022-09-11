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

# Development

To setup a new development environment, run the `./Scripts/setup_dev.bash`
script. This script will use `pacman` to install dependencies to your host, then
setup a python virtual environment ("venv") and install further python
dependencies there.

To run the test suite, run the `Scripts/test.bash` script.

# Installation

Run `Scripts/deploy.bash`. This will generate a python package and install it
and any other necessary files for running LLS.
