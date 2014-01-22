import logging
import formencode

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from webob.exc import HTTPFound

from ecomaps.lib.base import BaseController, render
from repoze.who.api import get_api
from ecomaps.model.loginform import LoginForm
from formencode import htmlfill

__author__ = 'Phil Jenkins (Tessella)'

log = logging.getLogger(__name__)

class AccountController(BaseController):

    def login(self):
        identity = request.environ.get('REMOTE_USER')
        came_from = request.params.get('came_from', None)
        message = request.params.get('message', None)

        if identity is not None:
            if came_from:
                redirect(url(str(came_from)))

        return render('login.mako', extra_vars={'came_from': came_from, 'message': message})

    def loggedin(self):
        return "You are logged in"

    def dologin(self):
        who_api = get_api(request.environ)
        message = ''
        came_from = request.params.get('came_from')

        if came_from is u'':
            came_from = 'loggedin'

        schema = LoginForm()
        c.form_errors = {}

        if request.POST:

            try:
                c.form_result = schema.to_python(request.params)
            except formencode.Invalid, error:
                c.form_result = error.value
                c.form_errors = error.error_dict or {}
            else:
                authenticated, headers = who_api.login(c.form_result)

                if authenticated:
                    return HTTPFound(location=came_from, headers=headers)

                message = 'Login failed: check your username and/or password.'
        else:
             # Forcefully forget any existing credentials.
            _, headers = who_api.login({})

            request.response_headerlist = headers
        if 'REMOTE_USER' in request.environ:
            del request.environ['REMOTE_USER']

        return htmlfill.render(
            render('login.mako', extra_vars={'came_from': came_from, 'message': message}),
            defaults=c.form_result,
            errors=c.form_errors
        )

    def logout(self):

        who_api = get_api(request.environ)
        headers = who_api.logout()

        return HTTPFound(location='/', headers=headers)