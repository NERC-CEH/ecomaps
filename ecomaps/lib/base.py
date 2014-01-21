"""The base Controller API

Provides the BaseController class for subclassing, and other objects
utilized by Controllers.
"""
from pylons import cache, config, request, response, session
from pylons import tmpl_context as c
from pylons.controllers import WSGIController
from pylons.controllers.util import abort, etag_cache, redirect
from pylons.decorators import jsonify, validate
from pylons.i18n import ungettext, N_
from pylons.templating import render_genshi as render
from paste import httpexceptions
import paste.request

import cowsclient.lib.helpers as h
import cowsclient.model as model

# To simplify upgrading to Pylons-1.0
app_globals = config['pylons.app_globals']

class BaseController(WSGIController):

    def __call__(self, environ, start_response):
        """Invoke the Controller"""

        # Redirect to a canonical form of the URL if necessary.
        self._redirect_noncanonical_url(environ)

        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']

        return WSGIController.__call__(self, environ, start_response)

    def _redirect_noncanonical_url(self, environ):
        """Convert the URL to the form /{controller}/ if the request URL is of
        the form /{controller} and redirect.
        """
        if environ['PATH_INFO'].lstrip('/').find('/') < 0:
            environ['PATH_INFO'] += '/'
            url = paste.request.construct_url(environ)
            raise httpexceptions.HTTPMovedPermanently(url)

# Include the '_' function in the public names
__all__ = [__name for __name in locals().keys() if not __name.startswith('_') \
           or __name == '_']
