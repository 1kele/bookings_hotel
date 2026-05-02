from fastapi import APIRouter, UploadFile
from fastapi import BackgroundTasks

from src.services.images import ImageService

router = APIRouter(prefix="/images", tags=["Изображения"])


@router.post("/")
def upload_image(file: UploadFile, background_tasks: BackgroundTasks):
    ImageService().upload_image(file, background_tasks)
