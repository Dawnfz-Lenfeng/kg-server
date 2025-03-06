from fastapi import APIRouter, Depends

from ..dependencies.auth import get_auth_svc, get_current_user
from ..models.user import User
from ..schemas.base import Result, ResultEnum
from ..schemas.user import (
    LoginParams,
    LoginResult,
    RegisterParams,
    RegisterResult,
    RoleInfo,
    UserInfo,
)
from ..services.auth import AuthService

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=Result[LoginResult])
async def login(
    params: LoginParams,
    auth_svc: AuthService = Depends(get_auth_svc),
):
    login_result = await auth_svc.login(params)
    if not login_result:
        return Result(
            code=ResultEnum.ERROR,
            message="用户名或密码错误",
        )
    return Result(result=login_result)


@router.get("/getUserInfo", response_model=Result[UserInfo])
async def get_user_info(current_user: User = Depends(get_current_user)):
    return Result(
        result=UserInfo(
            roles=[
                RoleInfo(roleName=current_user.role_name, value=current_user.role_value)
            ],
            userId=str(current_user.id),
            username=current_user.username,
            realName=current_user.real_name,
            avatar=current_user.avatar,
            desc=current_user.desc,
        )
    )


@router.get("/getPermCode")
async def get_perm_code(
    current_user: User = Depends(get_current_user),
    auth_svc: AuthService = Depends(get_auth_svc),
):
    return auth_svc.get_perm_codes(current_user.role_value)


@router.get("/logout", response_model=Result)
async def logout():
    return Result(message="退出登录成功")


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
