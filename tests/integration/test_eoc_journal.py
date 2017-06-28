"""
Basic integration tests for the EOC Journal XBlock.
"""

import json
from mock import Mock, patch

from xblock.reference.user_service import XBlockUser
from xblockutils.studio_editable_test import StudioEditableBaseTest
from xblockutils.resources import ResourceLoader


loader = ResourceLoader(__name__)


default_pb_answer_block_ids = [
    'i4x://Org/Course/pb-answer/b86edf60454b47dbb8f2e1b4e2d48d6a',
    'i4x://Org/Course/pb-answer/6f070c350e39429cbccfd3185a33621c',
    'i4x://Org/Course/pb-answer/a0b04a13d3074229b6be33fbc31de233',
]

def checkbox_value(block_id):
    """
    Checkbox value attributes are wrapped in double quotes.
    This method wraps a block_id (string) into double quotes,
    which is useful in tests to find checkboxes by block id
    and comparing checkbox values to expected block ids.
    """
    return '"{}"'.format(block_id)


class TestEOCJournal(StudioEditableBaseTest):
    default_css_selector = 'div.oec-journal-block'
    module_name = __name__


    def setUp(self):
        super(TestEOCJournal, self).setUp()
        # Patch _get_current_user method.
        mock_user = Mock()
        mock_user.username = 'some-user'
        self.patch('eoc_journal.eoc_journal.EOCJournalXBlock._get_current_user', mock_user)
        # Patch CourseBlocksApiClient.
        self.patch('eoc_journal.eoc_journal.CourseBlocksApiClient.connect', Mock())
        def mock_get_blocks(self, **kwargs):
            return json.loads(loader.load_unicode('data/course_api_response.json'))
        self.patch('eoc_journal.eoc_journal.CourseBlocksApiClient.get_blocks', mock_get_blocks)

    def patch(self, item, return_value):
        patcher = patch(item, return_value)
        patcher.start()
        self.addCleanup(patcher.stop)

    def set_standard_scenario(self):
        scenario = '<eoc-journal url_name="defaults" />'
        self.set_scenario_xml(scenario)

    def get_element_for_pb_answers_field(self):
        field = self.browser.find_element_by_css_selector(
            'li.field[data-field-name=selected_pb_answer_blocks]'
        )
        return field

    def configure_block(self, key_takeaways_pdf=None, selected_pb_answer_blocks=[]):
        self.set_standard_scenario()
        self.go_to_view('studio_view')
        self.fix_js_environment()

        if key_takeaways_pdf is not None:
            control = self.get_element_for_field('key_takeaways_pdf')
            control.clear()
            control.send_keys(key_takeaways_pdf)
        if selected_pb_answer_blocks:
            field = self.get_element_for_pb_answers_field()
            for block_id in selected_pb_answer_blocks:
                selector = "input[type=checkbox][value='{}']".format(checkbox_value(block_id))
                control = field.find_element_by_css_selector(selector)
                control.click()
        self.click_save()

        self.element = self.go_to_view('student_view')

    def test_pb_answer_blocks_listed_in_edit_view(self):
        self.set_standard_scenario()
        self.go_to_view('studio_view')
        self.fix_js_environment()

        field_control = self.get_element_for_pb_answers_field()
        items = field_control.find_elements_by_css_selector('.list-settings-item')
        # There are three pb-answer blocks in the mocked course blocks API response.
        self.assertEqual(len(items), 3)
        expected_choices = [
            {
                'value': default_pb_answer_block_ids[0],
                'title': 'First Section / Subsection 1 / Unit 3 / 23761f7',
            },
            {
                'value': default_pb_answer_block_ids[1],
                'title': 'Second Section / Subsection 2 / Unit 1 / Introductions'
            },
            {
                'value': default_pb_answer_block_ids[2],
                'title': 'Second Section / Subsection 2 / Unit 1 / More Info'
            },
        ]
        for idx, item in enumerate(items):
            value = expected_choices[idx]['value']
            title = expected_choices[idx]['title']
            checkbox = item.find_element_by_css_selector('input[type=checkbox]')
            self.assertEqual(checkbox.get_attribute('value'), checkbox_value(value))
            label = item.find_element_by_css_selector('label')
            self.assertEqual(label.text, title)

    def test_pb_answer_blocks_selection_preserved_in_edit_view(self):
        selected_block_id = default_pb_answer_block_ids[1]
        self.configure_block(selected_pb_answer_blocks=[selected_block_id])
        # Reload edit view.
        self.go_to_view('studio_view')
        field_control = self.get_element_for_pb_answers_field()
        checked_checkboxes = field_control.find_elements_by_css_selector(
            'input[type=checkbox]:checked'
        )
        self.assertEqual(len(checked_checkboxes), 1)
        self.assertEqual(
            checked_checkboxes[0].get_attribute('value'),
            checkbox_value(selected_block_id)
        )

    def test_no_takeaways_pdf_configured(self):
        self.configure_block()
        links = self.element.find_elements_by_css_selector('a.key-takeaways-link')
        self.assertEqual(len(links), 0)
        self.assertIn(self.element.text, 'Key Takeaways PDF not available at this time.')

    def test_takeaways_pdf_configured(self):
        self.configure_block(key_takeaways_pdf='/static/my.pdf')
        link = self.element.find_element_by_css_selector('a.key-takeaways-link')
        self.assertIn(link.text, 'Key Takeaways')
        self.assertEqual(link.get_attribute('target'), '_blank')
