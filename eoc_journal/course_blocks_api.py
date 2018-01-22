"""
An XBlock that allows learners to download their activity after they finish their course.
"""

from django.conf import settings

from .utils import build_jwt_edx_client


class CourseBlocksApiClient(object):
    """
    Object builds an API client to make calls to the LMS Grades API.
    """

    if hasattr(settings, 'LMS_ROOT_URL'):
        API_BASE_URL = settings.LMS_ROOT_URL + '/api/courses/v1'
    else:
        API_BASE_URL = None

    def __init__(self, user, course_id):
        """
        Connect to the REST API.
        """
        self.user = user
        self.course_id = course_id
        self.expires_in = getattr(settings, 'OAUTH_ID_TOKEN_EXPIRATION', 300)
        self.client = None
        self.connect()

    def connect(self):
        """
        Connect to the REST API, authenticating with a JWT for the current user.
        """
        scopes = ['profile', 'email']

        self.client = build_jwt_edx_client(
            self.API_BASE_URL, scopes, self.user,
            self.expires_in, append_slash=True
        )

    def get_blocks(self, **kwargs):
        """
        Fetches and returns blocks from the Course API.
        """
        return self.client.blocks.get(course_id=self.course_id, **kwargs)
