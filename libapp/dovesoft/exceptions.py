class DoveSoftError(Exception):

    """Base class for SendGrid-related errors."""


class DoveSoftClientError(DoveSoftError):

    """Client error, which corresponds to a 4xx HTTP error."""


class DoveSoftServerError(DoveSoftError):

    """Server error, which corresponds to a 5xx HTTP error."""
