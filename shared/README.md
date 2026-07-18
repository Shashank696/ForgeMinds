# Shared Contracts — ForgeMinds

> **🔒 LOCKED**: Only **SP** may modify files in this directory.

This directory contains the **Single Source of Truth** for all data models, enums, and constants used across the ForgeMinds platform.

## Files

| File | Purpose |
|------|---------|
| `enums.py` | All enum types (DocumentCategory, EquipmentType, AgentType, etc.) |
| `constants.py` | Application-wide constants (limits, defaults, model names) |
| `interfaces.py` | All Pydantic request/response models (API contracts) |

## Rules

1. **Do NOT modify** any file in this directory without SP's explicit approval.
2. All backend API endpoints MUST use the models from `interfaces.py` for request validation and response serialization.
3. All frontend API calls MUST expect responses matching these model shapes.
4. If you need a new model or field, **request it from SP**.

## Usage

### Backend (Python)
```python
from shared.interfaces import DocumentResponse, ChatRequest, ChatResponse
from shared.enums import DocumentCategory, AgentType
from shared.constants import MAX_FILE_SIZE_BYTES, DEFAULT_PAGE_SIZE
```

### Frontend (JavaScript)
See `frontend/src/utils/constants.js` for the JavaScript mirror of enums and constants.
