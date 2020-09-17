"""
An XBlock that allows learners to download their activity after they finish their course.
"""
# pylint: disable=wrong-import-position,wrong-import-order,no-name-in-module
from future import standard_library  # noqa
standard_library.install_aliases()  # noqa

import json
from builtins import str
from collections import OrderedDict
from io import BytesIO
from urllib.parse import urljoin

import pkg_resources
import webob
from django import utils
from django.conf import settings
from lxml import html
from lxml.etree import ParserError, XMLSyntaxError
from lxml.html.clean import clean_html
from opaque_keys.edx.keys import CourseKey, UsageKey
from problem_builder.models import Answer
from reportlab.lib import pagesizes
from reportlab.lib.colors import Color
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.platypus.flowables import HRFlowable
from xblock.core import XBlock
from xblock.fields import Boolean, List, Scope, String
from xblock.fragment import Fragment
from xblockutils.resources import ResourceLoader
from xblockutils.studio_editable import StudioEditableXBlockMixin

from .api_client import ApiClient
from .completion_api import CompletionApiClient
from .course_blocks_api import CourseBlocksApiClient
from .pdf_generator import get_style_sheet
from .utils import DummyTranslationService, _, normalize_id


try:
    from django.contrib.auth.models import User  # pylint: disable=import-outside-toplevel,ungrouped-imports
except ImportError:
    User = None  # pylint: disable=C0103


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


