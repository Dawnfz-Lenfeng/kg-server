from functools import wraps
from typing import Any, Callable, TypeVar

from fastapi import Response
from fastapi.responses import JSONResponse

from ..schemas.base import Result, ResultEnum

T = TypeVar("T")


def response_wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
    """响应包装装饰器"""

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
                    code=ResultEnum.SUCCESS.value,
                    result=response,
                ).model_dump()
            )

        except ValueError as e:
            # 处理参数验证错误
            return JSONResponse(
                content=Result(
                    code=ResultEnum.ERROR.value,
                    message=str(e),
                ).model_dump(),
            )
        except Exception as e:
            return JSONResponse(
                content=Result(
                    code=ResultEnum.ERROR.value,
                    message=f"{str(e)}",
                ).model_dump(),
            )

    return wrapper
