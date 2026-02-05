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


# =============================================================================
# Call 2 (Structured Data) Schema
# =============================================================================
# Call 2 streams natural language text and embeds structured JSON data
# between ===STRUCTURED_DATA_START=== and ===STRUCTURED_DATA_END=== markers.

# Articulated Insight schema (based on insight-articulation-final.pdf)
# 3-component structure: THE TRUTH → YOUR TRUTH → THE MARK
# Total: 160-250 words per insight
ARTICULATED_INSIGHT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        # Insight title (max 10 words) - displayed in popup header
        "title": {"type": "string"},               # Max 10-word title phrase for this insight

        # MICRO MOMENT (40-60 words): Fly-on-wall scene in user's world
        "micro_moment": {"type": "string"},        # Present tense, sensory, user's actual context

        # THE TRUTH (80-120 words): Analogy from outside user's domain
        "the_truth": {"type": "string"},           # Italicized analogy, present tense, sensory
        "the_truth_law": {"type": "string"},       # Bold one-line universal law (15-25 words)

        # YOUR TRUTH (50-80 words): Recognition + future protection
        "your_truth": {"type": "string"},          # "I see you" + "never miss again" trigger
        "your_truth_revelation": {"type": "string"},  # Bold revelation - what's now visible

        # THE MARK (30-50 words): Install the insight as permanent pattern
        "the_mark_name": {"type": "string"},       # Memorable name, 2-5 words (e.g., "The Permission Gap")
        "the_mark_prediction": {"type": "string"}, # Where they'll see this pattern
        "the_mark_identity": {"type": "string"}    # Bold new capability/identity
    },
    "required": [
        "title", "micro_moment",
        "the_truth", "the_truth_law",
        "your_truth", "your_truth_revelation",
        "the_mark_name", "the_mark_prediction", "the_mark_identity"
    ],
    "additionalProperties": False
}

# Row/Column option schema with insight_title (minimal) or full articulated_insight (after generation)
ROW_COLUMN_OPTION_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "label": {"type": "string"},
        "insight_title": {"type": "string"},  # Always present - title only from Call 2
        "articulated_insight": ARTICULATED_INSIGHT_SCHEMA  # Optional - full insight after user generates
    },
    "required": ["id", "label", "insight_title"]
}

# Cell schema (used in document matrix_data)
CELL_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "impact_score": {"type": "integer", "minimum": 0, "maximum": 100},
        "relationship": {"type": "string"},
        "dimensions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "value": {"type": "integer", "enum": [0, 50, 100]}
                },
                "required": ["name", "value"]
            },
            "minItems": 5,
            "maxItems": 5
        }
    },
    "required": ["impact_score", "dimensions"]
}

# Document schema - minimal from Call 2, expanded after matrix button generation
DOCUMENT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "matrix_data": {
            "type": "object",
            "properties": {
                "row_options": {
                    "type": "array",
                    "items": ROW_COLUMN_OPTION_SCHEMA
                },
                "column_options": {
                    "type": "array",
                    "items": ROW_COLUMN_OPTION_SCHEMA
                },
                "selected_rows": {"type": "array", "items": {"type": "integer"}},
                "selected_columns": {"type": "array", "items": {"type": "integer"}},
                "cells": {
                    "type": "object",
                    "additionalProperties": CELL_SCHEMA
                }  # Optional - only present after matrix button generation
            },
            "required": ["row_options", "column_options", "selected_rows", "selected_columns"]
        }
    },
    "required": ["id", "name", "matrix_data"]
}

# Preset schema
PRESET_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "description": {"type": "string"},
        "risk_level": {"type": "string"},
        "time_horizon": {"type": "string"},
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "order": {"type": "integer"},
                    "action": {"type": "string"},
                    "rationale": {"type": "string"}
                },
                "required": ["order", "action"]
            }
        }
    },
    "required": ["id", "name", "steps"]
}

# Follow-up question schema
QUESTION_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "question_text": {"type": "string"},
        "options": {
            "type": "object",
            "properties": {
                "option_1": {"type": "string"},
                "option_2": {"type": "string"},
                "option_3": {"type": "string"},
                "option_4": {"type": "string"}
            },
            "required": ["option_1", "option_2", "option_3", "option_4"]
        }
    },
    "required": ["question_text", "options"]
}

# Complete Call 2 structured data schema
CALL2_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "documents": {
            "type": "array",
            "items": DOCUMENT_SCHEMA,
            "minItems": 1
        },
        "presets": {
            "type": "array",
            "items": PRESET_SCHEMA
        },
        "follow_up_question": QUESTION_SCHEMA
    },
    "required": ["documents"]
}


def validate_call2_response(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate Call 2 structured data against schema.

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    try:
        jsonschema.validate(data, CALL2_SCHEMA)
        return True, []
    except jsonschema.ValidationError:
        # Collect all validation errors
        validator = jsonschema.Draft7Validator(CALL2_SCHEMA)
        for error in validator.iter_errors(data):
            path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"
            errors.append(f"{path}: {error.message}")

        return False, errors


def validate_and_log_call2(data: Dict[str, Any], provider: str) -> Dict[str, Any]:
    """
    Validate Call 2 structured data and log any errors.

    Post-hoc validation for both Anthropic and OpenAI (Call 2 uses marker-based extraction).

    Returns the data unchanged (validation is for logging/monitoring only).
    Does NOT raise errors - structured data is optional enhancement.
    """
    is_valid, errors = validate_call2_response(data)

    if not is_valid:
        api_logger.warning(f"[SCHEMA] {provider} Call 2 validation failed with {len(errors)} errors:")
        for error in errors[:5]:  # Log first 5 errors
            api_logger.warning(f"[SCHEMA]   - {error}")
        if len(errors) > 5:
            api_logger.warning(f"[SCHEMA]   ... and {len(errors) - 5} more errors")
    else:
        # Log validation success with summary
        doc_count = len(data.get("documents", []))
        preset_count = len(data.get("presets", []))
        has_question = "follow_up_question" in data
        api_logger.info(
            f"[SCHEMA] {provider} Call 2 validated: "
            f"{doc_count} docs, {preset_count} presets, question={'yes' if has_question else 'no'}"
        )

    return data


def validate_document_cells(document: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate that a document has the expected 100 cells (10x10 matrix).

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    matrix_data = document.get("matrix_data", {})
    cells = matrix_data.get("cells", {})

    # Check cell count
    if len(cells) < 100:
        errors.append(f"Expected 100 cells, got {len(cells)}")

    # Validate cell keys format (should be "row-col" like "0-0", "9-9")
    for key in cells:
        if not isinstance(key, str) or "-" not in key:
            errors.append(f"Invalid cell key format: {key}")
            continue

        parts = key.split("-")
        if len(parts) != 2:
            errors.append(f"Invalid cell key format: {key}")
            continue

        try:
            row, col = int(parts[0]), int(parts[1])
            if not (0 <= row <= 9 and 0 <= col <= 9):
                errors.append(f"Cell key out of range (0-9): {key}")
        except ValueError:
            errors.append(f"Cell key not numeric: {key}")

    # Validate dimension values (should be 0, 50, or 100)
    invalid_dim_values = []
    for key, cell in cells.items():
        dims = cell.get("dimensions", [])
        for dim in dims:
            value = dim.get("value")
            if value not in [0, 50, 100]:
                invalid_dim_values.append(f"{key}: {dim.get('name')}={value}")

    if invalid_dim_values:
        errors.append(f"Invalid dimension values (must be 0/50/100): {invalid_dim_values[:5]}")

    return len(errors) == 0, errors
