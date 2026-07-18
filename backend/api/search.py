from fastapi import APIRouter, Depends, HTTPException, status
from shared.interfaces import SearchRequest, SearchResponse

router = APIRouter(prefix="/api/search", tags=['Search'])

@router.post("/", response_model=SearchResponse)
async def search(data: SearchRequest):
    """Assigned to: HARSH"""
    # TODO: Implement — HARSH
    raise HTTPException(status_code=501, detail="Not implemented")
