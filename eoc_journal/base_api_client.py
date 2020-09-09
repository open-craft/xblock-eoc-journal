"""
A base client for API integrations.
"""
from builtins import object
from django.conf import settings

from .utils import build_jwt_edx_client


# pylint: disable=R0903
class BaseApiClient(object):
    """
    Base API client abstract class.
    """

    def __init__(self, user, course_id):
        """
        Connect to the REST API.
        """
        self.user = user
        self.course_id = course_id
        self.expires_in = getattr(settings, 'OAUTH_ID_TOKEN_EXPIRATION', 300)
        self.api_url = getattr(settings, 'LMS_ROOT_URL', None)
        # pylint: disable=E1101
        if self.api_url and hasattr(self, 'API_PATH'):
            self.api_url += self.API_PATH
        self.client = None
        self._connect()

    def _connect(self):
        """
        Connect to the REST API, authenticating with a JWT for the current user.
        """
        self.client = build_jwt_edx_client(self.user)
