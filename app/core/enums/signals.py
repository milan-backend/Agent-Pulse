from enum import Enum


class SignalType(str, Enum):
    """
    Deterministic signals extracted by Python Intelligence.
    """

    # Structure

    TITLE = "title"

    HEADING = "heading"

    SECTION = "section"

    SUBSECTION = "subsection"

    PARAGRAPH = "paragraph"

    LIST = "list"

    # Layout

    TABLE = "table"

    FIGURE = "figure"

    IMAGE = "image"

    CAPTION = "caption"

    FOOTNOTE = "footnote"

    HEADER = "header"

    FOOTER = "footer"

    PAGE_NUMBER = "page_number"

    # Semantic

    RULE = "rule"

    DEFINITION = "definition"

    PROCEDURE = "procedure"

    EXCEPTION = "exception"

    WARNING = "warning"

    NOTE = "note"

    EXAMPLE = "example"

    # Search

    KEYWORD = "keyword"

    ENTITY = "entity"

    REFERENCE = "reference"

    HYPERLINK = "hyperlink"

    ACRONYM = "acronym"

    # Numeric

    DATE = "date"

    TIMELINE = "timeline"

    CURRENCY = "currency"

    MEASUREMENT = "measurement"

    PERCENTAGE = "percentage"

    FORMULA = "formula"

    # Quality

    OCR = "ocr"

    DUPLICATE = "duplicate"

    LANGUAGE = "language"