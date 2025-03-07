from arq import ArqRedis
from fastapi import Request


async def get_redis(request: Request) -> ArqRedis:
    """获取 Redis 连接池"""
    return request.app.state.redis
