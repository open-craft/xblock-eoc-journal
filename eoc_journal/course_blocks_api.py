"""
An XBlock that allows learners to download their activity after they finish their course.
"""

from .base_api_client import BaseApiClient


class CourseBlocksApiClient(BaseApiClient):
    """
    Object builds an API client to make calls to the LMS Grades API.
    """

    def __init__(self, user, course_id):
        """
        Connect to the REST API.
        """
        super(CourseBlocksApiClient, self).__init__(user, course_id)
        # pylint: disable=C0103
        if self.API_BASE_URL:
            self.API_BASE_URL += '/api/courses/v1'
        self.connect()

    def get_blocks(self, **kwargs):
        """
        Fetches and returns blocks from the Course API.
        """
        return self.client.blocks.get(course_id=self.course_id, **kwargs)
