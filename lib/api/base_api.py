# Inheritance only

class BaseApi:
    SUPPORTED_METHODS = [
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS"
    ]

    def __init__(self, app):
        self.app = app
        self.prefix = "/" + self.__class__.__name__.lower()

        if self.prefix == "base":
            raise ValueError("This class can be only inherited.")

        self.init_api()

    def add_route(self, path, handler, *methods):
        handled_methods = self.validate_methods(methods)
        self.app.add_api_route(self.prefix + path, handler, methods=handled_methods)

    def validate_methods(self, methods):
        if not methods:
            raise ValueError("At least one method must be provided.")

        handled_methods = [obj.upper() for obj in methods]

        for http_method in handled_methods:
            if http_method not in self.SUPPORTED_METHODS:
                raise ValueError(f"Unsupported http method: {http_method}")

        return handled_methods

    def init_api(self):
        raise ValueError("This method must be defined.")
