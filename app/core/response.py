from functools import wraps
from typing import Any, Callable, TypeVar

from fastapi import Response
from fastapi.responses import JSONResponse

from ..schemas.base import Result, ResultEnum

T = TypeVar("T")


def response_wrapper():
    """响应包装装饰器"""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Response:
            try:
                response = await func(*args, **kwargs)

                # 如果是 FileResponse，直接返回
                if (
                    isinstance(response, Response)
                    and response.__class__.__name__ == "FileResponse"
                ):
                    return response

                # 如果已经是 Result 格式，直接返回
                if isinstance(response, dict) and "code" in response:
                    return JSONResponse(content=response)

                # 包装响应
                return JSONResponse(
                    content=Result(
                        code=ResultEnum.SUCCESS, result=response
                    ).model_dump()
                )

            except ValueError as e:
                # 处理参数验证错误
                return JSONResponse(
                    status_code=400,
                    content=Result(
                        code=ResultEnum.PARAM_ERROR, message=str(e)
                    ).model_dump(),
                )
            except Exception as e:
                # 处理其他未知错误
                return JSONResponse(
                    status_code=500,
                    content=Result(
                        code=ResultEnum.ERROR,
                        message=f"Internal Server Error: {str(e)}",
                    ).model_dump(),
                )

        return wrapper

    return decorator
