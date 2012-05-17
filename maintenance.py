#!/usr/bin/env python
import sys

default_settings = dict(config_path='/etc/cherokee/cherokee.conf',
                        disable=True,
                        vserver_nick='example.com',
                        ctk_path='/usr/share/cherokee/admin/CTK/')

def show_help():
    print """
    DESCRIPTION:
    ===========

    Finds the "maintenance rule" in the specified vserver and allows it to be enabled/disabled.

    To identify the correct rule the script looks for the following properties:
        1) Listed under the specified vserver
        2) Is a 'directory' matching rule
        3) Has a redirect handler
        4) Redirect handler directs all requests (.*) internally to '/maintenance/'

    USAGE:
    =====

    $ maintenance.py enable/disable [options]

    OPTIONS:
    =======

    The following options are available:
    * --help, -h
      Show this text.
    * --config_path, -c
      The path to the cherokee config file.
      Default: "%(config_path)s"
    * --vserver_nick, -v
      The virtual server nickname under which the rule change should be applied.
      Default: "%(vserver_nick)s"
    * --ctk_path, -p
      The location of the Cherokee Toolkit (CTK). This should be under the Cherokee install location.
      CTK contains a module that can read/write the Cherokee config file.
      Default: "%(ctk_path)s"
    """ % default_settings

def _find_vserver(config, nick):
    print "Looking for vserver nick: %s" % nick
    # Iterate over each vserver in the config
    for n in config['vserver'].keys():
        vs = config['vserver'][str(n)]
        cur_nick = vs['nick'].value
        print "Checking vserver!%s!nick = %s" % (n, cur_nick)
        if nick == cur_nick:
            print "Found"
            return vs
    raise Exception("The vserver \"%s\" was not found" % nick)

def _find_rule(vserver):
    print "Looking for Rule<\"directory\", \"/\"> with Handler<\"redir\", \".*->/maintenance/\"> in VServer<\"%s\">" % (vserver['nick'].value)
    # Iterate over each rule in the vserver
    for n in vserver['rule'].keys():
        # Index to the rule node
        rule = vserver['rule'][str(n)]

        print "Checking rule " + str(n)
        # Check that it's a directory rule
        if rule['match'] and rule['match'].value == 'directory':
            # Check that it matches the root path (will then match everything)
            if rule['match']['directory'] and rule['match']['directory'].value == '/':

                # Check that the handler is a redir (we want to find the one that redirects everything to "/maintenance/")
                if rule['handler'] and rule['handler'].value == 'redir':

                    # There should only be a single rewrite regex for the maintenance rule
                    rewrite_keys = rule['handler']['rewrite'].keys()
                    if len(rewrite_keys) == 1:
                        rw = rule['handler']['rewrite'][rewrite_keys[0]]

                        # Check that the rewrite attributes match our expectations
                        if rw['regex'] and rw['regex'].value == '.*' \
                            and rw['show'] and rw['show'].value == '0' \
                            and rw['substring'] and rw['substring'].value == '/maintenance/':
                                print "Found"
                                return rule

    raise Exception("rule not found")

def _find_vserver_rule(config, vserver_nick, ):
    vserver = _find_vserver(config, vserver_nick)
    rule = _find_rule(vserver)
    return rule

def update(config_path, disable, vserver_nick, ctk_path):
    import os
    if not os.path.exists(config_path):
        raise Exception('Config path "%s" not found' % config_path)
    elif not os.path.isfile(config_path):
        raise Exception('Config path "%s" is not a file.' % config_path)
    elif not os.access(config_path, os.W_OK):
        raise Exception('Config path "%s" is not writeable.' % config_path)

    # We don't expect CTK to be in the PYTHONPATH env variable, so just squeeze it in here.
    sys.path.insert(0, ctk_path)

    import CTK
    CTK.cfg.file = config_path
    CTK.cfg.load()
    rule = _find_vserver_rule(CTK.cfg, vserver_nick)
    rule['disabled'] = '1' if disable else '0'
    CTK.cfg.save()
    if disable:
        print "Rule disabled"
    else:
        print "Rule enabled"

def main(argv=None):
    if argv is None:
        argv = sys.argv
    # Set up django settings based possibly on first argument.
    if len(argv) <= 1 or argv[1] not in ('enable', 'disable'):
        print "Error: enable/disable not specified"
        show_help()
        return 1

    import getopt, copy
    settings = copy.deepcopy(default_settings)

    if argv[1] == 'enable':
        disable = False
    elif argv[1] == 'disable':
        disable  = True
    settings['disable'] = disable

    try:
        opts, args = getopt.getopt(sys.argv[2:], 'h:c:v:m:r', ['help', 'config_path=', 'vserver_nick=', 'ctk_path='])
    except getopt.GetoptError, err:
        print str(err) # will print something like "option -a not recognized"
        show_help()
        return 1
    for option, value in opts:
        if option in ('-h', '--help'):
            show_help()
            sys.exit(2)
        elif option in ('--config_path', '-c'):
            settings['config_path'] = value
        elif option in ('--vserver_nick', '-v'):
            settings['vserver_nick'] = value
        elif option in ('--ctk_path', '-p'):
            settings['ctk_path'] = value
        else:
            show_help()
            return 1

    print 'Running with settings: '
    print '\n'.join(['\t> %s: %s' % item for item in settings.items()])
    print ""
    update(**settings)
    return 0

if __name__ == "__main__":
    sys.exit(main())
