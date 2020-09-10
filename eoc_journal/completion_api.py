"""
A client for completion API for downloading course completion data.
"""
from edx_rest_api_client.exceptions import HttpClientError
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
        url = "{base_url}/course/{course_id}".format(
            base_url=self.api_url,
            course_id=self.course_id,
        )
        try:
            data = self.client.get(url, params=dict(username=self.user.username, **kwargs)).json()
            return data['results'][0]['completion']['percent'] * 100
        except (HttpClientError, IndexError):
            return None
