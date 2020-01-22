# LifeLog

LifeLog is a DIY life logging system. It is still in the very early stages of
development, but eventually it will be able to track exersise, weight, time, and
finances.

The main interface to the app is by running iOS shortcuts that launch the iOS
app Pythonista which will prompt you for any necessary input, then send the
request to a server where the information is stored in a database.

# Technical Overview of the Server

This section gives a summary of how the major software packages used by LifeLog
interact, as well as additional recommendations on how to configure a server
that runs LifeLog.

Unless your server is only accessible from your private, secure, network I would
recommend using a firewall; I use NFTables and unblock ports 80 and 443 for http
and https traffic respectively. At present I have not included nor do I expect
to ever include detailed firewall configuration instructions in LifeLog.

Having gotten through the firewall, web requests are next recieved by
[nginx](https://en.wikipedia.org/wiki/Nginx). If the request is to '/api' or one
of it's subdirectories, then nginx forwards the request to a
[uwsgi](https://uwsgi-docs.readthedocs.io/en/latest/) server. In all other
cases, nginx will assume the url corresponds to static web content and try to
serve find a file with an appropriate path to return.

The uwsgi server balances requests among a number of processes and threads
before we finally get to the "real" code for handling requests, which is written
in Python using the [flask](https://palletsprojects.com/p/flask/) framework.

# Server Setup

The setup guide is still a work in progress.

On Arch Linux, this command should install all the necessary packages:

    sudo pacman -Syu python python-flask pip nginx uwsgi uwsgi-plugin-python sqlite

If you have a firewall, you'll need to open ports 80 and 443.
