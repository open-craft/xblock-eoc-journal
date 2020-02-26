"""EOC Journal XBlock - Utils"""

from edx_rest_api_client.client import EdxRestApiClient


def normalize_id(key):
    """
    Helper method to normalize a key to avoid issues where some keys have version/branch and others don't.
    e.g. self.scope_ids.usage_id != self.runtime.get_block(self.scope_ids.usage_id).scope_ids.usage_id
    """
    if hasattr(key, "for_branch"):
        key = key.for_branch(None)
    if hasattr(key, "for_version"):
        key = key.for_version(None)
    return key


def _(text):
    """
    Dummy `gettext` replacement to make string extraction tools scrape strings marked for translation.
    """
    return text


def build_jwt_edx_client(url, scopes, user, expires_in, append_slash=True):
    """
    Returns an edx API client authorized using JWT.
    """

    # test env does not have edx-platform installed. because of this, all edx-platform imports must be
    # kept inside this function so that the test code does not break when importing the module
    from openedx.core.djangoapps.oauth_dispatch.jwt import create_jwt_for_user  # pylint: disable=import-error
    jwt = create_jwt_for_user(user)
    return EdxRestApiClient(url, append_slash=append_slash, jwt=jwt)


class NotConnectedToOpenEdX(Exception):
    """
    Exception to raise when not connected to OpenEdX.
    """
    pass
