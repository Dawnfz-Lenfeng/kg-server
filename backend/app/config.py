from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 数据库配置
    DATABASE_URL: str

    # 文件存储配置
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 20 * 1024 * 1024  # 20MB
    ALLOWED_EXTENSIONS: set = {"pdf", "txt"}

    # API配置
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "CKGCUS"

    class Config:
        env_file = ".env"


settings = Settings()
