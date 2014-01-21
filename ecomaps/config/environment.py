"""Pylons environment configuration"""
import os

from genshi.template import TemplateLoader
from pylons.configuration import PylonsConfig

import cowsclient.lib.app_globals as app_globals
import cowsclient.lib.helpers
from cowsclient.config.routing import make_map

def load_environment(global_conf, app_conf):
    """Configure the Pylons environment via the ``pylons.config``
    object
    """
    config = PylonsConfig()

    # Pylons paths
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = dict(root=root,
                 controllers=os.path.join(root, 'controllers'),
                 static_files=os.path.join(root, 'public'),
                 templates=[os.path.join(root, 'templates')])

    # Initialize config with the basic options
    config.init_app(global_conf, app_conf, package='cowsclient', paths=paths)

    config['routes.map'] = make_map(config)
    config['pylons.app_globals'] = app_globals.Globals(config)
    config['pylons.h'] = cowsclient.lib.helpers

    config['pylons.app_globals'].genshi_loader = TemplateLoader(
        paths['templates'], auto_reload=True)

    # CONFIGURATION OPTIONS HERE (note: all config options will override
    # any Pylons config options)
    config['pylons.strict_tmpl_context'] = False

    return config
