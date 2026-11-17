from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    title: str = "YanaTaskTraker"
    debug: bool = True


settings = Settings()
