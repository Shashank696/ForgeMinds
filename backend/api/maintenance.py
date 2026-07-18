"""
Maintenance Intelligence API endpoints.

Provides predictive maintenance predictions, root cause analysis,
and proactive alerting capabilities.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from shared.interfaces import (
    MaintenancePrediction,
    RCARequest,
    RCAResponse,
    ProactiveAlert,
    ErrorDetail,
    ErrorResponse,
)
from backend.services.maintenance_agent import maintenance_agent
from backend.services.rca_agent import rca_agent
from backend.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/maintenance", tags=['Maintenance Intelligence'])


@router.get(
    "/predictions",
    response_model=List[MaintenancePrediction],
    responses={500: {"model": ErrorResponse}},
)
async def get_predictions(
    equipment_id: Optional[str] = Query(
        None, description="Filter predictions for a specific equipment ID"
    ),
    criticality: Optional[str] = Query(
        None, description="Filter by criticality level (critical, high, medium, low)"
    ),
) -> List[MaintenancePrediction]:
    """Retrieve predictive maintenance predictions.

    Optionally filter by equipment_id and/or criticality level to narrow
    down the list of returned failure predictions.

    Args:
        equipment_id: Optional equipment identifier to filter predictions.
        criticality: Optional criticality level string to filter predictions.

    Returns:
        List of MaintenancePrediction objects sorted by risk level.

    Raises:
        HTTPException: 500 on internal error.
    """
    try:
        logger.info(
            "Predictions requested — equipment_id=%s criticality=%s",
            equipment_id,
            criticality,
        )
        predictions: List[MaintenancePrediction] = (
            await maintenance_agent.predict_failures(
                equipment_id=equipment_id,
                criticality=criticality,
            )
        )
        logger.info("Returned %d maintenance predictions", len(predictions))
        return predictions

    except NotImplementedError:
        logger.warning("maintenance_agent.predict_failures not yet implemented")
        return []
    except Exception as exc:
        logger.error(
            "Failed to fetch maintenance predictions: %s", exc, exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorDetail(
                code="PREDICTION_ERROR",
                message="An error occurred while fetching maintenance predictions.",
                details={"error": str(exc)},
            ).model_dump(),
        )


@router.post(
    "/rca",
    response_model=RCAResponse,
    responses={500: {"model": ErrorResponse}},
)
async def rca(data: RCARequest) -> RCAResponse:
    """Perform root cause analysis for an equipment failure.

    Analyzes the failure description against historical data, similar
    incidents, and knowledge graph relationships to identify probable
    root causes and recommend corrective actions.

    Args:
        data: The RCA request containing equipment_id,
              failure_description, and optional failure_date.

    Returns:
        RCAResponse with identified root causes, recommended actions,
        and related at-risk equipment.

    Raises:
        HTTPException: 500 on internal error.
    """
    try:
        logger.info(
            "RCA requested — equipment_id=%s description='%s'",
            data.equipment_id,
            data.failure_description[:80],
        )
        response: RCAResponse = await rca_agent.analyze_root_cause(request=data)
        logger.info(
            "RCA completed — %d root causes identified",
            len(response.root_causes),
        )
        return response

    except NotImplementedError:
        logger.warning("rca_agent.analyze_root_cause not yet implemented")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=ErrorDetail(
                code="NOT_IMPLEMENTED",
                message="Root cause analysis is not yet available.",
            ).model_dump(),
        )
    except Exception as exc:
        logger.error("RCA endpoint failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorDetail(
                code="RCA_ERROR",
                message="An error occurred during root cause analysis.",
                details={
                    "equipment_id": data.equipment_id,
                    "error": str(exc),
                },
            ).model_dump(),
        )


@router.get(
    "/alerts",
    response_model=List[ProactiveAlert],
    responses={500: {"model": ErrorResponse}},
)
async def get_alerts() -> List[ProactiveAlert]:
    """Retrieve proactive maintenance alerts.

    Returns system-generated alerts for detected failure patterns,
    overdue maintenance, and compliance deadlines related to equipment.

    Returns:
        List of ProactiveAlert objects ordered by severity.

    Raises:
        HTTPException: 500 on internal error.
    """
    try:
        logger.info("Fetching proactive maintenance alerts")
        alerts: List[ProactiveAlert] = await maintenance_agent.get_alerts()
        logger.info("Returned %d proactive alerts", len(alerts))
        return alerts

    except NotImplementedError:
        logger.warning("maintenance_agent.get_alerts not yet implemented")
        return []
    except Exception as exc:
        logger.error(
            "Failed to fetch maintenance alerts: %s", exc, exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorDetail(
                code="ALERTS_ERROR",
                message="An error occurred while fetching proactive alerts.",
                details={"error": str(exc)},
            ).model_dump(),
        )
