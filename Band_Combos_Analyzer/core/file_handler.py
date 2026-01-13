"""
File Handler Utility

Shared utilities for handling file uploads, knowledge base management,
and file type detection across all modules.
"""

import os
import uuid
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)


class FileHandler:
    """
    Handles file operations for the analysis tool.

    Provides utilities for:
    - File uploads with session management
    - Knowledge base file management
    - File type detection
    - Temporary file cleanup
    """

    ALLOWED_EXTENSIONS = {'xml', 'txt', 'pdf', 'png', 'jpg', 'jpeg', 'bin', 'hex', 'json', 'csv'}

    def __init__(self, upload_folder: str, kb_folder: str, output_folder: str):
        """
        Initialize the file handler.

        Args:
            upload_folder: Base folder for temporary uploads
            kb_folder: Knowledge base folder
            output_folder: Output folder for reports
        """
        self.upload_folder = Path(upload_folder)
        self.kb_folder = Path(kb_folder)
        self.output_folder = Path(output_folder)

        # Ensure directories exist
        self.upload_folder.mkdir(parents=True, exist_ok=True)
        self.kb_folder.mkdir(parents=True, exist_ok=True)
        self.output_folder.mkdir(parents=True, exist_ok=True)

    def allowed_file(self, filename: str) -> bool:
        """
        Check if file extension is allowed.

        Args:
            filename: The filename to check

        Returns:
            True if allowed, False otherwise
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def create_session(self) -> str:
        """
        Create a new upload session.

        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())[:8]
        session_folder = self.upload_folder / session_id
        session_folder.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created session: {session_id}")
        return session_id

    def save_uploaded_file(self, file, session_id: str) -> Optional[str]:
        """
        Save an uploaded file to the session folder.

        Args:
            file: Werkzeug FileStorage object
            session_id: The session ID

        Returns:
            Path to saved file, or None if failed
        """
        if not file or not file.filename:
            return None

        if not self.allowed_file(file.filename):
            logger.warning(f"File type not allowed: {file.filename}")
            return None

        filename = secure_filename(file.filename)
        session_folder = self.upload_folder / session_id
        filepath = session_folder / filename

        try:
            file.save(str(filepath))
            logger.debug(f"Saved file: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            return None

    def cleanup_session(self, session_id: str) -> None:
        """
        Clean up temporary files for a session.

        Args:
            session_id: The session ID to clean up
        """
        session_folder = self.upload_folder / session_id
        if session_folder.exists():
            try:
                shutil.rmtree(session_folder)
                logger.debug(f"Cleaned up session: {session_id}")
            except Exception as e:
                logger.error(f"Failed to cleanup session {session_id}: {e}")

    # Knowledge Base Operations

    def get_kb_files(self) -> List[Dict[str, Any]]:
        """
        Get list of files in knowledge base.

        Returns:
            List of file info dictionaries
        """
        files = []
        if self.kb_folder.exists():
            for filepath in sorted(self.kb_folder.iterdir()):
                if filepath.is_file():
                    stat = filepath.stat()
                    files.append({
                        'name': filepath.name,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                    })
        return files

    def save_kb_file(self, file) -> bool:
        """
        Save a file to the knowledge base.

        Args:
            file: Werkzeug FileStorage object

        Returns:
            True if saved, False otherwise
        """
        if not file or not file.filename:
            return False

        if not self.allowed_file(file.filename):
            return False

        filename = secure_filename(file.filename)
        filepath = self.kb_folder / filename

        try:
            file.save(str(filepath))
            logger.info(f"Saved KB file: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save KB file: {e}")
            return False

    def delete_kb_file(self, filename: str) -> bool:
        """
        Delete a file from the knowledge base.

        Args:
            filename: Name of file to delete

        Returns:
            True if deleted, False otherwise
        """
        filepath = self.kb_folder / secure_filename(filename)
        if filepath.exists():
            try:
                filepath.unlink()
                logger.info(f"Deleted KB file: {filepath}")
                return True
            except Exception as e:
                logger.error(f"Failed to delete KB file: {e}")
                return False
        return False

    def get_kb_file_path(self, filename: str) -> Optional[str]:
        """
        Get full path to a KB file.

        Args:
            filename: Name of the file

        Returns:
            Full path or None if not found
        """
        filepath = self.kb_folder / secure_filename(filename)
        if filepath.exists():
            return str(filepath)
        return None

    # Output Operations

    def get_output_path(self, filename: str) -> str:
        """
        Get full path for an output file.

        Args:
            filename: Name of the output file

        Returns:
            Full path
        """
        return str(self.output_folder / secure_filename(filename))

    def generate_output_filename(self, prefix: str, extension: str) -> str:
        """
        Generate a timestamped output filename.

        Args:
            prefix: Filename prefix
            extension: File extension (without dot)

        Returns:
            Generated filename
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{prefix}_{timestamp}.{extension}"

    def save_output(self, content: str, filename: str, encoding: str = 'utf-8') -> str:
        """
        Save content to an output file.

        Args:
            content: Content to save
            filename: Filename
            encoding: File encoding

        Returns:
            Full path to saved file
        """
        filepath = self.output_folder / filename
        with open(filepath, 'w', encoding=encoding) as f:
            f.write(content)
        logger.debug(f"Saved output: {filepath}")
        return str(filepath)

    def read_output(self, filename: str, encoding: str = 'utf-8') -> Optional[str]:
        """
        Read content from an output file.

        Args:
            filename: Filename
            encoding: File encoding

        Returns:
            File content or None if not found
        """
        filepath = self.output_folder / secure_filename(filename)
        if filepath.exists():
            with open(filepath, 'r', encoding=encoding) as f:
                return f.read()
        return None

    def output_exists(self, filename: str) -> bool:
        """
        Check if an output file exists.

        Args:
            filename: Filename to check

        Returns:
            True if exists
        """
        filepath = self.output_folder / secure_filename(filename)
        return filepath.exists()
