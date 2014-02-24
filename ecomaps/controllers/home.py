import logging

from ecomaps.lib.base import BaseController, c, request, response, render, session, abort
from ecomaps.services.user import UserService

#from pylons import request, response, session, tmpl_context as c, url
#from pylons.controllers.util import abort, redirect

__author__ = 'Phil Jenkins (Tessella)'

log = logging.getLogger(__name__)

class HomeController(BaseController):
    """Provides operations for home page actions"""

    _user_service = None

    def index(self):
        """Default action, shows the home page"""

        user = self._user_service.get_user_by_username(request.environ['REMOTE_USER'])
        c.name = user.name

        return render("home.html")