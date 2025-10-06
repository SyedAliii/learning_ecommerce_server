from pydantic_settings import BaseSettings

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
    URL : str = "http://localhost:8000/"

    class Config:
        env_file = ".env"

settings = Settings()