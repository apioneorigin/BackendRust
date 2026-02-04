"""
File Upload Security - Comprehensive file validation and sanitization.
"""

import hashlib
import mimetypes
import os
import re
import secrets
from dataclasses import dataclass
from typing import BinaryIO, Optional


# File size limits (bytes)
DEFAULT_MAX_SIZE = 10 * 1024 * 1024  # 10MB
SIZE_LIMITS = {
    "image": 5 * 1024 * 1024,  # 5MB
    "document": 10 * 1024 * 1024,  # 10MB
    "archive": 50 * 1024 * 1024,  # 50MB
}

# Allowed MIME types
ALLOWED_MIME_TYPES = {
    # Images
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/svg+xml",
    # Documents
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    # Text
    "text/plain",
    "text/csv",
    "text/markdown",
    "application/json",
    # Archives
    "application/zip",
    "application/x-tar",
    "application/gzip",
}

# Safe file extensions
SAFE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".txt", ".csv", ".md", ".json",
    ".zip", ".tar", ".gz",
}

# Dangerous extensions (always block)
DANGEROUS_EXTENSIONS = {
    ".exe", ".dll", ".msi", ".scr", ".pif", ".jar", ".vbs", ".vbe",
    ".js", ".jse", ".ws", ".wsf", ".wsc", ".wsh",
    ".sh", ".bash", ".ps1", ".bat", ".cmd", ".com",
    ".php", ".asp", ".aspx", ".jsp", ".py", ".rb", ".pl",
}

# Magic numbers for file type verification
MAGIC_NUMBERS = {
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/gif": [b"GIF87a", b"GIF89a"],
    "image/webp": [b"RIFF"],  # RIFF....WEBP
    "application/pdf": [b"%PDF"],
    "application/zip": [b"PK\x03\x04", b"PK\x05\x06"],
    "application/gzip": [b"\x1f\x8b"],
}

# Malware signatures (simplified)
MALWARE_SIGNATURES = [
    b"MZ",  # PE executable
    b"\x7fELF",  # ELF executable
    b"#!/",  # Shell script
    b"<?php",  # PHP
    b"<%",  # ASP/JSP
]


@dataclass
class FileValidationResult:
    """Result of file validation."""
    is_valid: bool
    error: Optional[str] = None
    sanitized_filename: Optional[str] = None
    detected_mime_type: Optional[str] = None
    file_hash: Optional[str] = None


class FileUploadValidator:
    """
    Comprehensive file upload validation.
    Checks MIME types, extensions, magic numbers, and content.
    """

    def __init__(
        self,
        max_size: int = DEFAULT_MAX_SIZE,
        allowed_mime_types: Optional[set[str]] = None,
        allowed_extensions: Optional[set[str]] = None,
    ):
        self.max_size = max_size
        self.allowed_mime_types = allowed_mime_types or ALLOWED_MIME_TYPES
        self.allowed_extensions = allowed_extensions or SAFE_EXTENSIONS

    def validate(
        self,
        file: BinaryIO,
        filename: str,
        content_type: Optional[str] = None,
    ) -> FileValidationResult:
        """
        Validate an uploaded file.
        Performs comprehensive security checks.
        """
        # Sanitize filename first
        sanitized_name = self._sanitize_filename(filename)
        if not sanitized_name:
            return FileValidationResult(
                is_valid=False,
                error="Invalid filename"
            )

        # Check extension
        ext = os.path.splitext(sanitized_name)[1].lower()
        if ext in DANGEROUS_EXTENSIONS:
            return FileValidationResult(
                is_valid=False,
                error=f"Dangerous file extension: {ext}"
            )

        if ext not in self.allowed_extensions:
            return FileValidationResult(
                is_valid=False,
                error=f"File extension not allowed: {ext}"
            )

        # Read file content
        file.seek(0)
        content = file.read()
        file.seek(0)

        # Check size
        if len(content) > self.max_size:
            return FileValidationResult(
                is_valid=False,
                error=f"File too large: {len(content)} bytes (max: {self.max_size})"
            )

        # Detect MIME type from content
        detected_mime = self._detect_mime_type(content, ext)

        # Verify MIME type matches extension
        if content_type and content_type not in self.allowed_mime_types:
            return FileValidationResult(
                is_valid=False,
                error=f"MIME type not allowed: {content_type}"
            )

        # Verify magic numbers
        if not self._verify_magic_number(content, detected_mime):
            return FileValidationResult(
                is_valid=False,
                error="File content does not match declared type"
            )

        # Check for malware signatures
        if self._has_malware_signature(content):
            return FileValidationResult(
                is_valid=False,
                error="File contains potentially dangerous content"
            )

        # Check for path traversal in content (for text files)
        if detected_mime and detected_mime.startswith("text/"):
            if self._has_path_traversal(content):
                return FileValidationResult(
                    is_valid=False,
                    error="File contains path traversal patterns"
                )

        # Calculate file hash
        file_hash = hashlib.sha256(content).hexdigest()

        return FileValidationResult(
            is_valid=True,
            sanitized_filename=sanitized_name,
            detected_mime_type=detected_mime,
            file_hash=file_hash,
        )

    def _sanitize_filename(self, filename: str) -> Optional[str]:
        """Sanitize a filename."""
        if not filename:
            return None

        # Remove path separators
        filename = filename.replace("/", "").replace("\\", "")

        # Remove null bytes
        filename = filename.replace("\x00", "")

        # Remove control characters
        filename = re.sub(r"[\x00-\x1f\x7f]", "", filename)

        # Remove special characters
        filename = re.sub(r'[<>:"|?*]', "", filename)

        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:250 - len(ext)] + ext

        # Ensure not empty after sanitization
        if not filename or filename == ".":
            return None

        return filename

    def _detect_mime_type(self, content: bytes, extension: str) -> Optional[str]:
        """Detect MIME type from content and extension."""
        # Try magic numbers first
        for mime, signatures in MAGIC_NUMBERS.items():
            for sig in signatures:
                if content.startswith(sig):
                    return mime

        # Fall back to extension-based detection
        mime_type, _ = mimetypes.guess_type(f"file{extension}")
        return mime_type

    def _verify_magic_number(self, content: bytes, mime_type: Optional[str]) -> bool:
        """Verify file content matches expected magic number."""
        if not mime_type or mime_type not in MAGIC_NUMBERS:
            return True  # No magic number check for this type

        signatures = MAGIC_NUMBERS[mime_type]
        return any(content.startswith(sig) for sig in signatures)

    def _has_malware_signature(self, content: bytes) -> bool:
        """Check for malware signatures."""
        for sig in MALWARE_SIGNATURES:
            if content.startswith(sig):
                return True
        return False

    def _has_path_traversal(self, content: bytes) -> bool:
        """Check for path traversal in text content."""
        try:
            text = content.decode("utf-8", errors="ignore")
            patterns = [r"\.\./", r"\.\.\\", r"%2e%2e"]
            return any(re.search(p, text, re.IGNORECASE) for p in patterns)
        except Exception:
            return False

    def generate_safe_filename(self, original_name: str) -> str:
        """Generate a safe random filename preserving extension."""
        ext = os.path.splitext(original_name)[1].lower()
        if ext not in self.allowed_extensions:
            ext = ""
        random_name = secrets.token_hex(16)
        return f"{random_name}{ext}"


# Global file upload validator instance
_file_validator: Optional[FileUploadValidator] = None


def get_file_validator() -> FileUploadValidator:
    """Get the global file upload validator instance."""
    global _file_validator
    if _file_validator is None:
        _file_validator = FileUploadValidator()
    return _file_validator
