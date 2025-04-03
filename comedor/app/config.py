from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Configuración básica
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720
    DATABASE_URL: str = "sqlite+aiosqlite:///./hotel.db"
    
    # Configuración CORS como string - ¡SIMPLE!
    CORS_ORIGINS: str = "http://localhost:3000"
    
    # Otras configuraciones
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    ADMIN_EMAIL: str
    INITIAL_CATEGORIES: str = "Bebidas,Comidas,Postres,Snacks"
    DEMO_ROOMS: str = "101:Gomez,102:Perez,103:Lopez"

    class Config:
        env_file = ".env"

settings = Settings()