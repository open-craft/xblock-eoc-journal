"""
A client for completion API for downloading course completion data.
"""
from .base_api_client import BaseApiClient


class CompletionApiClient(BaseApiClient):
    """
    Object builds an API client to make calls to the LMS Grades API.
    """

    def __init__(self, user, course_id):
        """
        Connect to the REST API.
        """
        super(CompletionApiClient, self).__init__(user, course_id)
        # pylint: disable=C0103
        if self.API_BASE_URL:
            self.API_BASE_URL += '/api/completion-aggregator/v1'
        self.connect()

    def get_user_progress(self, **kwargs):
        """
        Fetches and returns the progress percentage for the current user.
        """
        course_api = self.client.course(self.course_id)
        data = course_api.get(username=self.user.username, **kwargs)
        return data['results'][0]['completion']['percent'] * 100
