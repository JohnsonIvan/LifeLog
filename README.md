#LifeLog

LifeLog is a DIY life logging system. It is still in the very early stages of
development, but eventually it will be able to track exersise, weight, time, and
finances.

The main interface to the app is by running iOS shortcuts that launch the iOS
app Pythonista which will prompt you for any necessary input, then send the
request to a server where the information is stored in a database.

#Setup

    sudo pacman -S python pip nginx uwsgi sqlite

Open ports 80 & 443
uwsgi-plugin-python
