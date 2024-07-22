""" Custom exceptions. """


class GigError(RuntimeError):
    """Base exception."""

    def __init__(self, message: str):
        super().__init__(f"{type(self).__name__}: {message}")


class VenueExistsError(GigError):
    def __init__(self, venue: str):
        super().__init__(f'"{venue}" already exists in the database.')


class MissingSourceError(GigError):
    def __init__(self, venue: str):
        super().__init__(f'Could not find source for "{venue}".')


class MissingElementError(GigError):
    def __init__(self, missing_element: str, parent_element: str = ""):
        message = f"Could not find `{missing_element}` element"
        message += f" under `{parent_element}` element." if parent_element else "."
        super().__init__(message)
