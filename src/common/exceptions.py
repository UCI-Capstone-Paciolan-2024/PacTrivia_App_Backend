"""Exception types that may be returned to frontend"""


class AuthError(Exception):
    pass


class QueryError(Exception):
    pass


class NoMoreQuestionsError(Exception):
    pass


class InvalidSessionError(Exception):
    pass


class QuestionNotFoundError(Exception):
    pass


class NoValidSessionError(Exception):
    pass


class AnswerTimeoutException(Exception):
    pass