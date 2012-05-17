# cherokee_scripts

Scripts for interacting with Cherokee Web Server

## maintenance.py / maintenance.sh

Enables/disables a vserver rule to trigger a maintenance notice.

Cherokee has a great admin interface for humans but not much
support for scripted actions.  This script delves into the
cherokee config file to enable/disable a very specific rule under a
specified vserver.

### Example Usage
$ maintenance.py enable --vserver_nick="My Example VServer"

### Required Maintenance Rules

The relevant vserver should have two maintenance rules.  
Rule 1) Handles the maintenance page.  
Rule 2) Directs all traffic to a maintenance page.  

Rule 1) Can handle the maintenance page whatever way you like.

Rule 2) needs to be a directory match on '/' (which will match everything).
Its handler is a regex redirection performing an internal redirection
of everything (.*) to the maintenance page.
