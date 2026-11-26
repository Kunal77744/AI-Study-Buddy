"""Unit tests for services.pdf_service."""

import io

import pytest
from pypdf import PdfWriter

from services.pdf_service import (
    chunk_text_for_summary,
    extract_text_from_bytes,
    prepare_text_for_summary,
)
from utils.exceptions import FileProcessingError, ValidationError


def _make_blank_pdf_bytes(num_pages: int = 1) -> bytes:
    writer = PdfWriter()
    for _ in range(num_pages):
        writer.add_blank_page(width=200, height=200)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def _make_encrypted_pdf_bytes() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.encrypt("secret123")
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def test_extract_plain_text_success() -> None:
    content = b"# Study Notes\nNeural networks learn via backpropagation."
    result = extract_text_from_bytes("notes.md", content)
    assert result.extension == "md"
    assert "Neural networks" in result.text
    assert result.char_count == len(result.text)
    assert result.page_count is None
    assert len(result.file_hash) == 16


def test_extract_plain_text_non_utf8_fallback() -> None:
    content = b"Valid prefix \xff\xfe invalid utf8 bytes"
    result = extract_text_from_bytes("notes.txt", content)
    assert "Valid prefix" in result.text


def test_extract_plain_text_empty_raises() -> None:
    with pytest.raises(FileProcessingError, match="no readable text"):
        extract_text_from_bytes("blank.txt", b"   \n\t  ")


def test_extract_pdf_corrupted_raises() -> None:
    with pytest.raises(FileProcessingError, match="corrupted"):
        extract_text_from_bytes("bad.pdf", b"not-a-valid-pdf-header")


def test_extract_pdf_encrypted_raises() -> None:
    pdf_bytes = _make_encrypted_pdf_bytes()
    with pytest.raises(FileProcessingError, match="encrypted"):
        extract_text_from_bytes("locked.pdf", pdf_bytes)


def test_extract_pdf_zero_pages_raises() -> None:
    pdf_bytes = _make_blank_pdf_bytes(0)
    with pytest.raises(FileProcessingError, match="no pages"):
        extract_text_from_bytes("zero.pdf", pdf_bytes)


def test_extract_pdf_scanned_or_blank_raises() -> None:
    pdf_bytes = _make_blank_pdf_bytes(2)
    with pytest.raises(FileProcessingError, match="empty or scanned"):
        extract_text_from_bytes("scanned.pdf", pdf_bytes)


def test_extract_pdf_unsupported_extension_raises() -> None:
    with pytest.raises(ValidationError, match="Unsupported file type"):
        extract_text_from_bytes("image.png", b"1234")


def test_prepare_text_for_summary_truncates() -> None:
    text = "a" * 100
    trimmed, truncated = prepare_text_for_summary(text, max_chars=40)
    assert len(trimmed) == 40
    assert truncated is True

    short, not_truncated = prepare_text_for_summary("hello", max_chars=40)
    assert short == "hello"
    assert not_truncated is False


def test_chunk_text_for_summary_splits_and_bounds() -> None:
    short_chunks, short_trunc = chunk_text_for_summary("hello world", chunk_size=50)
    assert short_chunks == ["hello world"]
    assert short_trunc is False

    long_text = "\n\n".join([f"Paragraph {i} " + ("x" * 30) for i in range(6)])
    chunks, truncated = chunk_text_for_summary(long_text, chunk_size=60, max_chunks=2)
    assert len(chunks) == 2
    assert truncated is True
