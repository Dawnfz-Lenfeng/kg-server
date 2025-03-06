from pydantic import BaseModel


class RoleInfo(BaseModel):
    roleName: str
    value: str


class LoginParams(BaseModel):
    username: str
    password: str


class LoginResult(BaseModel):
    userId: str
    token: str
    role: RoleInfo


class UserInfo(BaseModel):
    roles: list[RoleInfo]
    userId: str
    username: str
    realName: str
    avatar: str
    desc: str | None = None


class RegisterParams(BaseModel):
    username: str
    password: str
    real_name: str


class RegisterResult(BaseModel):
    userId: str
    username: str
