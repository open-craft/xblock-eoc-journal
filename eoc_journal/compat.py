"""
edx-platform dependent code
"""
# pylint: disable=import-error


def create_jwt_for_user(user):
    """
    Wraps openedx.core.djangoapps.oauth_dispatch.jwt.create_jwt_for_user() call
    """
    # test env does not have edx-platform installed. because of this, all edx-platform imports must be
    # kept inside this function so that the test code does not break when importing the module
    from openedx.core.djangoapps.oauth_dispatch.jwt import create_jwt_for_user as openedx_create_jwt_for_user
    return openedx_create_jwt_for_user(user)
