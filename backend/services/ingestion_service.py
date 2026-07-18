class IngestionService:
    """Handles document ingestion pipeline. Assigned to: RUDRA"""

    def __init__(self):
        pass

    async def process_document(self, document_id):
        """Main pipeline to process a document."""
        # TODO: Implement — RUDRA
        raise NotImplementedError

    async def detect_type(self, file_path):
        """Detect document type."""
        # TODO: Implement — RUDRA
        raise NotImplementedError

    async def extract_text(self, document_id):
        """Extract text from a document."""
        # TODO: Implement — RUDRA
        raise NotImplementedError

    async def chunk_document(self, document_id):
        """Split document into chunks."""
        # TODO: Implement — RUDRA
        raise NotImplementedError
