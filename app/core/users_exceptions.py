from app.core.base_exception import BaseServiceError


class UserNotFoundError(BaseServiceError):
    def __init__(self, user_id=None):
        msg = "User not found" if not user_id else f"User with id {user_id} not found"
        super().__init__(msg, status_code=404)
        self.user_id = user_id


class PermissionDeniedError(BaseServiceError):
    def __init__(self, message="Permission denied"):
        super().__init__(message, status_code=403)


class InvalidCredentialsError(BaseServiceError):
    def __init__(self):
        super().__init__("Invalid credentials", status_code=401)


class EmailChangeForbiddenError(BaseServiceError):
    def __init__(self):
        super().__init__("Email cannot be changed", status_code=400)


class InvalidRefreshTokenError(BaseServiceError):
    def __init__(self):
        super().__init__("Invalid refresh token payload", status_code=401)
