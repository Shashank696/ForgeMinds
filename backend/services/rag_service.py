class RAGService:
    """Retrieval-Augmented Generation service. Assigned to: HARSH"""

    def __init__(self):
        pass

    async def retrieve_context(self, query):
        """Retrieve relevant context for a query."""
        # TODO: Implement — HARSH
        raise NotImplementedError

    async def generate_response(self, query, context):
        """Generate response using LLM."""
        # TODO: Implement — HARSH
        raise NotImplementedError

    async def build_prompt(self, query, context):
        """Construct prompt for the LLM."""
        # TODO: Implement — HARSH
        raise NotImplementedError

    async def extract_citations(self, response_text, context):
        """Extract and map citations from response."""
        # TODO: Implement — HARSH
        raise NotImplementedError
