"""Kiosk type scale.

Sizes are in points and chosen so text stays readable from about 1.5 m
away on the 10.1" 1024x600 touchscreen. Nothing customer-facing goes
below CAPTION.
"""

from PySide6.QtGui import QFont

SCORE = 64      # the big score number on the teleop result
DISPLAY = 32    # page titles
HEADLINE = 26   # main message on a page
TITLE = 20      # button labels, card names, live instructions
BODY = 16       # supporting sentences
LABEL = 14      # eyebrows, status chips, small buttons
CAPTION = 13    # hints and footnotes


def make_font(point_size: int, bold: bool = False) -> QFont:
    font = QFont()
    font.setPointSize(point_size)
    font.setBold(bold)
    return font
