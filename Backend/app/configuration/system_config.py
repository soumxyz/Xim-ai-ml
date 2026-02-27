from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Mesh Compliance Core"
    DEBUG: bool = False
    DATABASE_URL: str = "postgresql://user:password@localhost/mesh"
    
    class Config:
        env_file = ".env"

settings = Settings()
