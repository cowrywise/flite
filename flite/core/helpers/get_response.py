from flite.core.constants.messages import ERROR_MESSAGES

def get_response(**kwargs):
    """Creates response body"""

    msg_type = kwargs.get('res_type', 'error')
    response = {'status': msg_type}
    if msg_type == 'error':
        error_key = kwargs.get('error_key')
        error = ERROR_MESSAGES.get(error_key)
        format_str = kwargs.get('format_str')
        body = {
            'error': error[0].format(format_str),
            'message': error[1].format(format_str),
        }
    else:
        body = {'data': kwargs.get('data')}
    response.update(body)

    return response
