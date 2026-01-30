"""
Response builder utilities.
Auto-converts SQLAlchemy models to Pydantic response models.
"""

from typing import TypeVar, Type, Any

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def to_response(instance: Any, response_model: Type[T]) -> T:
    """
    Convert a SQLAlchemy model instance to a Pydantic response model.

    Automatically maps fields from the instance to the response model
    based on the response model's field names.

    Args:
        instance: SQLAlchemy model instance
        response_model: Pydantic response model class

    Returns:
        Instance of the response model

    Example:
        conversation = await get_or_404(db, ChatConversation, id, user_id)
        return to_response(conversation, ConversationResponse)
    """
    fields = response_model.model_fields.keys()
    data = {}

    for field in fields:
        if hasattr(instance, field):
            data[field] = getattr(instance, field)

    return response_model(**data)


def to_response_list(instances: list, response_model: Type[T]) -> list[T]:
    """
    Convert a list of SQLAlchemy model instances to Pydantic response models.

    Args:
        instances: List of SQLAlchemy model instances
        response_model: Pydantic response model class

    Returns:
        List of response model instances
    """
    return [to_response(i, response_model) for i in instances]
