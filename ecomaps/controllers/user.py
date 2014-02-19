import logging

from ecomaps.lib.base import BaseController, c, request, response, render, session, abort
from ecomaps.services.user import UserService
from ecomaps.services.dataset import DatasetService
from pylons import tmpl_context as c
from formencode import htmlfill

__author__ = 'Chirag Mistry'

log = logging.getLogger(__name__)

class UserController(BaseController):
    """Provides operations for user page actions"""

    _user_service = None
    _dataset_service = None

    def __init__(self, user_service=UserService(), dataset_service=DatasetService()):
        """Constructor for the user controller, takes in any services required
            Params:
                user_service: User service to use within the controller
        """
        super(BaseController, self).__init__()

        self._user_service = user_service
        self._dataset_service = dataset_service

    def view_users(self):

        c.all_users = self._user_service.get_all_users()

        return render('list_of_users.html')