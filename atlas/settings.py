from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_server: str = "localhost"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_port: str = "5432"
    postgres_db:str = "postgres"