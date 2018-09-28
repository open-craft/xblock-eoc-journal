"""
An XBlock that allows learners to download their activity after they finish their course.
"""

from .base_api_client import BaseApiClient


# pylint: disable=R0903
class CourseBlocksApiClient(BaseApiClient):
    """
    Object builds an API client to make calls to the LMS Grades API.
    """
    API_PATH = '/api/courses/v1'

    def get_blocks(self, **kwargs):
        """
        Fetches and returns blocks from the Course API.
        """
        return self.client.blocks.get(course_id=self.course_id, **kwargs)
