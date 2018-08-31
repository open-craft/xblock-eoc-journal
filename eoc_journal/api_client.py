"""
A wrapper around the Edx API.
"""
from urllib import urlencode

import requests

from django.conf import settings
from edx_rest_api_client.exceptions import HttpClientError

from .utils import build_jwt_edx_client


PROGRESS_IGNORE_COMPONENTS = [
    'discussion-course',
    'group-project',
    'discussion-forum',
    'eoc-journal',

    # GP v2 categories
    'gp-v2-project',
    'gp-v2-activity',
    'gp-v2-stage-basic',
    'gp-v2-stage-completion',
    'gp-v2-stage-submission',
    'gp-v2-stage-team-evaluation',
    'gp-v2-stage-peer-review',
    'gp-v2-stage-evaluation-display',
    'gp-v2-stage-grade-display',
    'gp-v2-resource',
    'gp-v2-video-resource',
    'gp-v2-submission',
    'gp-v2-peer-selector',
    'gp-v2-group-selector',
    'gp-v2-review-question',
    'gp-v2-peer-assessment',
    'gp-v2-group-assessment',
    'gp-v2-static-submissions',
    'gp-v2-static-grade-rubric',
    'gp-v2-project-team',
    'gp-v2-navigator',
    'gp-v2-navigator-navigation',
    'gp-v2-navigator-resources',
    'gp-v2-navigator-submissions',
    'gp-v2-navigator-ask-ta',
    'gp-v2-navigator-private-discussion',
]


def course_components_ids(course, ignored_categories):
    """
    Returns list of course components, excluding components of ignored
    categories.
    """
    def filter_children(children):
        """Returns list of children filtered out by category. """
        return [c['id'] for c in children if c['category'] not in ignored_categories]

    components = []
    for lesson in course['chapters']:
        for sequential in lesson['sequentials']:
            for page in sequential['pages']:
                if 'children' in page:
                    children = filter_children(page['children'])
                    components.extend(children)
    return components


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


def get(url, params=None):
    """
    Sends a GET request to the URL and returns the parsed JSON response.
    """
    key = _get_edx_api_key()

    if key:
        headers = {'X-Edx-Api-Key': key}
        return requests.get(url, headers=headers, params=params).json()
    return None


class ApiClient(object):
    """
    Object builds an API client to make calls to the LMS user API.
    """

    def __init__(self, user, course_id):
        """
        Connect to the REST API.
        """
        self.user = user
        self.course_id = course_id

        # pylint: disable=C0103
        if hasattr(settings, 'LMS_ROOT_URL'):
            self.API_BASE_URL = settings.LMS_ROOT_URL + '/api/server'
        else:
            self.API_BASE_URL = None

        self.expires_in = getattr(settings, 'OAUTH_ID_TOKEN_EXPIRATION', 300)
        self.jwt_edx_client = None
        self.connect_with_jwt()

    def connect_with_jwt(self):
        """
        Connect to the REST API, authenticating with a JWT for the current user.
        """
        self.jwt_edx_client = build_jwt_edx_client(
            self.API_BASE_URL, scopes=['profile', 'email'],
            user=self.user, expires_in=self.expires_in, append_slash=False
        )

    def get_user_engagement_metrics(self):
        """
        Fetches and returns social metrics for the current user in the
        specified course.
        """
        qs_params = {'include_stats': 'true'}
        url = '{base_url}/users/{user_id}/courses/{course_id}/metrics/social/?{query_string}'.format(
            base_url=self.API_BASE_URL,
            user_id=self.user.id,
            course_id=self.course_id,
            query_string=urlencode(qs_params),
        )

        return get(url)

    def _get_course_completions(self):
        """
        Fetches and returns the user's completed modules within the course.
        """
        params = {'page_size': 0, 'user_id': self.user.id}
        url = '{base_url}/courses/{course_id}/completions'.format(
            base_url=self.API_BASE_URL,
            course_id=self.course_id,
        )
        return get(url, params=params)

    def _get_course(self):
        """
        Fetches and returns chapters, sequentials, and pages information about
        the current course.
        """
        try:
            course = self.jwt_edx_client.courses(id=self.course_id).get(depth=5)
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
            base_url=self.API_BASE_URL,
            course_id=self.course_id,
        )

        return get(url, params=params)

    def _get_grades_leader_metrics(self):
        """
        Fetches the user grades metrics.
        """
        params = {'user_id': self.user.id}
        url = '{base_url}/courses/{course_id}/metrics/grades/leaders/'.format(
            base_url=self.API_BASE_URL,
            course_id=self.course_id,
        )
        return get(url, params=params)

    def get_user_progress(self):
        """
        Calculates the progress percentage for the current user.
        """
        completions = self._get_course_completions()
        course = self._get_course()

        if completions is None or course is None:
            return None

        completed_ids = [result['content_id'] for result in completions]

        chapters = [
            module
            for module in course['content'] if module['category'] == 'chapter'
        ]

        for chapter in chapters:
            chapter['sequentials'] = [
                child for child in chapter['children'] if child['category'] == 'sequential'
            ]
            for sequential in chapter['sequentials']:
                sequential['pages'] = [
                    child for child in sequential['children'] if child['category'] == 'vertical'
                ]
        course['chapters'] = chapters

        components_ids = course_components_ids(course, PROGRESS_IGNORE_COMPONENTS)
        actual_completions = set(components_ids).intersection(completed_ids)

        try:
            return round(float(100 * len(actual_completions)) / len(components_ids))
        except ZeroDivisionError:
            return 0

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
