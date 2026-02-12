"""
Centralized Logging Configuration for Reality Transformer Backend
Provides structured logging for all components with configurable levels
"""

import logging
import os
import sys
from typing import Optional
from datetime import datetime

_IS_PRODUCTION = os.getenv("ENVIRONMENT") == "production"
_DEFAULT_LEVEL = logging.INFO if _IS_PRODUCTION else logging.DEBUG

# Define log levels for different components
# In production, all components default to INFO to avoid verbose debug logs
COMPONENT_LEVELS = {
    'inference': _DEFAULT_LEVEL,
    'formulas': _DEFAULT_LEVEL,
    'articulation': logging.INFO,
    'reverse_causality': _DEFAULT_LEVEL,
    'consciousness': _DEFAULT_LEVEL,
    'value_organizer': _DEFAULT_LEVEL,
    'bottleneck': _DEFAULT_LEVEL,
    'leverage': _DEFAULT_LEVEL,
    'api': logging.INFO,
    'pipeline': logging.INFO,
    # Zero-fallback components
    'zero_fallback': logging.INFO,
    'priority_detector': _DEFAULT_LEVEL,
    'question_generator': _DEFAULT_LEVEL,
    'answer_mapper': _DEFAULT_LEVEL,
    'context_assembler': _DEFAULT_LEVEL,
    # Evidence-grounding components
    'evidence_grounding': logging.INFO,
    # Unity Principle components
    'unity_principle': _DEFAULT_LEVEL,
    'dual_pathway': _DEFAULT_LEVEL,
}


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for terminal output"""

    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m',
    }

    COMPONENT_COLORS = {
        'INFERENCE': '\033[94m',      # Light Blue
        'FORMULAS': '\033[95m',       # Light Magenta
        'ARTICULATION': '\033[96m',   # Light Cyan
        'REVERSE': '\033[93m',        # Light Yellow
        'VALIDATION': '\033[92m',     # Light Green
        'CONSCIOUSNESS': '\033[91m',  # Light Red
        'API': '\033[97m',            # White
    }

    def format(self, record):
        # Add color based on level
        level_color = self.COLORS.get(record.levelname)
        reset = self.COLORS['RESET']

        # Format the message
        record.levelname = f"{level_color}{record.levelname}{reset}"
        return super().format(record)


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Get a configured logger for a component

    Args:
        name: Component name (e.g., 'inference', 'formulas.cascade')
        level: Optional override for log level

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(f"oof.{name}")

    # Only configure if not already configured
    if not logger.handlers:
        # Set level from component config or default
        base_component = name.split('.')[0]
        log_level = level or COMPONENT_LEVELS.get(base_component)
        logger.setLevel(log_level)

        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)

        # Format: [COMPONENT] level - message
        formatter = ColoredFormatter(
            fmt='[%(name)s] %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Prevent propagation to root logger
        logger.propagate = False

    return logger


class CalculationLogger:
    """
    Specialized logger for tracking calculations and formula execution
    Provides structured logging for debugging formula chains
    """

    def __init__(self, component: str):
        self.logger = get_logger(component)
        self.component = component
        self.calculation_stack = []

    def start_calculation(self, name: str, inputs: dict):
        """Log the start of a calculation"""
        self.calculation_stack.append(name)
        depth = len(self.calculation_stack)
        indent = "  " * (depth - 1)

        input_summary = ", ".join(f"{k}={v:.3f}" if isinstance(v, float) else f"{k}={v}"
                                   for k, v in list(inputs.items())[:5])
        if len(inputs) > 5:
            input_summary += f", ... (+{len(inputs)-5} more)"

        self.logger.debug(f"{indent}[START] {name} | inputs: {input_summary}")

    def end_calculation(self, name: str, result: dict):
        """Log the end of a calculation with results"""
        if self.calculation_stack and self.calculation_stack[-1] == name:
            self.calculation_stack.pop()

        depth = len(self.calculation_stack)
        indent = "  " * depth

        result_summary = ", ".join(f"{k}={v:.3f}" if isinstance(v, float) else f"{k}={v}"
                                    for k, v in list(result.items())[:5])
        if len(result) > 5:
            result_summary += f", ... (+{len(result)-5} more)"

        self.logger.debug(f"{indent}[END] {name} | result: {result_summary}")

    def log_formula(self, formula_name: str, expression: str, inputs: dict, output: float):
        """Log a single formula execution"""
        input_str = ", ".join(f"{k}={v:.3f}" for k, v in inputs.items() if isinstance(v, (int, float)))
        self.logger.debug(f"  [FORMULA] {formula_name} = {output:.4f} | {expression[:50]}... | {input_str}")

    def log_tier(self, tier: int, formula_count: int, success_count: int):
        """Log tier completion"""
        self.logger.info(f"[TIER {tier}] Executed {success_count}/{formula_count} formulas")

    def log_error(self, context: str, error: Exception):
        """Log an error with context"""
        self.logger.error(f"[ERROR] {context}: {type(error).__name__}: {error}")

    def log_warning(self, message: str):
        """Log a warning"""
        self.logger.warning(f"[WARN] {message}")

    def log_metric(self, name: str, value: float, unit: str = ""):
        """Log a computed metric"""
        unit_str = f" {unit}" if unit else ""
        self.logger.info(f"[METRIC] {name} = {value:.4f}{unit_str}")


class PipelineLogger:
    """
    Logger for tracking the full inference pipeline
    """

    def __init__(self):
        self.logger = get_logger('pipeline')
        self.start_time = None
        self.steps = []

    def start_pipeline(self, query: str):
        """Log pipeline start"""
        self.start_time = datetime.now()
        self.steps = []
        query_preview = query[:100] + "..." if len(query) > 100 else query
        self.logger.info(f"{'='*60}")
        self.logger.info(f"[PIPELINE START] Query: {query_preview}")
        self.logger.info(f"{'='*60}")

    def log_step(self, step_name: str, details: dict = None):
        """Log a pipeline step"""
        elapsed = (datetime.now() - self.start_time).total_seconds() if self.start_time else None
        self.steps.append((step_name, elapsed))

        detail_str = ""
        if details:
            detail_str = " | " + ", ".join(f"{k}={v}" for k, v in details.items())

        self.logger.info(f"[STEP] {step_name} @ {f'{elapsed:.2f}' if elapsed is not None else 'N/A'}s{detail_str}")

    def end_pipeline(self, success: bool = True):
        """Log pipeline completion"""
        elapsed = (datetime.now() - self.start_time).total_seconds() if self.start_time else None
        status = "SUCCESS" if success else "FAILED"

        self.logger.info(f"{'='*60}")
        self.logger.info(f"[PIPELINE {status}] Total time: {f'{elapsed:.2f}' if elapsed is not None else 'N/A'}s | Steps: {len(self.steps)}")
        self.logger.info(f"{'='*60}")


# Global loggers for easy access
inference_logger = get_logger('inference')
formula_logger = CalculationLogger('formulas')
articulation_logger = get_logger('articulation')
reverse_logger = get_logger('reverse_causality')
consciousness_logger = get_logger('consciousness')
api_logger = get_logger('api')
pipeline_logger = PipelineLogger()

# Zero-fallback component loggers
zero_fallback_logger = get_logger('zero_fallback')
priority_logger = get_logger('priority_detector')
question_logger = get_logger('question_generator')
answer_mapper_logger = get_logger('answer_mapper')
context_logger = get_logger('context_assembler')

# Evidence-grounding logger
evidence_grounding_logger = get_logger('evidence_grounding')

# Unity Principle loggers
unity_principle_logger = get_logger('unity_principle')
dual_pathway_logger = get_logger('dual_pathway')
