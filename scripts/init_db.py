import asyncio
import shutil
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent.parent))
from sqlalchemy import select

from app.database import AsyncSessionLocal, Base, engine
from app.models.user import User
from app.services.auth import AuthService
from app.settings import settings


async def init_db():
    # 删除上传目录以及里面的文件
    if Path(settings.STORAGE_DIR).exists():
        shutil.rmtree(settings.STORAGE_DIR)
        print("Deleted old storage directory.")

    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 创建会话
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # 检查是否已有用户
            result = await session.execute(select(User))
            if result.first() is not None:
                print("Database already initialized!")
                return

            # 创建测试用户
            test_users = [
                {
                    "username": "admin",
                    "password": "123456",
                    "real_name": "Admin",
                    "avatar": "https://q1.qlogo.cn/g?b=qq&nk=190848757&s=640",
                    "desc": "manager",
                    "role_name": "Super Admin",
                    "role_value": "super",
                },
                {
                    "username": "test",
                    "password": "123456",
                    "real_name": "test user",
                    "avatar": "https://q1.qlogo.cn/g?b=qq&nk=339449197&s=640",
                    "desc": "tester",
                    "role_name": "Tester",
                    "role_value": "test",
                },
            ]

            for user_data in test_users:
                user = User(
                    username=user_data["username"],
                    password=AuthService.get_password_hash(user_data["password"]),
                    real_name=user_data["real_name"],
                    avatar=user_data["avatar"],
                    desc=user_data["desc"],
                    role_name=user_data["role_name"],
                    role_value=user_data["role_value"],
                )
                session.add(user)

            print("Database initialized successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
