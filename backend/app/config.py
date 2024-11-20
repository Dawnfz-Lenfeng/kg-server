from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    # 基础配置
    PROJECT_NAME: str = "CKGCUS"
    API_V1_STR: str = "/api/v1"

    # 数据库配置
    DATABASE_URL: str = "postgresql://dev_user:dev_password@localhost:5432/ckgcus"

    # 文件存储配置
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 20 * 1024 * 1024  # 20MB

    # 开发模式配置
    DEV_MODE: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
