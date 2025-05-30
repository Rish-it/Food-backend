from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    database_url: str = Field(..., env="DATABASE_URL")
    secret_key: str = "fallback-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Service ports
    user_service_port: int = Field(default=8001, env="USER_SERVICE_PORT")
    restaurant_service_port: int = Field(default=8002, env="RESTAURANT_SERVICE_PORT")
    delivery_service_port: int = Field(default=8003, env="DELIVERY_SERVICE_PORT")
    
    # Service URLs
    user_service_url: str = Field(default="http://localhost:8001", env="USER_SERVICE_URL")
    restaurant_service_url: str = Field(default="http://localhost:8002", env="RESTAURANT_SERVICE_URL")
    delivery_service_url: str = Field(default="http://localhost:8003", env="DELIVERY_SERVICE_URL")
    
    class Config:
        env_file = ".env"

settings = Settings()