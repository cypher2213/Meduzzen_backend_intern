from app.core.base_exception import BaseServiceError


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


class QuestionNotFoundException(BaseServiceError):
    def __init__(self):
        super().__init__(
            "This question is not from your company or it does not exist",
            status_code=403,
        )


class AlreadyAnsweredException(BaseServiceError):
    def __init__(self):
        super().__init__("You already answered to that question.", status_code=403)
