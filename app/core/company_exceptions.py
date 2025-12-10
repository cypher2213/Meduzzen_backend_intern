from app.core.base_exception import BaseServiceError


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
