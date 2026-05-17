class AppError(Exception):
    status_code = 400
    as_json = True

    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        return {"success": False, "message": self.message}


class ValidationError(AppError):
    status_code = 400


class NotFoundError(AppError):
    status_code = 404
