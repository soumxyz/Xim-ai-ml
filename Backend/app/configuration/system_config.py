from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Metrixa Compliance Core"
    DEBUG: bool = False
    DATABASE_URL: str = "postgresql://user:password@localhost/metrixa"
    
    class Config:
        env_file = ".env"

settings = Settings()
