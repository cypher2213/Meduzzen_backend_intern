from app.core.base_exception import BaseServiceError


class SelectedOptionsNotListError(BaseServiceError):
    def __init__(self):
        super().__init__("Selected options must be a list.", status_code=400)


class NoOptionsSelectedError(BaseServiceError):
    def __init__(self):
        super().__init__("At least one option must be selected.", status_code=400)


class OptionIndexOutOfRangeError(BaseServiceError):
    def __init__(self, index: int, max_index: int):
        super().__init__(
            f"Option index {index} is out of valid range (0 to {max_index}).",
            status_code=400,
        )
        self.index = index
        self.max_index = max_index


class TooManyOptionsSelectedError(BaseServiceError):
    def __init__(self, max_allowed: int):
        super().__init__(
            f"Too many options selected. Max {max_allowed} allowed.", status_code=400
        )
        self.max_allowed = max_allowed
