def _cors_headers(content_type):
    return {
        'Content-Type': content_type,
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type'}


def response(error: Exception | None, data=None):
    e = None
    if error:
        print(f"{error}")
        e = {'type': type(error).__name__, 'message': str(error) }
    return {
        'statusCode': (400 if error else 200),
        'headers': _cors_headers('application/json'),
        'body': {'error': e, 'data': data}
    }
