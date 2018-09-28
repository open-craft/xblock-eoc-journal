"""
A client for completion API for downloading course completion data.
"""
from .base_api_client import BaseApiClient


# pylint: disable=R0903
class CompletionApiClient(BaseApiClient):
    """
    Object builds an API client to make calls to the LMS Grades API.
    """
    API_PATH = '/api/completion-aggregator/v1'

    def get_user_progress(self, **kwargs):
        """
        Fetches and returns the progress percentage for the current user.
        """
        course_api = self.client.course(self.course_id)
        data = course_api.get(username=self.user.username, **kwargs)
        return data['results'][0]['completion']['percent'] * 100
