"""
Basic integration tests for the EOC Journal XBlock.
"""

from xblockutils.studio_editable_test import StudioEditableBaseTest

class TestEOCJournal(StudioEditableBaseTest):

    default_css_selector = 'div.oec-journal-block'
    module_name = __name__


    def configure_block(self, key_takeaways_pdf=None):
        scenario = '<eoc-journal url_name="defaults" />'
        self.set_scenario_xml(scenario)

        self.go_to_view('studio_view')
        self.fix_js_environment()
        if key_takeaways_pdf is not None:
            control = self.get_element_for_field('key_takeaways_pdf')
            control.clear()
            control.send_keys(key_takeaways_pdf)
        self.click_save()

        self.element = self.go_to_view('student_view')

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
