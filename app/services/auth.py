from datetime import datetime, timedelta

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database import transaction
from ..models.user import User
from ..schemas.user import LoginParams, LoginResult, RegisterParams, RoleInfo

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
PERM_CODES = {
    "super": ["1000", "3000", "5000"],
    "test": ["2000", "4000", "6000"],
}


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def login(self, params: LoginParams) -> LoginResult | None:
        """用户登录"""
        result = await self.db.execute(
            select(User).where(User.username == params.username)
        )
        user = result.scalar_one_or_none()
        if not user or not self.verify_password(params.password, user.password):
            return None

        access_token_expires = timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = self.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )

        return LoginResult(
            userId=str(user.id),
            token=access_token,
            role=RoleInfo(roleName=user.role_name, value=user.role_value),
        )

    async def register(self, params: RegisterParams) -> User:
        """用户注册"""
        result = await self.db.execute(
            select(User).where(User.username == params.username)
        )
        if result.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

        user = User(
            username=params.username,
            password=self.get_password_hash(params.password),
            real_name=params.real_name,
            avatar="https://q1.qlogo.cn/g?b=qq&nk=339449197&s=640",
            desc="New User",
            role_name="Tester",
            role_value="test",
        )

        async with transaction(self.db):
            self.db.add(user)

        await self.db.refresh(user)
        return user

    async def get_current_user(self, token: str) -> User:
        """获取当前用户"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            username: str | None = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        result = await self.db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if user is None:
            raise credentials_exception
        return user

    @staticmethod
    def get_perm_codes(role_value: str) -> list[str]:
        """获取权限码"""
        return PERM_CODES.get(role_value, [])

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """获取密码哈希"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now() + expires_delta
        else:
            expire = datetime.now() + timedelta(
                minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt
