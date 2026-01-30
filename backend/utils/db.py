"""
Database utilities for common query patterns.
Eliminates duplicated access verification and pagination logic.
"""

import json
from typing import TypeVar, Type, Optional, Any, List, Tuple

from fastapi import HTTPException
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


async def get_or_404(
    db: AsyncSession,
    model: Type[T],
    resource_id: str,
    user_id: Optional[str] = None,
    organization_id: Optional[str] = None,
    user_field: str = "user_id",
    org_field: str = "organization_id",
    error_msg: Optional[str] = None,
) -> T:
    """
    Get a resource by ID with ownership verification, or raise 404.

    Args:
        db: Database session
        model: SQLAlchemy model class
        resource_id: Resource ID to fetch
        user_id: User ID for ownership check (optional)
        organization_id: Organization ID for ownership check (optional)
        user_field: Name of user_id field on model (default: "user_id")
        org_field: Name of organization_id field on model (default: "organization_id")
        error_msg: Custom error message (default: "{ModelName} not found")

    Returns:
        The model instance

    Raises:
        HTTPException: 404 if not found or access denied
    """
    conditions = [getattr(model, "id") == resource_id]

    if user_id and hasattr(model, user_field):
        conditions.append(getattr(model, user_field) == user_id)

    if organization_id and hasattr(model, org_field):
        conditions.append(getattr(model, org_field) == organization_id)

    result = await db.execute(select(model).where(*conditions))
    instance = result.scalar_one_or_none()

    if not instance:
        msg = error_msg or f"{model.__name__} not found"
        raise HTTPException(status_code=404, detail=msg)

    return instance


async def paginate(
    db: AsyncSession,
    query,
    offset: int = 0,
    limit: int = 20,
    order_by_field: Optional[Any] = None,
    order_desc: bool = True,
) -> Tuple[List[Any], int]:
    """
    Execute a paginated query with total count.

    Args:
        db: Database session
        query: SQLAlchemy select query
        offset: Number of items to skip
        limit: Maximum items to return
        order_by_field: Field to order by (optional)
        order_desc: Whether to order descending (default: True)

    Returns:
        Tuple of (items list, total count)
    """
    # Get total count efficiently
    count_result = await db.execute(query)
    total = len(count_result.scalars().all())

    # Apply ordering if specified
    if order_by_field is not None:
        query = query.order_by(desc(order_by_field) if order_desc else order_by_field)

    # Apply pagination
    result = await db.execute(query.offset(offset).limit(limit))
    items = result.scalars().all()

    return items, total


def safe_json_loads(data: Any) -> Any:
    """
    Safely parse JSON string or return data as-is if already parsed.

    Args:
        data: JSON string or already-parsed data

    Returns:
        Parsed data
    """
    if isinstance(data, str):
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            return data
    return data
