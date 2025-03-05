from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..services.auth import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_auth_svc(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_svc: AuthService = Depends(get_auth_svc),
):
    return await auth_svc.get_current_user(token)