@XBlock.needs("i18n")
@XBlock.needs('user')
class EOCJournalXBlock(StudioEditableXBlockMixin, XBlock):
    """
    An XBlock that allows learners to download their activity after they finish their course.
    """

    display_name = String(
        display_name=_("Title (display name)"),
        help=_("Title to display"),
        default=_("Course Journal"),
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

    pdf_report_title = String(
        display_name=_("PDF Title"),
        help=_("Title of the PDF report. Leave blank to use the course title."),
        default=None,
        scope=Scope.content,
    )

    pdf_report_link_heading = String(
        display_name=_("PDF Report Link heading"),
        help=_("The heading text to display above the link for downloading the PDF Report."),
        default=_("PDF Report"),
        scope=Scope.content,
    )

    pdf_report_link_text = String(
        display_name=_("PDF Report Link text"),
        help=_("The text to display in the link for downloading the PDF Report."),
        default=_("Download PDF"),
        scope=Scope.content,
    )

    display_metrics_section = Boolean(
        display_name=_("Display User Metrics"),
        help=_("Would you like to display progress, proficiency and engagement metrics in the XBlock view in LMS?"),
        default=False,
        scope=Scope.content,
    )

    display_key_takeaways_section = Boolean(
        display_name=_("Display Key Takeaways section"),
        help=_("Would you like to display Key Takeaways section in the XBlock view in LMS?"),
        default=False,
        scope=Scope.content,
    )

    display_answers = Boolean(
        display_name=_("Display answers"),
        help=_("Would you like to display free text answers in the XBlock view in LMS?"),
        default=False,
        scope=Scope.content,
    )

    custom_font = String(
        display_name=_("Default Font"),
        help=_("Studio static URL to a custom font file to be used for PDF report. "
               "Example: \"/static/myfont.ttf\". Leave empty to use default fonts. "
               "You can upload custom TTF font files from the Content - Files "
               "& Uploads page."),
        default=None,
        scope=Scope.settings,
    )

    editable_fields = (
        'display_name',
        'key_takeaways_pdf',
        'selected_pb_answer_blocks',
        'pdf_report_title',
        'pdf_report_link_heading',
        'pdf_report_link_text',
        'display_metrics_section',
        'display_key_takeaways_section',
        'display_answers',
        'custom_font',
    )

    @property
    def i18n_service(self):
        """ Obtains translation service """
        return self.runtime.service(self, "i18n") or DummyTranslationService()

    def student_view_data(self, context=None):
        """
        JSON representation of data shown to students.
        """
        context = context.copy() if context else {}

        context["display_name"] = self.display_name
        context["display_answers"] = self.display_answers
        context["display_user_metrics"] = self.display_metrics_section

        context["display_key_takeaways"] = self.display_key_takeaways_section
        if self.display_key_takeaways_section:
            key_takeaways_handle = self.key_takeaways_pdf.strip()
            if key_takeaways_handle:
                context["key_takeaways_pdf_url"] = self._expand_static_url(
                    url=self.key_takeaways_pdf,
                    absolute=True,
                )

        context["pdf_report_url"] = self._make_url_absolute(
            self.runtime.handler_url(self, "serve_pdf")
        )
        context["pdf_report_link_heading"] = self.pdf_report_link_heading
        context["pdf_report_link_text"] = self.pdf_report_link_text

        return context

    def _get_user_state(self):
        """
        Return student-specific data in dictionary.
        """
        state = {
            "answer_sections": self.list_user_pb_answers_by_section(),
        }

        if self.display_metrics_section:
            state["progress"] = self.get_progress_metrics()
            state["proficiency"] = self.get_proficiency_metrics()
            state["engagement"] = self.get_engagement_metrics()
        return state

    @XBlock.handler
    def student_view_user_state(self, request, suffix=''):  # pylint: disable=unused-argument
        """
        XBlock handler to return student-specific block data as JSON.
        """
        return webob.Response(
            body=json.dumps(self._get_user_state()),
            charset='UTF-8',
            content_type='application/json',
        )

    def student_view(self, context=None):
        """
        View shown to students.
        """
        context = self.student_view_data(context=context)
        context.update(self._get_user_state())

        fragment = Fragment()
        fragment.add_content(
            loader.render_django_template('templates/eoc_journal.html',
                                          context=context,
                                          i18n_service=self.i18n_service)
        )
        fragment.add_css_url(
            self.runtime.local_resource_url(self, "public/css/eoc_journal.css")
        )
        fragment.add_javascript(self.get_translation_content())
        fragment.add_javascript_url(
            self.runtime.local_resource_url(self, "public/js/eoc_journal.js")
        )
        fragment.initialize_js("EOCJournalXBlock")
        return fragment

    @staticmethod
    def resource_string(path):
        """Handy helper for getting resources."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def get_translation_content(self):
        """
        Returns JS content containing translations for user's language.
        """
        try:
            return self.resource_string('public/js/translations/{lang}/textjs.js'.format(
                lang=utils.translation.to_locale(utils.translation.get_language()),
            ))
        except IOError:
            return self.resource_string('public/js/translations/en/textjs.js')

    @XBlock.handler
    def serve_pdf(self, request, _suffix):
        """
        Builds and serves a PDF document containing user's freeform answers.
        """
        font_path = self._expand_static_url(self.custom_font, absolute=True) if self.custom_font else None
        styles = get_style_sheet(font_url=font_path)
        pdf_buffer = BytesIO()

        report_header_name = self.pdf_report_title or self._get_course_name()
        document = SimpleDocTemplate(pdf_buffer, pagesize=pagesizes.letter, title=report_header_name)
        story = [
            Paragraph(report_header_name, styles["Title"]),
        ]

        answer_sections = self.list_user_pb_answers_by_section()
        for section in answer_sections:
            story.append(Spacer(0, 16))
            story.append(Paragraph(section["name"], styles["h1"]))
            for question in section["questions"]:
                story.append(Paragraph(question["question"], styles["h2"]))
                story.append(Paragraph(question["answer"], styles["Normal"]))
                story.append(HRFlowable(color=Color(0, 0, 0, 0.1), width='100%', spaceBefore=5, spaceAfter=10))

        document.build(story)
        pdf_buffer.seek(0)
        pdf = pdf_buffer.read()

        response = webob.Response(
            body=pdf,
            content_type='application/pdf',
        )

        return response

    def list_user_pb_answers_by_section(self):
        """
        Returns a list of dicts with pb-answers grouped by section.
        """
        # Get the selected blocks and their answers
        blocks = self.list_pb_answers()
        blocks = [b for b in blocks if b['id'] in self.selected_pb_answer_blocks]
        course_id = self._get_course_id()
        user_id = self._get_current_anonymous_user_id()
        answers_names = [block['name'] for block in blocks]

        answers = Answer.objects.filter(  # pylint: disable=no-member
            course_key=course_id,
            student_id=user_id,
            name__in=answers_names
        )

        if answers.count() > 0:
            # Map answer names to student inputs
            students_inputs = {a.name: a.student_input for a in answers}

            # Group answers by section
            answers = OrderedDict()

            for block in blocks:
                name = block['name']
                section = block['section']

                if section not in answers:
                    answers[section] = []

                try:
                    parsed_question = html.fromstring(block['question'])
                    question = clean_html(parsed_question).text_content()
                except (XMLSyntaxError, ParserError):
                    question = block['question']

                answers[section].append({
                    'answer': students_inputs.get(name, _('Not answered yet.')),
                    'question': question,
                })

            # Make list of sections-answers
            return [
                {'name': key, 'questions': value}
                for key, value in answers.items()
            ]
        return None

    @staticmethod
    def _iter_pb_answers(response):
        """
        Iterate over pb-answer blocks in course blocks API response and yield
        section, subsection and unit display names along with pb-answer blocks.
        """
        blocks = response['blocks']
        course_block = blocks[response['root']]
        for section_id in course_block.get('children', []):
            section_block = blocks[section_id]
            for subsection_id in section_block.get('children', []):
                subsection_block = blocks[subsection_id]
                for unit_id in subsection_block.get('children', []):
                    unit_block = blocks[unit_id]
                    for pb_id in unit_block.get('children', []):
                        pb_block = blocks[pb_id]
                        for pb_answer_id in pb_block.get('children', []):
                            pb_answer_block = blocks[pb_answer_id]
                            yield (
                                section_block['display_name'],
                                subsection_block['display_name'],
                                unit_block['display_name'],
                                pb_answer_block,
                            )

    def list_pb_answers(self, all_blocks=False):
        """
        Returns a list of dicts with info about all problem builder's pb-answer
        blocks present in the current coures.

        The items are ordered in the order they appear in the course.
        """
        response = self._fetch_pb_answer_blocks(all_blocks)
        return [
            {
                'section': section,
                'subsection': subsection,
                'unit': unit,
                'id': block['id'],
                'name': block['student_view_data']['name'],
                'question': block['student_view_data']['question'],
                'display_name': block['display_name'],
            }
            for section, subsection, unit, block in self._iter_pb_answers(response)
        ]

    def _get_course_id(self):
        """
        Returns the course id (string) corresponding to the current course.
        """
        course_id = getattr(self.runtime, 'course_id', 'course_id')
        course_id = str(normalize_id(course_id))
        return course_id

    def _get_current_user(self):
        """
        Returns django.contrib.auth.models.User instance corresponding to the current user.
        """
        xblock_user = self.runtime.service(self, 'user').get_current_user()
        user_id = xblock_user.opt_attrs['edx-platform.user_id']
        user = User.objects.get(pk=user_id)  # pylint: disable=no-member
        return user

    def _get_current_anonymous_user_id(self):
        """
        Returns anonymous id (string) corresponding to the current user.
        """
        return self.runtime.anonymous_student_id

    def _get_course_name(self):
        """
        Get the name of the current course, for the downloadable report.
        """
        try:
            course_key = self.scope_ids.usage_id.course_key
        except AttributeError:
            return ''  # We are not in an edX runtime

        try:
            course_root_key = course_key.make_usage_key('course', 'course')
            return self.runtime.get_block(course_root_key).display_name
        # ItemNotFoundError most likely, but we can't import that exception in non-edX environments
        except Exception:  # pylint: disable=W0703
            # We may be on old mongo:
            try:
                course_root_key = course_key.make_usage_key('course', course_key.run)
                return self.runtime.get_block(course_root_key).display_name
            except Exception:  # pylint: disable=W0703
                return ''

    @staticmethod
    def _make_url_absolute(url):
        """
        This method will turn make relative urls absolute. It's helpful in
        some cases where some functions treat a variable as a path and url in
        the same time
        """
        lms_base = settings.ENV_TOKENS.get('LMS_BASE')
        scheme = 'https' if settings.HTTPS == 'on' else 'http'
        lms_base = '{}://{}'.format(scheme, lms_base)
        return urljoin(str(lms_base), str(url))

    def get_progress_metrics(self):
        """
        Fetches and returns dict with progress metrics for the current user
        in the course.
        """
        user = self._get_current_user()
        course_id = self._get_course_id()
        client = ApiClient(user, course_id)
        completion_client = CompletionApiClient(user, course_id)

        user_progress = completion_client.get_user_progress()
        cohort_average = client.get_cohort_average_progress()

        if user_progress is None or cohort_average is None:
            return None

        return {
            'user': int(round(user_progress)),
            'cohort_average': int(round(cohort_average)),
        }

    def get_proficiency_metrics(self):
        """
        Fetches and returns dict with proficiency (grades) metrics for the current user
        in the course.
        """
        user = self._get_current_user()
        course_id = self._get_course_id()
        client = ApiClient(user, course_id)

        proficiency = client.get_user_proficiency()

        if proficiency is None:
            return None

        return {
            'user': int(round(proficiency.get('user', 0))),
            'cohort_average': int(round(proficiency.get('cohort_average', 0))),
        }

    def get_engagement_metrics(self):
        """
        Fetches and returns dict with engagement metrics for the current user
        and course.
        """
        user = self._get_current_user()
        course_id = self._get_course_id()
        client = ApiClient(user, course_id)

        user_engagement = client.get_user_engagement_metrics()

        if not user_engagement:
            return None

        cohort_score = user_engagement['course_avg']
        cohort_score_rounded = int(round(cohort_score))
        if cohort_score_rounded < 1 and cohort_score > 0:
            cohort_score_rounded = 1
        metrics = user_engagement['stats']
        return {
            'user_score': user_engagement['score'],
            'cohort_score': cohort_score_rounded,
            'new_posts': metrics.get('num_threads', 0),
            'total_replies': metrics.get('num_replies', 0) + metrics.get('num_comments', 0),
            'upvotes': metrics.get('num_upvotes', 0),
            'comments_generated': metrics.get('num_comments_generated', 0),
            'posts_followed': metrics.get('num_thread_followers', 0),
        }

    def _fetch_pb_answer_blocks(self, all_blocks=False):
        """
        Fetches blocks from the Course API. Results are currently limited to
        course, chapter, sequential, vetcial, and pb-answer blocks.

        If `all_blocks` is True, returns all blocks, including those that are
        visible only to specific learners (cohort groups, randomized content...).
        Only staff users can request `all_blocks`.
        """
        user = self._get_current_user()
        course_id = getattr(self.runtime, 'course_id', 'course_id')
        course_id = str(normalize_id(course_id))

        client = CourseBlocksApiClient(user, course_id)
        response = client.get_blocks(
            all_blocks=all_blocks,
            depth='all',
            requested_fields='student_view_data,children',
            student_view_data='pb-answer',
            block_types_filter='pb-answer,problem-builder,vertical,sequential,chapter,course',
            username=user.username,
        )
        return response

    def _expand_static_url(self, url, absolute=False):
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
                from static_replace import replace_static_urls  # pylint: disable=import-error,import-outside-toplevel
                url = replace_static_urls('"{}"'.format(url), None, course_id=self.runtime.course_id)[1:-1]
            except ImportError:
                pass

        if absolute:
            url = self._make_url_absolute(url)

        return url

    @classmethod
    def parse_xml(cls, node, runtime, keys, id_generator):
        """
        Use `node` to construct a new block.
        Arguments:
            node (:class:`~xml.etree.ElementTree.Element`): The xml node to parse into an xblock.
            runtime (:class:`.Runtime`): The runtime to use while parsing.
            keys (:class:`.ScopeIds`): The keys identifying where this block
                will store its data.
            id_generator (:class:`.IdGenerator`): An object that will allow the
                runtime to generate correct definition and usage ids for
                children of this block.

        Notes:
            This method is overwritten from :class:`~xblock.mixins.XmlSerizalizationMixin`.
            https://github.com/edx/XBlock/blob/master/xblock/mixins.py
        """
        block = super(EOCJournalXBlock, cls).parse_xml(node, runtime, keys, id_generator)
        course_id = getattr(id_generator, 'target_course_id', '')

        if not course_id:
            return block

        course_id = str(normalize_id(course_id))
        course_key = CourseKey.from_string(course_id)

        transformed_block_ids = []
        for selected in block.selected_pb_answer_blocks:
            usage_key = UsageKey.from_string(selected)
            if usage_key.course_key == course_key:
                transformed_block_ids.append(selected)
            else:
                mapped = usage_key.map_into_course(course_key)
                transformed_block_ids.append(str(mapped))

        block.selected_pb_answer_blocks = transformed_block_ids
        return block
