
class UpnpError (Exception):
    def __init__(self, description, code):
        self._description = description
        self._code = code
    
    def __str__(self):
        return f"UpnpError({self._code})::{self._description}"