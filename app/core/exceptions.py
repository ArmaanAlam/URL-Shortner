class BaseAppException(Exception):
    """Base application exception."""
    pass

class URLNotFoundException(BaseAppException):
    def __init__(self, key: str):
        super().__init__(f"Short URL '{key}' was not found.")
        self.key = key

class AliasConflictException(BaseAppException):
    def __init__(self, alias: str):
        super().__init__(f"Custom alias '{alias}' is already in use.")
        self.alias = alias

class InvalidURLException(BaseAppException):
    def __init__(self, message: str):
        super().__init__(message)
