from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int 
    DB_USER: str
    DB_USER: str
    DB_PASSWORD: str
    
    
settings = Settings()