#!/bin/bash

# vim /etc/tmux.conf
#   new-session -s officelock /home/pi/git/officelock/officelock.sh
#
# sudo systemctl edit getty@tty1.service
# sudo systemctl restart getty@tty1.service

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

figlet Booting
while true; do
    echo "."
    aplay -q sounds/booting.wav
done &
PID=$!
disown
source /usr/local/bin/virtualenvwrapper.sh
workon officelock
kill $PID
killall -q aplay
figlet Initializing
aplay -q sounds/bootcomplete.wav

while true; do
    ./officelock.py
    aplay -q sounds/crash.wav
done
