import simplejson

__author__ = 'Phil Jenkins (Tessella)'


class UserRequest(object):

    def __init__(self):
        self._user_name = ""
        self._password = ""
        self._validation_factors = []
        self._remote_address = ""

    @property
    def username(self):
        return self._user_name
    @username.setter
    def username(self, u):
        self._user_name = u

    @property
    def password(self):
        return self._password
    @password.setter
    def password(self, p):
        self._password = p

    @property
    def remote_address(self):
        return self._remote_address
    @remote_address.setter
    def remote_address(self, r):
        self._remote_address = r

    def to_json(self):

        return simplejson.dumps(
            {
                'username' : self.username,
                'password' : self.password,
                'validation-factors' : dict(validationFactors=[dict(name="remote_address", value=self.remote_address)])
            }
        )