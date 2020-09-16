"""EOC Journal XBlock - Utils"""

from edx_rest_api_client.auth import SuppliedJwtAuth
from requests import Session

from .compat import create_jwt_for_user


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


def build_jwt_edx_client(user):
    """
    Returns an edx API client authorized using JWT.
    """

    jwt = create_jwt_for_user(user)
    session = Session()
    session.auth = SuppliedJwtAuth(jwt)
    return session


def ngettext_fallback(text_singular, text_plural, number):
    """ Dummy `ngettext` replacement to make string extraction tools scrape strings marked for translation """
    if number == 1:
        return text_singular
    return text_plural


class NotConnectedToOpenEdX(Exception):
    """
    Exception to raise when not connected to OpenEdX.
    """


class DummyTranslationService(object):  # pylint: disable=too-few-public-methods,useless-object-inheritance
    """
    Dummy drop-in replacement for i18n XBlock service
    """
    _catalog = {}
    gettext = _
    ngettext = ngettext_fallback
