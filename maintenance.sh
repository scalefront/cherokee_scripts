#!/bin/bash

# This is an example script that can be used to call
# the maintenance.py script and reload cherokee web
# server.
#
# This script takes enable/disable as the first argument

if [ "$(whoami)" != "root" ]; then
    echo "This script needs to be run as sudo/root."
    exit 1
fi

# Specify the vserver nick that should be affected.
./maintenance.py "$1" --vserver_nick="Example Nick"

# Only reload cherokee if the maintenance script succeeded
if [ "$?" == 0 ]; then
    service cherokee reload
fi
