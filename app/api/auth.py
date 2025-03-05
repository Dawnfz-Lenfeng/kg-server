from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database import get_db, transaction
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
from ..utils.auth import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=Result[LoginResult])
async def login(params: LoginParams, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == params.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(params.password, user.password):
        return Result(code=ResultEnum.ERROR, message="Incorrect username or password")

    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    login_result = LoginResult(
        userId=str(user.id),
        token=access_token,
        role=RoleInfo(roleName=user.role_name, value=user.role_value),
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
async def get_perm_code(current_user: User = Depends(get_current_user)):
    # 这里可以根据用户角色返回不同的权限码
    perm_codes = {"super": ["1000", "3000", "5000"], "test": ["2000", "4000", "6000"]}
    return perm_codes.get(current_user.role_value, [])


@router.get("/logout")
async def logout():
    return {"message": "Token has been destroyed"}


@router.post("/register", response_model=RegisterResult)
async def register(params: RegisterParams, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == params.username))
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # 创建新用户
    user = User(
        username=params.username,
        password=get_password_hash(params.password),
        real_name=params.real_name,
        avatar="https://q1.qlogo.cn/g?b=qq&nk=339449197&s=640",  # 默认头像
        desc="New User",
        role_name="Tester",
        role_value="test",
    )
    async with transaction(db):
        db.add(user)

    await db.refresh(user)
    return RegisterResult(
        userId=str(user.id),
        username=user.username,
    )
