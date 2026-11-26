"""Document validation and text extraction service (PDF and plain-text formats)."""

import hashlib
import io
from dataclasses import dataclass

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from config.settings import (
    MAX_PDF_PAGES,
    MAX_SUMMARY_INPUT_CHARS,
    MIN_MEANINGFUL_TEXT_CHARS,
)
from utils.exceptions import FileProcessingError
from utils.validators import validate_uploaded_file_metadata


@dataclass(frozen=True)
class DocumentExtractionResult:
    """Structured result of extracting text from an uploaded document."""

    filename: str
    extension: str
    text: str
    char_count: int
    page_count: int | None
    pages_processed: int | None
    truncated_pages: bool
    file_hash: str


def extract_text_from_bytes(filename: str, file_bytes: bytes) -> DocumentExtractionResult:
    """Validate and extract text from uploaded file bytes.

    Supports PDF (via pypdf) and UTF-8/text files (.txt, .md, .py, .json).
    Raises ValidationError or FileProcessingError on invalid/unreadable input.
    """
    ext = validate_uploaded_file_metadata(filename, len(file_bytes))
    file_hash = hashlib.sha256(file_bytes).hexdigest()[:16]

    if ext == "pdf":
        return _extract_pdf_text(filename, file_bytes, file_hash)
    return _extract_plain_text(filename, ext, file_bytes, file_hash)


def _extract_pdf_text(
    filename: str, file_bytes: bytes, file_hash: str
) -> DocumentExtractionResult:
    """Extract text from PDF bytes with page limits and scanned-PDF detection."""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
    except (PdfReadError, Exception) as exc:
        raise FileProcessingError(
            f"Could not read PDF '{filename}'. The file may be corrupted."
        ) from exc

    if reader.is_encrypted:
        raise FileProcessingError(
            f"PDF '{filename}' is encrypted/password-protected. Please upload an unlocked PDF."
        )

    total_pages = len(reader.pages)
    if total_pages == 0:
        raise FileProcessingError(f"PDF '{filename}' contains no pages.")

    pages_to_read = min(total_pages, MAX_PDF_PAGES)
    truncated_pages = total_pages > MAX_PDF_PAGES

    chunks: list[str] = []
    for page_index in range(pages_to_read):
        page_text = reader.pages[page_index].extract_text() or ""
        if page_text.strip():
            chunks.append(page_text.strip())

    combined = "\n\n".join(chunks).strip()
    if len(combined) < MIN_MEANINGFUL_TEXT_CHARS:
        raise FileProcessingError(
            f"PDF '{filename}' appears to be empty or scanned (no selectable text found). "
            "OCR for image-only PDFs is not supported."
        )

    return DocumentExtractionResult(
        filename=filename,
        extension="pdf",
        text=combined,
        char_count=len(combined),
        page_count=total_pages,
        pages_processed=pages_to_read,
        truncated_pages=truncated_pages,
        file_hash=file_hash,
    )


def _extract_plain_text(
    filename: str, ext: str, file_bytes: bytes, file_hash: str
) -> DocumentExtractionResult:
    """Decode plain-text or source files with safe encoding fallback."""
    try:
        text = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        text = file_bytes.decode("utf-8", errors="replace")

    cleaned = text.strip()
    if not cleaned:
        raise FileProcessingError(f"File '{filename}' contains no readable text.")

    return DocumentExtractionResult(
        filename=filename,
        extension=ext,
        text=cleaned,
        char_count=len(cleaned),
        page_count=None,
        pages_processed=None,
        truncated_pages=False,
        file_hash=file_hash,
    )


def prepare_text_for_summary(
    text: str, max_chars: int = MAX_SUMMARY_INPUT_CHARS
) -> tuple[str, bool]:
    """Trim text to the configured API character limit.

    Returns (trimmed_text, was_truncated).
    """
    cleaned = text.strip()
    if len(cleaned) <= max_chars:
        return cleaned, False
    return cleaned[:max_chars], True


def chunk_text_for_summary(
    text: str,
    chunk_size: int = MAX_SUMMARY_INPUT_CHARS,
    max_chunks: int = 3,
) -> tuple[list[str], bool]:
    """Split long text into bounded chunks at paragraph/line boundaries.

    Returns (chunks, was_truncated_beyond_max_chunks).
    """
    cleaned = text.strip()
    if not cleaned:
        return [], False
    if len(cleaned) <= chunk_size:
        return [cleaned], False

    chunks: list[str] = []
    start = 0
    total_len = len(cleaned)
    while start < total_len and len(chunks) < max_chunks:
        end = min(start + chunk_size, total_len)
        if end < total_len:
            split_at = cleaned.rfind("\n\n", start, end)
            if split_at <= start:
                split_at = cleaned.rfind("\n", start, end)
            if split_at > start:
                end = split_at
        piece = cleaned[start:end].strip()
        if piece:
            chunks.append(piece)
        start = end

    was_truncated = start < total_len
    return chunks, was_truncated
