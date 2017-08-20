#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
__license__   = 'GPL v3'
__copyright__ = '2011, Jason Kulatunga <jason@quietthyme.com>'
__docformat__ = 'restructuredtext en'

import traceback, os, urllib2, sys, logging

# The class that sets and stores the user configured preferences
from calibre_plugins.quietthyme.quietthymedeviceplugin import QuietthymeDevicePlugin

# The class that sets and stores the user configured preferences
from calibre_plugins.quietthyme.config import prefs
from calibre_plugins.quietthyme import version
#configure logger
logger = logging.getLogger(__name__)
logger.propagate = False
logger.setLevel(logging.WARN)

ch = logging.StreamHandler()
ch.setLevel(logging.WARN)
# create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)

if prefs['debug_mode']:
    logger.setLevel(logging.DEBUG)
    ch.setLevel(logging.DEBUG)
    #add log to file channel.
    #TODO: make this os agnostic using tempfile.gettempdir() and path.
    fh = logging.FileHandler('/tmp/plugin.quietthyme.calibre.log', 'w')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

# add ch to logger
logger.addHandler(ch)

class QuietthymePlugin(QuietthymeDevicePlugin):
    '''
    This class is a simple wrapper that provides information about the actual
    plugin class. The actual interface plugin class is called InterfacePlugin
    and is defined in the ui.py file, as specified in the actual_plugin field
    below.

    The reason for having two classes is that it allows the command line
    calibre utilities to run without needing to load the GUI libraries.
    '''
    name                = 'QuietThyme Device Plugin'
    description         = 'QuietThyme storage plugin for Calibre'
    supported_platforms = ['windows', 'osx', 'linux']
    author              = 'Jason Kulatunga'
    version             = version.version_tuple
    minimum_calibre_version = (0, 7, 53)
    gui_name = 'QuietThyme Storage'

    def is_customizable(self):
        logger.debug(sys._getframe().f_code.co_name)
        return True

    def cli_main(self, argv):
        '''
        This method is the main entry point for your plugins command line interface. It is called when the user does:
        calibre-debug -r “Plugin Name”. Any arguments passed are present in the args variable.
        :param args:
        :return:
        '''
        from calibre_plugins.quietthyme.cli import main as cli_main
        cli_main(argv[1:],usage='%prog --run-plugin "'+self.name+'" --')

    def config_widget(self):
        '''
        Implement this method and :meth:`save_settings` in your plugin to
        use a custom configuration dialog.

        This method, if implemented, must return a QWidget. The widget can have
        an optional method validate() that takes no arguments and is called
        immediately after the user clicks OK. Changes are applied if and only
        if the method returns True.

        If for some reason you cann1=-0-ot perform the configuration at this time,
        return a tuple of two strings (message, details), these will be
        displayed as a warning dialog to the user and the process will be
        aborted.

        The base class implementation of this method raises NotImplementedError
        so by default no user configuration is possible.
        '''
        # It is important to put this import statement here rather than at the
        # top of the module as importing the config class will also cause the
        # GUI libraries to be loaded, which we do not want when using calibre
        # from the command line
        logger.debug(sys._getframe().f_code.co_name)

        from calibre_plugins.quietthyme.config import ConfigWidget
        return ConfigWidget()
