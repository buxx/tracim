# -*- coding: utf-8 -*-
import inspect

import tg
from tg import AppConfig
from tg.configuration.app_config import config, log, DispatchingConfigWrapper as BaseDispatchingConfigWrapper
from tg.util import DottedFileNameFinder, Bunch

from tracim.lib.auth.wrapper import AuthConfigWrapper
from tg.request_local import config as reqlocal_config

class DispatchingConfigWrapper(BaseDispatchingConfigWrapper):

    def __setattr__(self, key, value):

        if key == 'tg.app_globals' and value is None:
            with open('/tmp/debug.txt', 'a') as f:
                print('tg.app_globals set to None', file=f)
        if key == 'tg.app_globals':
            with open('/tmp/debug.txt', 'a') as f:
                print('tg.app_globals set to %s' % value, file=f)

        self.config_proxy.current_conf()[key] = value

tg.config = DispatchingConfigWrapper(reqlocal_config)



class TracimAppConfig(AppConfig):
    """
    Tracim specific config processes.
    """

    def after_init_config(self, conf):
        AuthConfigWrapper.wrap(conf)
        #  Fix an tg2 strange thing: auth_backend is set in config, but instance
        #  of AppConfig has None in auth_backend attr
        self.auth_backend = conf['auth_backend']
        self.sa_auth = conf.get('sa_auth')

    def setup_helpers_and_globals(self):
        """Add helpers and globals objects to the config.

        Override this method to customize the way that ``app_globals`` and ``helpers``
        are setup.
        """

        with open('/tmp/debug.txt', 'a') as f:
            #print('NEW setup_helpers_and_globals (inspect: %s)' % str(inspect.stack()[1][3]), file=f)

            gclass = getattr(self, 'app_globals', None)
            if gclass is None:
                #print('gclass is None', file=f)
                try:
                    # if hasattr(self.package, 'lib'):
                    #     print('package have lib', file=f)
                    # if hasattr(self.package.lib, 'app_globals'):
                    #     print('package have lib.app_globals', file=f)
                    # if hasattr(self.package.lib.app_globals, 'Globals'):
                    #     print('package have lib.app_globals.Globals', file=f)
                    g = self.package.lib.app_globals.Globals()
                except AttributeError:
                    #print('app_globals not provided', file=f)
                    log.warn('app_globals not provided and lib.app_globals.Globals class is not available.')
                    g = Bunch()
            else:
                #print('gclass already exist (%s)' % str(gclass), file=f)
                g = gclass()


            g.dotted_filename_finder = DottedFileNameFinder()
            config['tg.app_globals'] = g

            if config.get('tg.pylons_compatible', True):
                config['pylons.app_globals'] = g

            h = getattr(self, 'helpers', None)
            if h is None:
                try:
                    h = self.package.lib.helpers
                except AttributeError:
                    log.warn('helpers not provided and lib.helpers is not available.')
                    h = Bunch()
            config['helpers'] = h

            # print('config.helpers: %s' % config['helpers'], file=f)
            # print('config.tg.app_globals: %s' % config['tg.app_globals'], file=f)
            #
            # print('END setup_helpers_and_globals', file=f)
            # print('', file=f)
