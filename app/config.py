from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    title: str = "YanaTaskTraker"
    debug: bool = True
    description: str = "Pet-project 1. TaskTracker."


settings = Settings()
