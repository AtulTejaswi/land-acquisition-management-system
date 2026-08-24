"""Storage Service — abstracted file storage per spec D7.

Local /uploads volume for hackathon, abstracted behind StorageService interface
so it could swap to S3 later.
"""

import os
import uuid
import shutil
from typing import Optional
from app.core.config import settings


class StorageService:
    """Local file storage implementation with S3-ready interface."""

    @staticmethod
    def get_upload_dir() -> str:
        """Base upload directory."""
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        return settings.UPLOAD_DIR

    @staticmethod
    def save_file(
        file_content: bytes,
        file_name: str,
        project_id: Optional[str] = None,
        stage: Optional[str] = None,
        subfolder: str = "documents",
    ) -> str:
        """Save a file and return the relative path.

        Structure: {subfolder}/{project_id}/{stage}/{uuid}_{filename}
        S3-ready: the path structure mirrors bucket key patterns.
        """
        base_dir = StorageService.get_upload_dir()
        unique_name = f"{uuid.uuid4()}_{file_name}"

        path_parts = [subfolder]
        if project_id:
            path_parts.append(project_id)
        if stage:
            path_parts.append(stage)

        rel_dir = os.path.join(*path_parts)
        full_dir = os.path.join(base_dir, rel_dir)
        os.makedirs(full_dir, exist_ok=True)

        full_path = os.path.join(full_dir, unique_name)
        with open(full_path, "wb") as f:
            f.write(file_content)

        return f"/{rel_dir}/{unique_name}"

    @staticmethod
    def delete_file(file_path: str) -> bool:
        """Delete a file by relative path."""
        base_dir = StorageService.get_upload_dir()
        full_path = os.path.join(base_dir, file_path.lstrip("/"))
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False

    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Get file size in bytes."""
        base_dir = StorageService.get_upload_dir()
        full_path = os.path.join(base_dir, file_path.lstrip("/"))
        if os.path.exists(full_path):
            return os.path.getsize(full_path)
        return 0
