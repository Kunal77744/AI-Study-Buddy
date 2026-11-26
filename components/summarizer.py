"""Notes & Document Summarizer UI component."""

import hashlib

import streamlit as st

from config.settings import ALLOWED_FILE_EXTENSIONS, MAX_FILE_SIZE_MB, MAX_PDF_PAGES
from services.gemini_service import generate_text
from services.pdf_service import (
    DocumentExtractionResult,
    extract_text_from_bytes,
    prepare_text_for_summary,
)
from utils.exceptions import (
    ConfigurationError,
    GeminiAPIError,
    GeminiRateLimitError,
    StudyBuddyError,
)
from utils.validators import validate_non_empty_text


def _session_extract(filename: str, file_bytes: bytes) -> DocumentExtractionResult:
    """Cache document extraction in st.session_state so data stays isolated per user session."""
    cache_key = (filename, hashlib.sha256(file_bytes).hexdigest())
    cached = st.session_state.get("extracted_doc_cache")
    if isinstance(cached, tuple) and len(cached) == 2 and cached[0] == cache_key:
        return cached[1]
    result = extract_text_from_bytes(filename, file_bytes)
    st.session_state["extracted_doc_cache"] = (cache_key, result)
    return result


def render_summarizer() -> None:
    """Render the Notes & Document Summarizer section."""
    st.markdown("### 📝 Notes & Document Summarizer")
    st.caption(
        "Convert raw text, lecture notes, textbooks (PDF), or source code into "
        "high-retention summaries."
    )

    input_type = st.radio(
        "Input Source:",
        [
            "Text / Code Snippet",
            "Upload Document File (.pdf, .txt, .md, .py, .json)",
        ],
        horizontal=True,
    )

    raw_content = ""
    if input_type == "Text / Code Snippet":
        raw_content = st.text_area(
            "Paste your notes or code snippet here:",
            height=220,
            placeholder="Paste raw lecture notes, textbook excerpts, or code blocks here...",
        )
    else:
        uploaded_file = st.file_uploader(
            f"Upload Notes or PDF Document (max {MAX_FILE_SIZE_MB} MB, {MAX_PDF_PAGES} PDF pages)",
            type=list(ALLOWED_FILE_EXTENSIONS),
        )
        if uploaded_file is not None:
            try:
                with st.spinner("Extracting text from file..."):
                    result = _session_extract(uploaded_file.name, uploaded_file.getvalue())
                raw_content = result.text
                page_info = (
                    f", {result.pages_processed}/{result.page_count} pages"
                    if result.page_count is not None
                    else ""
                )
                st.success(
                    f"File '{result.filename}' loaded ({result.char_count:,} chars{page_info})."
                )
                if result.truncated_pages:
                    st.info(
                        f"Note: Only the first {MAX_PDF_PAGES} pages were extracted "
                        "to keep processing fast."
                    )
            except StudyBuddyError as exc:
                st.error(f"Notice: {exc}")
                raw_content = ""

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        summary_format = st.selectbox(
            "Summary Output Format",
            [
                "Structured Bullet Points",
                "Executive Overview",
                "Flashcard Q&A Pairs",
                "Code Analysis & Debugging Tips",
            ],
        )
    with col_s2:
        detail_level = st.select_slider(
            "Summary Detail Level",
            options=[
                "Concise (Key Highlights)",
                "Standard Balanced Summary",
                "In-Depth Detailed Analysis",
            ],
        )

    if st.button("✨ Summarize Document", type="primary", use_container_width=True):
        try:
            validated_text = validate_non_empty_text(raw_content, "Notes or document content")
            trimmed_text, was_truncated = prepare_text_for_summary(validated_text)
            if was_truncated:
                st.info(
                    f"Input exceeded {len(trimmed_text):,} characters and was trimmed "
                    "to fit summary limits."
                )

            prompt = (
                f"Summarize the following text in '{summary_format}' format "
                f"with detail level '{detail_level}'.\n\n"
                f'Content:\n"""\n{trimmed_text}\n"""'
            )
            system_prompt = (
                "You are a professional academic research assistant specializing in "
                "notes summarization."
            )
            with st.spinner("Creating your study summary..."):
                summary_output = generate_text(
                    prompt,
                    system_instruction=system_prompt,
                )
            st.session_state["last_summary"] = summary_output
        except ConfigurationError:
            st.error(
                "AI Study Assistant is currently unavailable. "
                "Please try again later."
            )
        except GeminiRateLimitError:
            st.error(
                "Too many requests right now. Please wait a moment and try again."
            )
        except GeminiAPIError:
            st.error(
                "Could not generate a summary right now. "
                "Please wait a moment and try again."
            )
        except StudyBuddyError as exc:
            st.error(f"Notice: {exc}")

    if "last_summary" in st.session_state:
        st.markdown("---")
        st.markdown("#### 📋 Generated Summary Output")
        st.markdown(st.session_state["last_summary"])
        st.download_button(
            label="📥 Download Summary (.md)",
            data=st.session_state["last_summary"],
            file_name="Study_Notes_Summary.md",
            mime="text/markdown",
        )
