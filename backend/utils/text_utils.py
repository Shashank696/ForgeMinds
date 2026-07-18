"""
ForgeMinds — Text Utility Functions.
Helpers for text cleaning, chunking, and sentence segmentation.
"""

import re
import unicodedata
from typing import List, Dict, Any


# Abbreviations common in industrial documents — should NOT trigger sentence splits.
_ABBREVIATIONS = {
    "Dr", "Mr", "Mrs", "Ms", "Jr", "Sr", "Prof",
    "No", "Vol", "Fig", "Ref", "Sec", "Ch", "App",
    "Rev", "Ed", "Dept", "Div", "Inc", "Ltd", "Corp",
    "Mfg", "Eng", "Maint", "Insp", "Oper", "Mgr",
    "Std", "Spec", "Req", "Min", "Max", "Avg",
    "Approx", "Temp", "Press", "Freq", "Dia",
    "Eq", "Pt", "vs", "etc", "e.g", "i.e",
}
_ABBREV_PATTERN = "|".join(re.escape(a) for a in _ABBREVIATIONS)


def clean_text(text: str) -> str:
    """
    Clean and normalize raw extracted text.

    - Strips null bytes and control characters (keeps newlines/tabs).
    - Normalises Unicode to NFKC form.
    - Fixes common encoding artefacts (â€™ → ', â€" → —, etc.).
    """
    if not text:
        return ""

    # Unicode normalisation
    text = unicodedata.normalize("NFKC", text)

    # Remove null bytes
    text = text.replace("\x00", "")

    # Strip control characters except \n, \r, \t
    text = re.sub(r"[^\S \n\r\t]", " ", text)  # non-printable whitespace → space
    text = re.sub(r"[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Fix common mojibake / encoding artefacts
    replacements = {
        "\u2019": "'", "\u2018": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-",
        "\u2026": "...",
        "\ufeff": "",   # BOM
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.strip()


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> List[Dict[str, Any]]:
    """
    Split text into overlapping chunks, preferring sentence boundaries.

    Returns:
        List of dicts: {text, start_char, end_char, chunk_index}
    """
    if not text:
        return []

    text_len = len(text)

    # Single-chunk case
    if text_len <= chunk_size:
        return [{
            "text": text,
            "start_char": 0,
            "end_char": text_len,
            "chunk_index": 0,
        }]

    chunks: List[Dict[str, Any]] = []
    start = 0
    chunk_index = 0

    while start < text_len:
        end = min(start + chunk_size, text_len)

        # Try to break at a sentence boundary (look back from `end`)
        if end < text_len:
            # Search for the last sentence-ending punctuation before `end`
            search_region = text[start:end]
            # Find last '. ', '! ', '? ', or newline
            best_break = -1
            for m in re.finditer(r"[.!?]\s|\n\n", search_region):
                candidate = m.end()
                # Only accept if we keep at least 40% of the chunk size
                if candidate >= chunk_size * 0.4:
                    best_break = candidate

            if best_break > 0:
                end = start + best_break

        chunk_text_content = text[start:end].strip()
        if chunk_text_content:
            chunks.append({
                "text": chunk_text_content,
                "start_char": start,
                "end_char": end,
                "chunk_index": chunk_index,
            })
            chunk_index += 1

        # Advance with overlap
        start = end - overlap if end < text_len else text_len

        # Safety: avoid infinite loop
        if start >= end:
            break

    return chunks


def normalize_whitespace(text: str) -> str:
    """
    Collapse multiple spaces to a single space and multiple newlines
    to a double newline. Strip leading/trailing whitespace.
    """
    if not text:
        return ""

    # Collapse multiple blank lines into a double newline
    text = re.sub(r"\n\s*\n", "\n\n", text)

    # Collapse runs of spaces/tabs (within a line) to single space
    text = re.sub(r"[^\S\n]+", " ", text)

    # Strip leading/trailing whitespace from each line
    lines = [line.strip() for line in text.splitlines()]
    text = "\n".join(lines)

    return text.strip()


def extract_sentences(text: str) -> List[str]:
    """
    Split text into sentences using regex, handling common industrial
    abbreviations so they do not cause false splits.

    Returns:
        List of sentence strings.
    """
    if not text:
        return []

    # Temporarily protect abbreviations by replacing their trailing dot
    # with a sentinel character (Unicode PUA U+E000) to prevent false splits
    _SENTINEL = "\ue000"
    protected = text
    for abbr in _ABBREVIATIONS:
        # Case-insensitive search and replace "No." -> "No<sentinel>"
        pattern = re.compile(rf"\b({re.escape(abbr)})\.", re.IGNORECASE)
        protected = pattern.sub(lambda m: m.group(1) + _SENTINEL, protected)

    # Split on sentence-ending punctuation followed by whitespace or end
    raw_sentences = re.split(r"(?<=[.!?])\s+", protected)

    # Restore protected dots and clean up
    sentences = []
    for s in raw_sentences:
        s = s.replace(_SENTINEL, ".").strip()
        if s:
            sentences.append(s)

    return sentences
