class BaseServiceError(Exception):
    """Базовый класс для ошибок сервисного уровня"""

    status_code = 400

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code


# ================= USER ERRORS =================
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


# ================= INVITE ERRORS =================
class InviteNotFoundError(BaseServiceError):
    def __init__(self, invite_id):
        super().__init__(f"Invite with id {invite_id} does not exist!", status_code=404)
        self.invite_id = invite_id


class InviteAlreadyProcessedError(BaseServiceError):
    def __init__(self):
        super().__init__(
            "This invite is already accepted or declined.", status_code=400
        )


class InvitePermissionDeniedError(BaseServiceError):
    def __init__(self):
        super().__init__(
            "You do not have rights to modify this invitation",
            status_code=403,
        )


class InviteInvalidOptionError(BaseServiceError):
    def __init__(self):
        super().__init__("Option must be accepted or declined", status_code=400)


# ================= REQUEST ERRORS =================
class RequestNotFoundError(BaseServiceError):
    def __init__(self, req_id):
        super().__init__(f"Request with id {req_id} is not found!", status_code=404)
        self.req_id = req_id


# ================= INVITE ERRORS =================
class InvalidInviteStatusError(BaseServiceError):
    def __init__(self, status):
        super().__init__(
            f"Invite cannot be processed in status '{status}'.", status_code=400
        )
        self.status = status


class RequestWrongTypeError(BaseServiceError):
    def __init__(self):
        super().__init__("You can cancel only requests", status_code=400)


class RequestAlreadyCanceledError(BaseServiceError):
    def __init__(self):
        super().__init__("This request has been already canceled", status_code=400)


class RequestPermissionDeniedError(BaseServiceError):
    def __init__(self):
        super().__init__("You can cancel only your requests", status_code=403)


# ================= COMPANY ERRORS =================
class NotCompanyMemberError(BaseServiceError):
    def __init__(self, user_id=None):
        msg = "You are not a member of this company"
        if user_id:
            msg += f" (user id={user_id})"
        super().__init__(msg, status_code=404)
        self.user_id = user_id


class OwnerCannotLeaveError(BaseServiceError):
    def __init__(self):
        super().__init__(
            "You cannot leave the company as the only owner. Transfer ownership first.",
            status_code=400,
        )


class CompanyNotFoundError(BaseServiceError):
    def __init__(self, company_id):
        super().__init__(f"Company with id {company_id} is not found.", status_code=404)
        self.company_id = company_id


class OwnerOnlyActionError(BaseServiceError):
    def __init__(self):
        super().__init__(
            "Only company owners can perform this action.", status_code=403
        )


class OwnerAndAdminOnlyActionError(BaseServiceError):
    def __init__(self):
        super().__init__(
            "Only company owners or admins can perform this action.", status_code=403
        )


class FewOptionsException(BaseServiceError):
    def __init__(self):
        super().__init__(
            "The question must have at least 2 answer options.", status_code=400
        )


class FewQuestionsException(BaseServiceError):
    def __init__(self):
        super().__init__("You need to provide at least two questions", status_code=400)


class QuizNotFoundException(BaseServiceError):
    def __init__(self):
        super().__init__(
            "This quiz is not from your company or it does not exist", status_code=403
        )


class NotEnoughOptionsException(BaseServiceError):
    def __init__(self):
        super().__init__("Question must include at least 2 options", status_code=400)


class QuestionNotFoundException(BaseException):
    def __init__(self):
        super().__init__(
            "This question is not from your company or it does not exist",
            status_code=403,
        )


class MemberNotFoundError(BaseServiceError):
    def __init__(self, user_id):
        super().__init__(
            f"User with id {user_id} is not a member of the company.", status_code=404
        )
        self.user_id = user_id


class UserAlreadyAdminException(BaseServiceError):
    def __init__(self):
        super().__init__("This user is already admin", status_code=400)


class UserAlreadyOwnerException(BaseServiceError):
    def __init__(self):
        super().__init__(
            "This user is owner and cannot become an admin", status_code=400
        )
