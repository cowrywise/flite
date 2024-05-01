from functools import wraps
from drf_yasg.utils import swagger_auto_schema

def swagger_decorator(methods=None, request_body=None, responses=None):
    def decorator(func):
        @wraps(func)
        def decorated_func(*args, **kwargs):
            return func(*args, **kwargs)

        for method in methods:
            schema_kwargs = {}
            if request_body:
                schema_kwargs['request_body'] = request_body
            if responses:
                schema_kwargs['responses'] = responses

            decorated_func = swagger_auto_schema(
                methods=[method],
                **schema_kwargs
            )(decorated_func)

        return decorated_func
    return decorator