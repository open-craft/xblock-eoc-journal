"""
An XBlock that allows learners to download their activity after they finish their course.
"""

from xblock.core import XBlock
from xblock.fields import Scope, String, List
from xblock.fragment import Fragment
from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable import StudioEditableXBlockMixin

from .course_blocks_api import CourseBlocksApiClient
from .utils import _

try:
    from django.contrib.auth.models import User
except ImportError:
    User = None


loader = ResourceLoader(__name__)


def provide_pb_answer_list(xblock_instance):
    """
    Returns a list of dicts containing information about pb-answer
    blocks present in current course.

    Used as a list value provider for the `selected_pb_answer_blocks`
    field in the Studio.
    """
    blocks = xblock_instance.list_pb_answers(all_blocks=True)
    result = []
    for block in blocks:
        block_name = block['display_name'] or block['name']
        label = ' / '.join([block['section'], block['subsection'], block['unit'], block_name])
        result.append({
            'display_name': label,
            'value': block['id'],
        })
    return result


@XBlock.needs('user')
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

    selected_pb_answer_blocks = List(
        display_name=_("Problem Builder Freeform Answers"),
        help=_("Select Problem Builder Freeform Answer components which you want to include in the report."),
        default=[],
        scope=Scope.content,
        list_style='set',
        list_values_provider=provide_pb_answer_list,
    )

    editable_fields = (
        'display_name',
        'key_takeaways_pdf',
        'selected_pb_answer_blocks',
    )

    def student_view(self, context=None):
        """
        View shown to students.
        """
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

    def list_pb_answers(self, all_blocks=False):
        """
        Returns a list of dicts with info about all problem builder's pb-answer
        blocks present in the current coures.

        The items are ordered in the order they appear in the course.
        """
        response = self._fetch_pb_answer_blocks(all_blocks)
        blocks = response['blocks']
        course_block = blocks[response['root']]
        result = []
        for section_id in course_block.get('children', []):
            section_block = blocks[section_id]
            for subsection_id in section_block.get('children', []):
                subsection_block = blocks[subsection_id]
                for unit_id in subsection_block.get('children', []):
                    unit_block = blocks[unit_id]
                    for pb_answer_id in unit_block.get('children', []):
                        pb_answer_block = blocks[pb_answer_id]
                        result.append({
                            'section': section_block['display_name'],
                            'subsection': subsection_block['display_name'],
                            'unit': unit_block['display_name'],
                            'id': pb_answer_block['id'],
                            'name': pb_answer_block['student_view_data']['name'],
                            'display_name': pb_answer_block['display_name'],
                        })
        return result

    def _get_current_user(self):
        """
        Returns django.contrib.auth.models.User instance corresponding to the current user.
        """
        xblock_user = self.runtime.service(self, 'user').get_current_user()
        user_id = xblock_user.opt_attrs['edx-platform.user_id']
        user = User.objects.get(pk=user_id)
        return user

    def _fetch_pb_answer_blocks(self, all_blocks=False):
        """
        Fetches blocks from the Course API. Results are currently limited to
        course, chapter, sequential, vetcial, and pb-answer blocks.

        If `all_blocks` is True, returns all blocks, including those that are
        visible only to specific learners (cohort groups, randomized content...).
        Only staff users can request `all_blocks`.
        """
        user = self._get_current_user()
        course_id = unicode(getattr(self.runtime, 'course_id', 'course_id'))
        client = CourseBlocksApiClient(user, course_id)
        response = client.get_blocks(
            all_blocks=all_blocks,
            depth='all',
            requested_fields='student_view_data,children',
            student_view_data='pb-answer',
            block_types_filter='pb-answer,vertical,sequential,chapter,course',
            username=user.username,
        )
        return response

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
