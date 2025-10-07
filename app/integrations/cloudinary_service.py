import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from app.core.config import settings
from fastapi import status, UploadFile
  
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

def upload_image(image: UploadFile, image_id: str):
    try:
        cloudinary.uploader.upload(image.file, public_id=image_id)
        optimize_url, _ = cloudinary_url(image_id, fetch_format="auto", quality="auto")
        return True, optimize_url
    except Exception as e:
        print(f"Error uploading image: {e}")
        return False, e

# # Transform the image: auto-crop to square aspect_ratio
# auto_crop_url, _ = cloudinary_url("shoes", width=500, height=500, crop="auto", gravity="auto")
# print(auto_crop_url)