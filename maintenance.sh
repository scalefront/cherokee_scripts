#!/bin/bash

# This is an example script that can be used to call
# the maintenance.py script and reload cherokee web
# server.
#
# This script takes enable/disable or up/down as the first argument

if [ "$(whoami)" != "root" ]; then
    echo "This script needs to be run as sudo/root."
    exit 1
fi

# Convert up/down to enable/disable
action=$1
if [ $action == 'up' ]; then
    action='enable'
elif [ $action == 'down' ]; then
    action='disable'
fi

# Specify the vserver nick that should be affected.
./maintenance.py "$action" --vserver_nick="Example Nick"

# Only reload cherokee if the maintenance script succeeded
if [ "$?" == 0 ]; then
    service cherokee reload
fi
