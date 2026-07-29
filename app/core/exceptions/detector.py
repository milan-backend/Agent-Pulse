class DetectorError(Exception):
    """Base detector exception."""


class OCRDetectorError(DetectorError):
    pass


class LayoutDetectorError(DetectorError):
    pass


class HeadingDetectorError(DetectorError):
    pass