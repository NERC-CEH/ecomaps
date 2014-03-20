import formencode

__author__ = 'Chirag Mistry (Tessella)'


class UpdateUserForm(formencode.Schema):

    allow_extra_fields = True
    filter_extra_fields = False

    name = formencode.validators.String(not_empty=True)
    email = formencode.validators.Email(not_empty=True)
    is_admin = formencode.validators.Bool()

class CreateUserForm(UpdateUserForm):
    """Used to validate data from the Create New User page"""

    allow_extra_fields = False
    filter_extra_fields = True

    user_name = formencode.validators.String(not_empty=True)