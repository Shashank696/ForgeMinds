"""
Compliance Intelligence API endpoints.

Provides compliance posture overview, gap detection, targeted assessments,
and evidence package generation for regulatory audits.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Any

from shared.interfaces import (
    ComplianceOverview,
    ComplianceGap,
    ComplianceAssessRequest,
    ErrorDetail,
    ErrorResponse,
)
from backend.services.compliance_agent import compliance_agent
from backend.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/compliance", tags=['Compliance Intelligence'])


@router.get(
    "/status",
    response_model=ComplianceOverview,
    responses={500: {"model": ErrorResponse}},
)
async def get_status() -> ComplianceOverview:
    """Retrieve the overall compliance posture.

    Returns a high-level compliance overview including the aggregate
    compliance score and per-regulation breakdowns.

    Returns:
        ComplianceOverview with overall_compliance_score and by_regulation.

    Raises:
        HTTPException: 500 on internal error.
    """
    try:
        logger.info("Fetching compliance status overview")
        overview: ComplianceOverview = await compliance_agent.get_status()
        logger.info(
            "Compliance overview — score=%.2f regulations=%d",
            overview.overall_compliance_score,
            len(overview.by_regulation),
        )
        return overview

    except NotImplementedError:
        logger.warning("compliance_agent.get_status not yet implemented")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=ErrorDetail(
                code="NOT_IMPLEMENTED",
                message="Compliance status is not yet available.",
            ).model_dump(),
        )
    except Exception as exc:
        logger.error(
            "Failed to fetch compliance status: %s", exc, exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorDetail(
                code="COMPLIANCE_STATUS_ERROR",
                message="An error occurred while fetching compliance status.",
                details={"error": str(exc)},
            ).model_dump(),
        )


@router.get(
    "/gaps",
    response_model=List[ComplianceGap],
    responses={500: {"model": ErrorResponse}},
)
async def get_gaps() -> List[ComplianceGap]:
    """Detect and list all compliance gaps.

    Scans across all tracked regulations and equipment to identify
    non-compliant or partially compliant areas.

    Returns:
        List of ComplianceGap objects describing each detected gap.

    Raises:
        HTTPException: 500 on internal error.
    """
    try:
        logger.info("Detecting compliance gaps")
        gaps: List[ComplianceGap] = await compliance_agent.detect_gaps()
        logger.info("Detected %d compliance gaps", len(gaps))
        return gaps

    except NotImplementedError:
        logger.warning("compliance_agent.detect_gaps not yet implemented")
        return []
    except Exception as exc:
        logger.error(
            "Failed to detect compliance gaps: %s", exc, exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorDetail(
                code="GAPS_ERROR",
                message="An error occurred while detecting compliance gaps.",
                details={"error": str(exc)},
            ).model_dump(),
        )


@router.post(
    "/assess",
    response_model=List[ComplianceGap],
    responses={500: {"model": ErrorResponse}},
)
async def assess(data: ComplianceAssessRequest) -> List[ComplianceGap]:
    """Perform a targeted compliance assessment.

    Assesses compliance for a specific regulation code, optionally
    scoped to a subset of equipment IDs.

    Args:
        data: The assessment request containing regulation_code and
              optional equipment_ids to scope the assessment.

    Returns:
        List of ComplianceGap objects found for the targeted assessment.

    Raises:
        HTTPException: 500 on internal error.
    """
    try:
        logger.info(
            "Compliance assessment requested — regulation=%s equipment_ids=%s",
            data.regulation_code,
            data.equipment_ids,
        )
        gaps: List[ComplianceGap] = await compliance_agent.assess_compliance(
            request=data,
        )
        logger.info(
            "Assessment completed — %d gaps found for regulation=%s",
            len(gaps),
            data.regulation_code,
        )
        return gaps

    except NotImplementedError:
        logger.warning("compliance_agent.assess_compliance not yet implemented")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=ErrorDetail(
                code="NOT_IMPLEMENTED",
                message="Compliance assessment is not yet available.",
            ).model_dump(),
        )
    except Exception as exc:
        logger.error(
            "Compliance assessment failed: %s", exc, exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorDetail(
                code="ASSESS_ERROR",
                message="An error occurred during compliance assessment.",
                details={
                    "regulation_code": data.regulation_code,
                    "error": str(exc),
                },
            ).model_dump(),
        )


@router.get(
    "/evidence-package/{regulation_code}",
    responses={500: {"model": ErrorResponse}},
)
async def get_evidence_package(regulation_code: str) -> Dict[str, Any]:
    """Generate an evidence package for a regulatory audit.

    Assembles all supporting documents, assessment records, and
    compliance artifacts for the specified regulation code into a
    structured evidence bundle.

    Args:
        regulation_code: The regulation identifier to generate evidence for
                         (e.g., 'OISD-STD-137', 'PESO-SMPV').

    Returns:
        Dictionary containing the evidence package with documents,
        assessment records, and metadata.

    Raises:
        HTTPException: 500 on internal error.
    """
    try:
        logger.info(
            "Generating evidence package for regulation=%s", regulation_code
        )
        evidence: dict = await compliance_agent.generate_evidence(
            regulation_code=regulation_code,
        )
        logger.info(
            "Evidence package generated for regulation=%s keys=%s",
            regulation_code,
            list(evidence.keys()) if evidence else [],
        )
        return evidence

    except NotImplementedError:
        logger.warning(
            "compliance_agent.generate_evidence not yet implemented"
        )
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=ErrorDetail(
                code="NOT_IMPLEMENTED",
                message="Evidence package generation is not yet available.",
            ).model_dump(),
        )
    except Exception as exc:
        logger.error(
            "Evidence package generation failed for regulation=%s: %s",
            regulation_code,
            exc,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorDetail(
                code="EVIDENCE_ERROR",
                message="An error occurred while generating the evidence package.",
                details={
                    "regulation_code": regulation_code,
                    "error": str(exc),
                },
            ).model_dump(),
        )
