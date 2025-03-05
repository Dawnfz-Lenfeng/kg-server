from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    # 基础配置
    PROJECT_NAME: str = "CKGCUS"
    API_V1_STR: str = "/api/v1"

    # 数据库配置
    DATABASE_URL: str = "postgresql://dev_user:dev_password@localhost:5432/ckgcus"

    # 存储根目录
    STORAGE_DIR: str = "storage"

    @property
    def UPLOAD_DIR(self):
        """上传文件目录"""
        return Path(f"{self.STORAGE_DIR}/uploads")

    @property
    def RAW_TEXT_DIR(self):
        """原始文本目录"""
        return Path(f"{self.STORAGE_DIR}/texts/raw")

    @property
    def NORM_TEXT_DIR(self):
        """标准化文本目录"""
        return Path(f"{self.STORAGE_DIR}/texts/normalized")

    # 开发模式配置
    DEV_MODE: bool = True
    TESTING: bool = False

    # JWT Settings
    JWT_SECRET_KEY: str = "secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
