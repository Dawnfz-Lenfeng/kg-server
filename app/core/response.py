from functools import wraps

from ..schemas.base import Result, ResultEnum


def to_response(func):
    """响应包装装饰器"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            response = await func(*args, **kwargs)
            return Result(code=ResultEnum.SUCCESS, result=response)
        except Exception as e:
            return Result(code=ResultEnum.ERROR, message=str(e))

    return wrapper
