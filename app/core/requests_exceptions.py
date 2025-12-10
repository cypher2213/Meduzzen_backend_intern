from app.core.base_exception import BaseServiceError


class RequestNotFoundError(BaseServiceError):
    def __init__(self, req_id):
        super().__init__(f"Request with id {req_id} is not found!", status_code=404)
        self.req_id = req_id


class RequestWrongTypeError(BaseServiceError):
    def __init__(self):
        super().__init__("You can cancel only requests", status_code=400)


class RequestAlreadyCanceledError(BaseServiceError):
    def __init__(self):
        super().__init__("This request has been already canceled", status_code=400)


class RequestPermissionDeniedError(BaseServiceError):
    def __init__(self):
        super().__init__("You can cancel only your requests", status_code=403)
