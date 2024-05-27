class ReturnableException(Exception):
    """Exceptions that may be returned to frontend"""
    pass


class AuthError(ReturnableException):
    pass


class NoMoreQuestionsError(ReturnableException):
    pass


class QuestionNotFoundError(ReturnableException):
    pass


class NoValidSessionError(ReturnableException):
    pass


class AnswerTimeoutError(ReturnableException):
    pass


class NoGameFoundError(ReturnableException):
    pass


class InternalError(ReturnableException):
    pass


class QueryError(Exception):
    pass


class IntegrityError(Exception):
    pass
