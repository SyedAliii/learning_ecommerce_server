import os
from io import StringIO
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

environment = os.getenv("ENVIRONMENT", "development")
if environment == "production":
    env_file = ".env.production"
elif environment == "development":
    env_file = ".env.development"
else:
    env_file = ".env"

secret_env = os.getenv("APP_ENV")
if secret_env and not os.path.exists(env_file):
    load_dotenv(stream=StringIO(secret_env))

class Settings(BaseSettings):
    PROJECT_NAME: str = "E-Commerce Server"
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 180
    DEBUG: bool = True 
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
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SENDER_EMAIL: str
    APP_PASSWORD: str

    class Config:
        env_file = env_file

settings = Settings()