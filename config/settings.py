from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    NAME: str
    API_ENDPOINT: str
    STORAGE_DIRECTORY: str

    MATHPIX_APP_ID: str
    MATHPIX_APP_KEY: str
    MATHPIX_DAILY_OCR_REQUESTS_LIMIT: int

    OPENAI_API_KEY: str
    WHISPER_TRANSCRIPTION_DEVICE: str

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator('BACKEND_CORS_ORIGINS', pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith('['):
            return [i.strip() for i in v.split(',')]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    POSTGRES_SERVER: str
    POSTGRES_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URI: Optional[PostgresDsn] = None

    @validator('DATABASE_URI', pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme='postgresql',
            user=values.get('POSTGRES_USER'),
            password=values.get('POSTGRES_PASSWORD'),
            host=values.get('POSTGRES_SERVER'),
            port=values.get('POSTGRES_USER'),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_PASSWORD: Union[str, None] = None

    OPENSEARCH_HOST: str
    OPENSEARCH_PORT: str
    OPENSEARCH_USERNAME: str
    OPENSEARCH_PASSWORD: str

    class Config:
        case_sensitive = True
        env_file = '.env'


settings = Settings()
