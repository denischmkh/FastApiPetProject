class RegisterException(Exception):
    def __init__(self, detail, status_code):
        self.detail = detail
        self.status_code = status_code


class LoginException(Exception):
    def __init__(self, detail, status_code):
        self.detail = detail
        self.status_code = status_code