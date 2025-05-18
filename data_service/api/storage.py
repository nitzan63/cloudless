from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
import io
from services.storage.local_storage import LocalStorageService
# from services.storage.google_storage import GoogleStorageService

router = APIRouter()
storage_service = LocalStorageService()  # or GoogleStorageService()

@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    result = storage_service.upload_file(content, file.filename)
    return result

@router.get("/storage/get-file")
def get_file(file_path: str):
    result = storage_service.get_file(file_path)
    if result['status'] != 'success':
        raise HTTPException(status_code=404, detail=result['message'])

    return StreamingResponse(
        io.BytesIO(result['file_content']),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={result['file_name']}"}
    )

@router.delete("/delete")
def delete(file_path: str = Form(...)):
    result = storage_service.delete_file(file_path)
    return result
