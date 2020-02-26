"""
Test EOC Journal Block import.
"""

import sys
import unittest
from mock import Mock, patch
from django.test import TestCase

sys.modules['openedx'] = Mock()
sys.modules['openedx.core'] = Mock()
sys.modules['openedx.core.djangoapps'] = Mock()
sys.modules['openedx.core.djangoapps.oauth_dispatch'] = Mock()
sys.modules['openedx.core.djangoapps.oauth_dispatch.jwt'] = Mock()
from eoc_journal.eoc_journal import EOCJournalXBlock


class TestEOCJournalImport(TestCase):
    """
    Test End of Course Journal Import
    """

    @patch('eoc_journal.eoc_journal.XBlock.parse_xml',
        return_value=Mock(autospec=EOCJournalXBlock)
    )
    def test_parse_xml(self, mock_xblock_parse_xml):
        mock_xblock_parse_xml().selected_pb_answer_blocks = [
            'i4x://Org/Course/pb-answer/b86edf60454b47dbb8f2e1b4e2d48d6a',
            'i4x://Org/Course/pb-answer/6f070c350e39429cbccfd3185a33621c',
            'i4x://Org/Course/pb-answer/a0b04a13d3074229b6be33fbc31de233',
            'i4x://Org/Course/pb-answer/927c5b8cd051475e937b8c1091a9feaf',
        ]
        mock_node = Mock()
        mock_runtime = Mock()
        mock_keys = Mock()
        mock_id_generator = Mock(target_course_id='Org/CourseToImport/2014')
        block = EOCJournalXBlock.parse_xml(mock_node, mock_runtime, mock_keys, mock_id_generator)
        for block_id in block.selected_pb_answer_blocks:
            self.assertTrue(block_id.startswith('i4x://Org/CourseToImport'))
