"""
Response builder utilities.
Auto-converts SQLAlchemy models to Pydantic response models.
"""

from enum import Enum
from typing import TypeVar, Type, Any, Optional, Dict, Callable

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def _get_value(instance: Any, field: str, field_map: Optional[Dict[str, str]] = None) -> Any:
    """Get field value, handling enums and field mappings."""
    # Check if there's a field mapping
    source_field = field_map.get(field, field) if field_map else field

    if not hasattr(instance, source_field):
        return None

    value = getattr(instance, source_field)

    # Auto-convert enums to their values
    if isinstance(value, Enum):
        return value.value

    return value


def to_response(
    instance: Any,
    response_model: Type[T],
    field_map: Optional[Dict[str, str]] = None,
) -> T:
    """
    Convert a SQLAlchemy model instance to a Pydantic response model.

    Automatically maps fields from the instance to the response model
    based on the response model's field names. Handles enums by extracting
    their .value automatically.

    Args:
        instance: SQLAlchemy model instance
        response_model: Pydantic response model class
        field_map: Optional dict mapping response fields to instance fields
                   e.g., {"metadata": "usage_metadata"} maps response.metadata
                   to instance.usage_metadata

    Returns:
        Instance of the response model

    Example:
        conversation = await get_or_404(db, ChatConversation, id, user_id)
        return to_response(conversation, ConversationResponse)

        # With field mapping:
        return to_response(record, UsageRecordResponse, {"metadata": "usage_metadata"})
    """
    fields = response_model.model_fields.keys()
    data = {}

    for field in fields:
        value = _get_value(instance, field, field_map)
        if value is not None or field in (field_map or {}):
            data[field] = value

    return response_model(**data)


def to_response_list(
    instances: list,
    response_model: Type[T],
    field_map: Optional[Dict[str, str]] = None,
) -> list[T]:
    """
    Convert a list of SQLAlchemy model instances to Pydantic response models.

    Args:
        instances: List of SQLAlchemy model instances
        response_model: Pydantic response model class
        field_map: Optional dict mapping response fields to instance fields

    Returns:
        List of response model instances
    """
    return [to_response(i, response_model, field_map) for i in instances]
