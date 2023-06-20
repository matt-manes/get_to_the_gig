""" Custom exceptions. """


class GigError(RuntimeError):
    """Base exception."""

    def __init__(self, message: str):
        super().__init__(f"{type(self).__name__}: {message}")


class VenueExistsError(GigError):
    def __init__(self, venue: str):
        super().__init__(f'"{venue}" already exists in the database.')
