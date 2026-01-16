from app.core.base_exception import BaseServiceError


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
            "You do not have rights to modify this invitation", status_code=403
        )


class InviteInvalidOptionError(BaseServiceError):
    def __init__(self):
        super().__init__("Option must be accepted or declined", status_code=400)


class InvalidInviteStatusError(BaseServiceError):
    def __init__(self, status):
        super().__init__(
            f"Invite cannot be processed in status '{status}'.", status_code=400
        )
        self.status = status
