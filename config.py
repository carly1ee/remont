from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_NAME: str
    USER: str
    PASSWORD: str
    PORT_NAME: str
    HOST_NAME: str
    SECRET_KEY: str


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()