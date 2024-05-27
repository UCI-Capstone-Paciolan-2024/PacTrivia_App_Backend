import common.packages.simplejson as json
from common.exceptions import ReturnableException, InternalError


def _cors_headers(content_type):
    return {
        'Content-Type': content_type,
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*'}


def response(error: Exception | None, data: dict | None = None) -> None:
    """Returns a dict to respond to API calls with the appropriate headers and given Exception/Data."""
    e = None
    if error:
        if not issubclass(type(error), ReturnableException):
            error = InternalError("Backend internal error.")
        e = {'type': type(error).__name__, 'message': str(error)}
    return {
        'statusCode': (400 if error else 200),
        'headers': _cors_headers('application/json'),
        'body': json.dumps({'error': e, 'data': data})
    }
