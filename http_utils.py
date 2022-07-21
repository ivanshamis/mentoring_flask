

class ResponseError(BaseException):
    def __init__(self, status, message, **kwargs):
        self.status = status
        self.message = message
        self.kwargs = kwargs

