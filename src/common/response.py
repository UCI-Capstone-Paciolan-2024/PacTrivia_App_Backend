import common.packages.simplejson as json


def _cors_headers(content_type):
    return {
        'Content-Type': content_type,
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type'}


def response(error: Exception | None, data: dict | None = None) -> None:
    """Returns a dict to respond to API calls with the appropriate headers and given Exception/Data."""
    e = None
    if error:
        e = {'type': type(error).__name__, 'message': str(error)}
    return {
        'statusCode': (400 if error else 200),
        'headers': _cors_headers('application/json'),
        'body': json.dumps({'error': e, 'data': data})
    }
