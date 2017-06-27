"""
An XBlock that allows learners to download their activity after they finish their course.
"""

from xblock.core import XBlock
from xblock.fields import Scope, String
from xblock.fragment import Fragment
from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable import StudioEditableXBlockMixin

from .utils import _


loader = ResourceLoader(__name__)


class EOCJournalXBlock(StudioEditableXBlockMixin, XBlock):
    """
    An XBlock that allows learners to download their activity after they finish their course.
    """

    display_name = String(
        display_name=_("Title (display name)"),
        help=_("Title to display"),
        default=_("End of Course Journal"),
        scope=Scope.content,
    )

    key_takeaways_pdf = String(
        display_name=_("Key Takeaways PDF handle"),
        help=_(
            "URL handle of the Key Takeaways PDF file that was uploaded to Studio Files & Uploads section. "
            "Should start with '/static/'. Example: /static/KeyTakeaways.pdf"
        ),
        default="",
        scope=Scope.content,
    )

    editable_fields = (
        "display_name",
        "key_takeaways_pdf",
    )

    def student_view(self, context=None):
        """View shown to students"""
        context = context.copy() if context else {}

        key_takeaways_handle = self.key_takeaways_pdf.strip()
        if key_takeaways_handle:
            context["key_takeaways_pdf_url"] = self._expand_static_url(self.key_takeaways_pdf)

        fragment = Fragment()
        fragment.add_content(
            loader.render_template("templates/eoc_journal.html", context)
        )
        fragment.add_css_url(
            self.runtime.local_resource_url(self, "public/css/eoc_journal.css")
        )
        return fragment

    def _expand_static_url(self, url):
        """
        This is required to make URLs like '/static/takeaways.pdf' work (note: that is the
        only portable URL format for static files that works across export/import and reruns).
        This method is unfortunately a bit hackish since XBlock does not provide a low-level API
        for this.
        """
        if hasattr(self.runtime, 'replace_urls'):
            url = self.runtime.replace_urls('"{}"'.format(url))[1:-1]
        elif hasattr(self.runtime, 'course_id'):
            # edX Studio uses a different runtime for 'studio_view' than 'student_view',
            # and the 'studio_view' runtime doesn't provide the replace_urls API.
            try:
                from static_replace import replace_static_urls  # pylint: disable=import-error
                url = replace_static_urls('"{}"'.format(url), None, course_id=self.runtime.course_id)[1:-1]
            except ImportError:
                pass
        return url
