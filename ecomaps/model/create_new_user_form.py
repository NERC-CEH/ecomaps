import formencode

__author__ = 'Chirag Mistry (Tessella)'


class CreateUserForm(formencode.Schema):
    """Used to validate data from the Create New User page"""

    allow_extra_fields = False
    filter_extra_fields = True

    name = formencode.validators.String(not_empty=True)
    username = formencode.validators.String(not_empty=True)
    email = formencode.validators.Email(not_empty=True)