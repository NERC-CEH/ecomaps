import logging

from ecomaps.lib.base import BaseController, c, request, response, render, session, abort
from ecomaps.services.user import UserService
from ecomaps.services.dataset import DatasetService
from pylons import tmpl_context as c
from formencode import htmlfill
import formencode
from ecomaps.model.create_new_user_form import CreateUserForm

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
        """Allow user to see all users of the system
        """
        c.all_users = self._user_service.get_all_users()

        return render('list_of_users.html')

    def create(self):
        """Create a new user
        """
        if not request.POST:

            return render('new_user.html')

        schema = CreateUserForm()
        c.form_errors = {}

        if request.POST:

            try:
                c.form_result = schema.to_python(request.params)

            except formencode.Invalid, error:

                c.form_result = error.value
                c.form_errors = error.error_dict or {}
                html = render('new_user.html')
                return htmlfill.render(html,
                                       defaults=c.form_result,
                                       errors=c.form_errors,
                                       auto_error_formatter=custom_formatter)
            else:

                self._user_service.create(c.form_result.get('name'),
                                          c.form_result.get('username'),
                                          c.form_result.get('email'),)
                c.all_users = self._user_service.get_all_users()
                return render('list_of_users.html')


def custom_formatter(error):
    """Custom error formatter"""
    return '<span class="help-inline">%s</span>' % (
        htmlfill.html_quote(error)
    )