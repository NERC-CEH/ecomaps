import logging

from ecomaps.lib.base import BaseController, c, request, response, render, session, abort
from ecomaps.services.analysis import AnalysisService
from ecomaps.services.user import UserService

#from pylons import request, response, session, tmpl_context as c, url
#from pylons.controllers.util import abort, redirect

__author__ = 'Phil Jenkins (Tessella)'

log = logging.getLogger(__name__)

class AnalysisController(BaseController):
    """Provides operations for analysis page actions"""

    _user_service = None
    _analysis_service = None

    def __init__(self, user_service=UserService(), analysis_service=AnalysisService()):
        """Constructor for the user controller, takes in any services required
            Params:
                user_service: User service to use within the controller
        """
        super(BaseController, self).__init__()

        self._user_service = user_service
        self._analysis_service = analysis_service
