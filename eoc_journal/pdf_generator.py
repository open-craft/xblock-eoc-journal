"""
Utils around Reportlab customizations
"""
from __future__ import unicode_literals
import logging

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.fonts import tt2ps
from reportlab.lib.styles import (
    getSampleStyleSheet,
    StyleSheet1,
    ParagraphStyle,
)

import reportlab
import reportlab.rl_config
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont, TTFError

log = logging.getLogger(__name__)


def get_style_sheet(font_url=None):
    """Returns a custom stylesheet object"""
    default_style_sheet = getSampleStyleSheet()

    if not font_url:
        return default_style_sheet

    stylesheet = StyleSheet1()
    font_name = 'customFont'

    try:
        font = TTFont(font_name, font_url)
    except TTFError:
        log.warning(u'Cannot load %s', font_url)
        return default_style_sheet

    reportlab.rl_config.warnOnMissingFontGlyphs = 0
    pdfmetrics.registerFont(font)

    font_name_bold = tt2ps(font_name, 1, 0)
    font_name_italic = tt2ps(font_name, 0, 1)
    font_name_bold_italic = tt2ps(font_name, 1, 1)

    stylesheet.add(ParagraphStyle(
        name='Normal',
        fontName=font_name,
        fontSize=10,
        leading=12
    ))

    stylesheet.add(ParagraphStyle(
        name='BodyText',
        parent=stylesheet['Normal'],
        spaceBefore=6
    ))
    stylesheet.add(ParagraphStyle(
        name='Italic',
        parent=stylesheet['BodyText'],
        fontName=font_name_italic
    ))

    stylesheet.add(
        ParagraphStyle(
            name='Heading1',
            parent=stylesheet['Normal'],
            fontName=font_name_bold,
            fontSize=18,
            leading=22,
            spaceAfter=6
        ),
        alias='h1'
    )

    stylesheet.add(
        ParagraphStyle(
            name='Title',
            parent=stylesheet['Normal'],
            fontName=font_name_bold,
            fontSize=22,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=6
        ),
        alias='title'
    )

    stylesheet.add(
        ParagraphStyle(
            name='Heading2',
            parent=stylesheet['Normal'],
            fontName=font_name_bold,
            fontSize=14,
            leading=18,
            spaceBefore=12,
            spaceAfter=6
        ),
        alias='h2'
    )

    stylesheet.add(
        ParagraphStyle(
            name='Heading3',
            parent=stylesheet['Normal'],
            fontName=font_name_bold_italic,
            fontSize=12,
            leading=14,
            spaceBefore=12,
            spaceAfter=6
        ),
        alias='h3'
    )

    stylesheet.add(ParagraphStyle(
        name='Heading4',
        parent=stylesheet['Normal'],
        fontName=font_name_bold_italic,
        fontSize=10,
        leading=12,
        spaceBefore=10,
        spaceAfter=4
    ),
        alias='h4'
    )

    stylesheet.add(ParagraphStyle(
        name='Heading5',
        parent=stylesheet['Normal'],
        fontName=font_name_bold,
        fontSize=9,
        leading=10.8,
        spaceBefore=8,
        spaceAfter=4
    ),
        alias='h5'
    )

    stylesheet.add(
        ParagraphStyle(
            name='Heading6',
            parent=stylesheet['Normal'],
            fontName=font_name_bold,
            fontSize=7,
            leading=8.4,
            spaceBefore=6,
            spaceAfter=2
        ),
        alias='h6'
    )

    stylesheet.add(
        ParagraphStyle(
            name='Bullet',
            parent=stylesheet['Normal'],
            firstLineIndent=0,
            spaceBefore=3
        ),
        alias='bu'
    )

    stylesheet.add(
        ParagraphStyle(
            name='Definition',
            parent=stylesheet['Normal'],
            firstLineIndent=0,
            leftIndent=36,
            bulletIndent=0,
            spaceBefore=6,
            bulletFontName=font_name_bold_italic
        ),
        alias='df'
    )

    stylesheet.add(
        ParagraphStyle(
            name='Code',
            parent=stylesheet['Normal'],
            fontName='Courier',
            fontSize=8,
            leading=8.8,
            firstLineIndent=0,
            leftIndent=36
        ))

    return stylesheet
