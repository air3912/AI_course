from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings


class FileService:
    async def save_upload(self, file: UploadFile) -> str:
        target_dir = Path(settings.upload_dir).resolve()
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / file.filename
        content = await file.read()
        target_path.write_bytes(content)
        return str(target_path)
