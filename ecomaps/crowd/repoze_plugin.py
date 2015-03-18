import logging
from ecomaps.crowd.client import CrowdClient, ClientException
from ecomaps.services.user import UserService
from zope.interface import directlyProvides
from repoze.who.interfaces import IChallengeDecider

__author__ = 'Phil Jenkins (Tessella)'

log = logging.getLogger(__name__)

class CrowdRepozePlugin(object):
    """Implementation of a repoze.who plugin which communicates
        with our Crowd client.

        The functions within will be called by repoze.who
        at various stages of the request/response cycle,
        if the who middleware is active and configured with
        this plugin
    """
    _user = None

    def __init__(self):
        """Constructor"""

        # Set up the bits we need
        self._client = CrowdClient()
        self._user_service = UserService()

    def authenticate(self, environ, identity):
        """Authenticates a preauthenticated user against Crowd
            Params:
                environ: The WSGI environment
                identity: Identity dict which contains the username and
                                preauth set to true
            Returns:
                Name of successfully authenticated user, or None
        """
        log.debug("--> Repoze authenticate")

        # Do we have an active session already?
        if 'preauth' in identity:
            return identity['login']
        else:
            return None

    def add_metadata(self, environ, identity):
        """Placeholder to add metadata to the user object
            if we so desire"""
        pass

    def identify(self, environ):
        """Reads the supplied HTTP_REMOTE_USER header from an authentication proxy and
            verifies the user's identity in crowd
            Params:
                environ: The WSGI environment
            Returns:
                A dictionary containing 'login' and 'preauth' entries if
                a valid session is active, otherwise None.
        """
        if 'HTTP_REMOTE_USER' in environ:
            return {
                "login":   environ['HTTP_REMOTE_USER'],
                "preauth": True
            }
        else:
            return None

    def remember(self, environ, identity):
        """Called once authentication is successful, asks us to "remember" the
            details for future identity queries
            Params:
                    environ: WSGI environment
                    identity: May be login/password or login/token
        """
        username = identity['login']

        # Loaded in the details of this user from crowd. Lets check if they need to be
        # stored in the local database
        u = self._user_service.get_user_by_username(username)
        if not u:
            log.debug("Couldn't find %s in Ecomaps DB, creating user" % username)
            user_info = self._client.get_user_info(username)
            self._user_service.create(username,
                                      user_info['first-name'],
                                      user_info['last-name'],
                                      user_info['email'],
                                      None)
        return None

    def forget(self, environ, identity):
        """We are relying on the username details being sent in via 
            an authentication proxy. As such we can not forget them.

            Just empty array
        """
        return []

def crowd_challenge_decider(environ, status, headers):
    """Inspects each request and decides whether to challenge for authentication
    this is an implementation for repoze.who
        Params:
            environ: WSGI environment
            status: The HTTP status message
            headers: Any HTTP headers in the request
        Returns:
            True if a challenge should be made, otherwise False
    """

    # Are we logging in anyway? So we don't get caught in an infinite loop,
    # don't challenge for the login controller
    if 'login' in environ.get('PATH_INFO'):
        return False
    else:
        # The middleware should populate REMOTE_USER
        # if a valid user is logged in, so raise a challenge
        # if this is not found
        return (status.startswith('401') or
                environ.get('REMOTE_USER') is None)

# Let zope know we're a challenge decider
directlyProvides(crowd_challenge_decider, IChallengeDecider)
