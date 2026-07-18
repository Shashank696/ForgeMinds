"""
ForgeMinds — Shared Constants (Single Source of Truth).

LOCKED: Only SP may modify this file.
"""

# ─── Application ─────────────────────────────────────────

APP_NAME = "ForgeMinds"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "AI-powered Industrial Knowledge Intelligence Platform"

# ─── File Upload ─────────────────────────────────────────

MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

ALLOWED_FILE_EXTENSIONS = {
    ".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif",
    ".xlsx", ".xls", ".csv",
    ".docx", ".doc", ".txt",
    ".pptx", ".ppt",
    ".eml", ".msg",
}

# ─── Document Chunking ──────────────────────────────────

DEFAULT_CHUNK_SIZE = 1000       # characters
DEFAULT_CHUNK_OVERLAP = 200     # characters

# ─── Embedding ───────────────────────────────────────────

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

# ─── Vector Database ────────────────────────────────────

QDRANT_COLLECTION_NAME = "document_chunks"

# ─── Pagination ──────────────────────────────────────────

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# ─── Authentication ─────────────────────────────────────

JWT_ALGORITHM = "HS256"
JWT_EXPIRY_MINUTES = 1440  # 24 hours

# ─── Cache ───────────────────────────────────────────────

CACHE_TTL_SECONDS = 3600        # 1 hour
LLM_CACHE_TTL_SECONDS = 86400   # 24 hours

# ─── Knowledge Graph ────────────────────────────────────

MAX_GRAPH_DEPTH = 3
DEFAULT_GRAPH_DEPTH = 2
MAX_GRAPH_NODES = 500

# ─── Search ──────────────────────────────────────────────

DEFAULT_SEARCH_LIMIT = 10
MAX_SEARCH_LIMIT = 50
SIMILARITY_THRESHOLD = 0.5

# ─── LLM ─────────────────────────────────────────────────

DEFAULT_LLM_MODEL = "gemini-2.0-flash"
FALLBACK_LLM_MODEL = "gemini-1.5-flash"
MAX_LLM_TOKENS = 4096
LLM_TEMPERATURE = 0.3

# ─── Error Codes ─────────────────────────────────────────

ERROR_NOT_FOUND = "NOT_FOUND"
ERROR_VALIDATION = "VALIDATION_ERROR"
ERROR_UNAUTHORIZED = "UNAUTHORIZED"
ERROR_FORBIDDEN = "FORBIDDEN"
ERROR_INTERNAL = "INTERNAL_ERROR"
ERROR_NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
ERROR_FILE_TOO_LARGE = "FILE_TOO_LARGE"
ERROR_UNSUPPORTED_FILE = "UNSUPPORTED_FILE_TYPE"
ERROR_PROCESSING_FAILED = "PROCESSING_FAILED"
ERROR_LLM_ERROR = "LLM_ERROR"
