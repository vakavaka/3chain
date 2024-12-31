import os
from typing import Optional
import logging
from utils import safe_path_join, validate_file_type, sanitize_filename

logger = logging.getLogger(__name__)

class DocumentManager:
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.allowed_extensions = {'.pdf', '.txt', '.doc', '.docx'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB

    def add_document(self, file_path: str) -> bool:
        """Add document with proper validation and error handling."""
        try:
            # Validate file path
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return False

            # Validate file type
            if not validate_file_type(file_path, self.allowed_extensions):
                logger.error(f"Invalid file type: {file_path}")
                return False

            # Check file size
            if os.path.getsize(file_path) > self.max_file_size:
                logger.error(f"File too large: {file_path}")
                return False

            # Sanitize filename
            safe_name = sanitize_filename(os.path.basename(file_path))
            
            # Create safe destination path
            dest_path = safe_path_join(self.base_path, safe_name)

            # Check for duplicates
            if os.path.exists(dest_path):
                logger.warning(f"File already exists: {dest_path}")
                return False

            # Copy file
            with open(file_path, 'rb') as src, open(dest_path, 'wb') as dst:
                dst.write(src.read())

            return True

        except Exception as e:
            logger.error(f"Error adding document: {e}")
            return False