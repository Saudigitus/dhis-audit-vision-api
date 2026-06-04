from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    ENVIRONMENT: str = "development"
    host: str
    port: int

    SERVER_DHIS2_URL: str
    SERVER_DHIS2_AUTH: str
    SQL_VIEW_ID: str
    CONTROL_FILE_PATH: str
    DATA_BASE_DIR: str
    SECRET_KEY: str
    TOKEN_EXPIRE_MINUTES: int
    ADMIN_USERNAME : str
    ADMIN_EMAIL : str
    ADMIN_PASSWORD : str
    OFFSET_HOURS : int
    RETRIEVE_SQL_VIEW_ID : str
    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_HOST_USER: str
    EMAIL_HOST_PASSWORD: str
    EMAIL_USE_TLS: bool
    EMAIL_USE_SSL: bool
    

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
        

    # @property
    # def DATABASE_URL(self) -> str:
    #     return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()
