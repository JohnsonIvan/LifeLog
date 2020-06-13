# LifeLog

LifeLog is a DIY system for tracking metrics about your life, such as how much
you weigh, how often you exersise, or how you spend your time. It is still in
the very early stages of development. This repository contains the server side
components that implement the web API; as the API develops, client-side projects
using LifeLogServer will be made.

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

# Setup

Before starting development for LifeLogServer, there are a few things you have
to do such as installing dependencies and setting up a python virtual
environment. The `setup_dev.bash` script will handle this for you.
