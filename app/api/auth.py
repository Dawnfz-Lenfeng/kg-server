from fastapi import APIRouter, Depends, HTTPException

from ..core.response import response_wrapper
from ..dependencies.auth import get_auth_svc, get_current_user
from ..models.user import User
from ..schemas.user import (
    LoginParams,
    RegisterParams,
    RegisterResult,
    RoleInfo,
    UserInfo,
)
from ..services.auth import AuthService

router = APIRouter(tags=["auth"])


@router.post("/login")
@response_wrapper
async def login(
    params: LoginParams,
    auth_svc: AuthService = Depends(get_auth_svc),
):
    result = await auth_svc.login(params)
    if not result:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return result


@router.get("/getUserInfo")
@response_wrapper
async def get_user_info(user: User = Depends(get_current_user)):
    return UserInfo(
        roles=[RoleInfo(roleName=user.role_name, value=user.role_value)],
        userId=str(user.id),
        username=user.username,
        realName=user.real_name,
        avatar=user.avatar,
        desc=user.desc,
    )


@router.get("/getPermCode")
@response_wrapper
async def get_perm_code(
    user: User = Depends(get_current_user),
    auth_svc: AuthService = Depends(get_auth_svc),
):
    return auth_svc.get_perm_codes(user.role_value)


@router.get("/logout")
@response_wrapper
async def logout():
    return "退出登录成功"


@router.post("/register", response_model=RegisterResult)
async def register(
    params: RegisterParams,
    auth_svc: AuthService = Depends(get_auth_svc),
):
    user = await auth_svc.register(params)
    return RegisterResult(
        userId=str(user.id),
        username=user.username,
    )
