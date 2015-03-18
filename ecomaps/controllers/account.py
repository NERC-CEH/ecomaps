import logging
import formencode

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from webob.exc import HTTPFound

from ecomaps.lib.base import BaseController, render
from repoze.who.api import get_api
from ecomaps.model.loginform import LoginForm
from formencode import htmlfill
from ecomaps.services.general import ServiceException
from ecomaps.services.user import UserService

__author__ = 'Phil Jenkins (Tessella)'

log = logging.getLogger(__name__)

class AccountController(BaseController):
    """Encapsulates operations on a user's ecomaps account"""

    _user_service = None

    def __init__(self, user_service=UserService()):
        """Constructor for the user controller, takes in any services required
            Params:
                user_service: User service to use within the controller
        """
        super(BaseController, self).__init__()

        self._user_service = user_service


    def login(self):
        """Action for the 'log in' view"""
        came_from = request.params.get('came_from', '/')

        return redirect('/sso/login?success=' + came_from)

def custom_formatter(error):
    """Custom error formatter"""
    return '<span class="help-inline">%s</span>' % (
        htmlfill.html_quote(error)
    )
