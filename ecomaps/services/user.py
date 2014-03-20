from ecomaps.model import User
from ecomaps.services.general import DatabaseService, ServiceException

__author__ = 'Phil Jenkins (Tessella)'


class UserService(DatabaseService):
    """Provides operations on User objects"""

    def create(self, username, fullname, email, access_level):
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
            user.access_level = access_level

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
                return None


    def get_user_by_email_address(self, email):
        """ Returns a user with the given email (which should be unique)

            @param email: email address to filter on
        """

        with self.readonly_scope() as session:

            try:
                return session.query(User).filter(User.email == email).one()

            except:
                # We'll get an exception if the user can't be found
                return None



    def get_user_by_id(self, id):
        """ Simply returns the user with the specified ID

            @param id: ID of the user to get
        """

        with self.readonly_scope() as session:

            try:
                return session.query(User).get(id)
            except:
                return None


    def get_all_users(self):
        """Returns an array containing all the users"""

        with self.readonly_scope() as session:

            return session.query(User)


    def update(self, full_name, email, access_level, user_id):
        """ Updates the user specified by the ID passed in

            @param full_name: New friendly name for the user
            @param email: New email address
            @param access_level: New access level
            @param user_id: ID of the user to update
        """
        with self.transaction_scope() as session:

            user = session.query(User).get(user_id)

            user.name = full_name
            user.email = email
            user.access_level = access_level

            session.add(user)


