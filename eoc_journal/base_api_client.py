"""
A base client for API integrations.
"""
from abc import ABCMeta
from django.conf import settings

from .utils import build_jwt_edx_client


class BaseApiClient(object):
    """
    Base API client abstract class.
    """
    __metaclass__ = ABCMeta

    def __init__(self, user, course_id):
        """
        Connect to the REST API.
        """
        self.user = user
        self.course_id = course_id
        self.expires_in = getattr(settings, 'OAUTH_ID_TOKEN_EXPIRATION', 300)
        self.API_BASE_URL = getattr(settings, 'LMS_ROOT_URL', None)
        self.client = None

    def connect(self):
        """
        Connect to the REST API, authenticating with a JWT for the current user.
        """
        scopes = ['profile', 'email']

        self.client = build_jwt_edx_client(
            self.API_BASE_URL, scopes, self.user,
            self.expires_in, append_slash=True
        )
