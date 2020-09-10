"""
A wrapper around the Edx API.
"""
# pylint: disable=C0413,C0411
from future import standard_library  # noqa
standard_library.install_aliases()  # noqa

from urllib.parse import urlencode

import requests
from django.conf import settings
from edx_rest_api_client.exceptions import HttpClientError

from .base_api_client import BaseApiClient


class ApiClient(BaseApiClient):
    """
    Object builds an API client to make calls to the LMS user API.
    """
    API_PATH = '/api/server'

    @staticmethod
    def _get_edx_api_key():
        """
        Returns the EDX_API_KEY from the django settings.
        If key is not set, returns None.

        This key should never be sent to the client, as it is only used to
        communicate with the api server.
        """
        if hasattr(settings, 'EDX_API_KEY'):
            return settings.EDX_API_KEY
        return None

    @staticmethod
    def _get(url, params=None):
        """
        Sends a GET request to the URL and returns the parsed JSON response.
        """
        key = ApiClient._get_edx_api_key()

        if key:
            headers = {'X-Edx-Api-Key': key}
            return requests.get(url, headers=headers, params=params).json()
        return None

    def get_user_engagement_metrics(self):
        """
        Fetches and returns social metrics for the current user in the
        specified course.
        """
        qs_params = {'include_stats': 'true'}
        url = '{base_url}/users/{user_id}/courses/{course_id}/metrics/social/?{query_string}'.format(
            base_url=self.api_url,
            user_id=self.user.id,
            course_id=self.course_id,
            query_string=urlencode(qs_params),
        )

        return self._get(url)

    def _get_course(self):
        """
        Fetches and returns chapters, sequentials, and pages information about
        the current course.
        """
        try:
            course = self.client.get(self.api_url + '/courses', params={"depth": 5}).json()
        except HttpClientError:
            return None

        return course

    def _get_completion_leader_metrics(self):
        """
        Fetches and returns user completion metrics.
        """
        params = {
            'skipleaders': True,
            'user_id': self.user.id,
        }

        url = '{base_url}/courses/{course_id}/metrics/completions/leaders/'.format(
            base_url=self.api_url,
            course_id=self.course_id,
        )

        return self._get(url, params=params)

    def _get_grades_leader_metrics(self):
        """
        Fetches the user grades metrics.
        """
        params = {'user_id': self.user.id}
        url = '{base_url}/courses/{course_id}/metrics/grades/leaders/'.format(
            base_url=self.api_url,
            course_id=self.course_id,
        )
        return self._get(url, params=params)

    def get_cohort_average_progress(self):
        """
        Fetches and returns cohort average progress.
        """
        data = self._get_completion_leader_metrics()

        if data:
            return data.get('course_avg', None)
        return None

    def get_user_proficiency(self):
        """
        Fetches and returns the user's and average course proficiency scores.
        """
        data = self._get_grades_leader_metrics()
        if data is None:
            return None

        user_grade = data.get('user_grade')
        course_avg = data.get('course_avg')
        if user_grade is None or course_avg is None:
            return None

        user_grade = int(round(user_grade * 100.0))
        course_avg = int(round(course_avg * 100.0))
        return dict(user=user_grade, cohort_average=course_avg)
