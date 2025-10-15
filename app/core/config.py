import os
from pydantic_settings import BaseSettings

environment = os.getenv("ENVIRONMENT", "development")
if environment == "production":
    env_file = ".env.production"
elif environment == "development":
    env_file = ".env.development"

class Settings(BaseSettings):
    PROJECT_NAME: str = "E-Commerce Server"
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 180
    DEBUG: bool = True 
    APP_PASSWORD: str
    SENDER_EMAIL: str
    PRODUCT_IMAGES_DIR: str = "assets/product_images/"
    ROOT_FOLDER: str = "app/"
    FUZZY_SEARCH_THRESHOLD: int = 60
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    FRONTEND_URL: str
    FRONTEND_FALLBACK_URL: str
    FRONTEND_SPECIFIC_BROWSER_URL: str
    REDIS_URL: str
    PRODUCT_UPDATE_CHANNEL: str = f"product"

    class Config:
        env_file = env_file

settings = Settings()