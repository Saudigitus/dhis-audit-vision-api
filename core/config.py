from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    ENVIRONMENT: str = "development"
    host: str
    port: int
    CORS_ALLOW_ORIGINS: str = ""
    DHIS2_CA_BUNDLE: str | None = None
    MAX_REQUEST_BODY_BYTES: int = 1_048_576
    LOG_MAX_BYTES: int = 262_144
    LOG_ROTATION_MAX_BYTES: int = 5_242_880
    LOG_ROTATION_BACKUP_COUNT: int = 5
    DHIS2_OBJECT_FIELDS: str = "id,name,displayName,code,created,lastUpdated"
    DHIS2_PROGRAM_DEPENDENCY_FIELDS: str = (
        "id,programStages[id,programStageDataElements[id,dataElement[id]],programStageSections[id]],"
        "programIndicators[id],programRules[id],programRuleVariables[id],trackedEntityType[id],"
        "categoryCombo[id],organisationUnits[id],attributeValues[attribute[id],value]"
    )
    DHIS2_DATASET_DEPENDENCY_FIELDS: str = (
        "id,dataSetElements[id,dataElement[id]],sections[id,dataElements[id]],categoryCombo[id],"
        "organisationUnits[id],indicators[id],attributeValues[attribute[id],value]"
    )

    SERVER_DHIS2_URL: str
    SERVER_DHIS2_AUTH: str
    SQL_VIEW_ID: str
    CONTROL_FILE_PATH: str
    DATA_BASE_DIR: str
    SECRET_KEY: str = Field(min_length=32)
    TOKEN_EXPIRE_MINUTES: int = 60
    ADMIN_USERNAME: str
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: SecretStr
    OFFSET_HOURS: int
    RETRIEVE_SQL_VIEW_ID: str
    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_HOST_USER: str
    EMAIL_HOST_PASSWORD: SecretStr
    EMAIL_USE_TLS: bool
    EMAIL_USE_SSL: bool

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key_entropy(cls, value: str) -> str:
        if len(value.encode("utf-8")) < 32:
            raise ValueError("SECRET_KEY must be at least 32 bytes")
        weak_values = {
            "replace_with_a_random_secret",
            "replace_with_a_random_secret_at_least_32_bytes",
            "changeme",
            "secret",
            "password",
        }
        if value in weak_values:
            raise ValueError("SECRET_KEY must not use a documented placeholder")
        return value

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
        

    # @property
    # def DATABASE_URL(self) -> str:
    #     return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def cors_allow_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ALLOW_ORIGINS.split(",") if origin.strip()]

settings = Settings()
