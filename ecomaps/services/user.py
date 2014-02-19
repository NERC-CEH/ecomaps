from ecomaps.model import User
from ecomaps.services.general import DatabaseService, ServiceException

__author__ = 'Phil Jenkins (Tessella)'


class UserService(DatabaseService):
    """Provides operations on User objects"""

    def create(self, username, fullname, email):
        """Creates a user (if the user doesn't already exist)
            Params:
                username: The login name of the user
                fullname: The user's friendly name
                email: User's email address
        """

        with self.transaction_scope() as session:

            user = User()
            user.username = username
            user.name = fullname
            user.email = email

            session.add(user)

    def get_user_by_username(self, username):
        """Gets a single user by their username
            Params:
                username: Login name of the user to retrieve
        """

        with self.readonly_scope() as session:

            try:
                return session.query(User).filter(User.username == username).one()

            except:
                # We'll get an exception if the user can't be found
                raise ServiceException()

    def get_all_users(self):
        """Returns an array containing all the users"""

        with self.readonly_scope() as session:

            return session.query(User)



