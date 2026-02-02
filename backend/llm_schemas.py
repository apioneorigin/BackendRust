"""
Shared JSON schemas for LLM responses.

Used for:
- OpenAI: Pre-hoc enforcement (strict JSON schema)
- Anthropic: Post-hoc validation (validate after response)

Single source of truth for expected LLM output structure.
"""

import jsonschema
from typing import Any, Dict, List, Tuple
import logging

api_logger = logging.getLogger("api")


# Call 1 (Evidence Extraction) Schema
CALL1_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "user_identity": {"type": "string"},
        "goal": {"type": "string"},
        "s_level": {
            "type": "object",
            "properties": {
                "current": {"type": "number"},
                "confidence": {"type": "number"},
                "in_transition": {"type": "boolean"},
                "transition_direction": {
                    "type": "string",
                    "enum": ["up", "down", "stable"]
                },
                "reasoning": {"type": "string"}
            },
            "required": ["current", "confidence", "in_transition", "transition_direction", "reasoning"],
            "additionalProperties": False
        },
        "query_pattern": {"type": "string"},
        "goal_category": {
            "type": "string",
            "enum": ["achievement", "relationship", "peace", "transformation"]
        },
        "emotional_undertone": {
            "type": "string",
            "enum": ["urgency", "uncertainty", "curiosity", "openness", "neutral"]
        },
        "domain": {
            "type": "string",
            "enum": ["business", "personal", "health", "spiritual"]
        },
        "web_research_summary": {"type": "string"},
        "search_queries_used": {"type": "array", "items": {"type": "string"}},
        "key_facts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "fact": {"type": "string"},
                    "source": {"type": "string"},
                    "relevance": {"type": "string"}
                },
                "required": ["fact", "source", "relevance"],
                "additionalProperties": False
            }
        },
        "search_guidance": {
            "type": "object",
            "properties": {
                "high_priority_values": {"type": "array", "items": {"type": "string"}},
                "evidence_search_queries": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "target_value": {"type": "string"},
                            "search_query": {"type": "string"},
                            "proof_type": {"type": "string"}
                        },
                        "required": ["target_value", "search_query", "proof_type"],
                        "additionalProperties": False
                    }
                },
                "consciousness_to_reality_mappings": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "consciousness_value": {"type": "string"},
                            "observable_reality": {"type": "string"},
                            "proof_search": {"type": "string"}
                        },
                        "required": ["consciousness_value", "observable_reality", "proof_search"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["high_priority_values", "evidence_search_queries", "consciousness_to_reality_mappings"],
            "additionalProperties": False
        },
        "observations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "var": {"type": "string"},
                    "value": {"type": "number"},
                    "confidence": {"type": "number"},
                    "reasoning": {"type": "string"}
                },
                "required": ["var", "value", "confidence", "reasoning"],
                "additionalProperties": False
            }
        },
        "targets": {"type": "array", "items": {"type": "string"}},
        "relevant_oof_components": {"type": "array", "items": {"type": "string"}},
        "missing_operator_priority": {
            "type": "array",
            "items": {"type": "string"}
        },
        "conversation_title": {"type": "string"}
    },
    "required": [
        "user_identity", "goal", "s_level", "query_pattern", "goal_category",
        "emotional_undertone", "domain", "web_research_summary", "search_queries_used",
        "key_facts", "search_guidance", "observations", "targets",
        "relevant_oof_components", "missing_operator_priority", "conversation_title"
    ],
    "additionalProperties": False
}

# OpenAI format wrapper (includes name and strict flag)
CALL1_OPENAI_SCHEMA: Dict[str, Any] = {
    "type": "json_schema",
    "name": "evidence_extraction",
    "schema": CALL1_SCHEMA,
    "strict": True
}


def validate_call1_response(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate Call 1 response against schema.

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    try:
        jsonschema.validate(data, CALL1_SCHEMA)
        return True, []
    except jsonschema.ValidationError as e:
        # Collect all validation errors
        validator = jsonschema.Draft7Validator(CALL1_SCHEMA)
        for error in validator.iter_errors(data):
            path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"
            errors.append(f"{path}: {error.message}")

        return False, errors


def validate_and_log_call1(data: Dict[str, Any], provider: str) -> Dict[str, Any]:
    """
    Validate Call 1 response and log any errors.

    For Anthropic: Post-hoc validation (response already generated)
    For OpenAI: Should always pass (pre-hoc enforcement)

    Returns the data unchanged (validation is for logging/monitoring only).
    Raises ValueError if critical fields are missing.
    """
    is_valid, errors = validate_call1_response(data)

    if not is_valid:
        api_logger.warning(f"[SCHEMA] {provider} Call 1 validation failed with {len(errors)} errors:")
        for error in errors[:5]:  # Log first 5 errors
            api_logger.warning(f"[SCHEMA]   - {error}")
        if len(errors) > 5:
            api_logger.warning(f"[SCHEMA]   ... and {len(errors) - 5} more errors")
    else:
        api_logger.info(f"[SCHEMA] {provider} Call 1 response validated successfully")

    # Check critical fields that we absolutely need
    critical_fields = ["observations", "targets", "search_guidance"]
    missing_critical = [f for f in critical_fields if f not in data or not data[f]]

    if missing_critical:
        raise ValueError(f"Critical fields missing from {provider} response: {missing_critical}")

    return data
