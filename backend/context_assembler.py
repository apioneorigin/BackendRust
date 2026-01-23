"""
Context Assembler - Builds LLM Context from Session State

Assembles context for LLM prompts including:
- Current operator values and their sources
- Missing operators that need to be collected
- Historical context from previous interactions
- Priority information for targeted questioning

ZERO-FALLBACK MODE: Context clearly indicates which operators are missing.
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from session_store import SessionStore, SessionState, OperatorSource


@dataclass
class AssembledContext:
    """Context assembled for LLM consumption"""
    session_id: str
    original_query: str
    operator_summary: str
    missing_summary: str
    historical_context: str
    priority_operators: List[str]
    full_context_prompt: str


class ContextAssembler:
    """
    Assembles context from session state for LLM prompts.

    Creates structured context that helps the LLM understand:
    - What information is already known
    - What information is missing
    - What should be prioritized for collection
    """

    # Operator descriptions for context
    OPERATOR_DESCRIPTIONS = {
        'Psi': 'consciousness quality/field coherence',
        'K': 'karmic load/accumulated impressions',
        'M': 'maya/illusion/veiling power',
        'G': 'grace/divine support available',
        'W': 'witness consciousness/observer presence',
        'A': 'awareness/present-moment attention',
        'P': 'presence/being here now',
        'E': 'equanimity/emotional balance',
        'V': 'void tolerance/emptiness capacity',
        'L': 'love/heart openness',
        'R': 'resistance/opposition to what is',
        'At': 'attachment/clinging to outcomes',
        'Av': 'aversion/pushing away experiences',
        'Se': 'service orientation/selflessness',
        'Ce': 'celebration/cleaning/purification',
        'Su': 'suffering/distress level',
        'As': 'aspiration/spiritual longing',
        'Fe': 'faith/trust in the process',
        'De': 'devotion/heart connection',
        'Re': 'receptivity/openness to receive',
        'Hf': 'habit force/conditioning strength',
        'Sa': 'samskara/deep impressions',
        'Bu': 'buddhi/discriminative wisdom',
        'Ma': 'manas/mental activity',
        'Ch': 'chitta/mind-stuff/memory patterns',
        'I': 'intention/will power',
        'S': 'surrender/letting go',
        'F': 'fear/anxiety level',
        'D': 'dharma/righteous purpose',
        'Sh': 'shakti/energy available',
        'Tr': 'trust/faith in support',
        'O': 'openness/receptive attitude',
        'Co': 'coherence/internal alignment',
        'J': 'joy/happiness level',
    }

    def __init__(self, session_store: SessionStore):
        """
        Initialize context assembler.

        Args:
            session_store: The session store to draw context from
        """
        self.session_store = session_store

    def assemble_context(
        self,
        session_id: str,
        priority_operators: Optional[List[str]] = None
    ) -> Optional[AssembledContext]:
        """
        Assemble complete context from session state.

        Args:
            session_id: Session identifier
            priority_operators: Optional list of operators to prioritize

        Returns:
            AssembledContext if session exists, None otherwise
        """
        session = self.session_store.get_session(session_id)
        if session is None:
            return None

        # Build operator summary
        operator_summary = self._build_operator_summary(session)

        # Build missing summary
        missing_summary = self._build_missing_summary(session)

        # Build historical context
        historical_context = self._build_historical_context(session)

        # Determine priority operators if not provided
        if priority_operators is None:
            priority_operators = self._determine_priority_operators(session)

        # Build full context prompt
        full_context = self._build_full_context_prompt(
            session,
            operator_summary,
            missing_summary,
            historical_context,
            priority_operators
        )

        return AssembledContext(
            session_id=session_id,
            original_query=session.context.original_query,
            operator_summary=operator_summary,
            missing_summary=missing_summary,
            historical_context=historical_context,
            priority_operators=priority_operators,
            full_context_prompt=full_context
        )

    def _build_operator_summary(self, session: SessionState) -> str:
        """Build summary of known operator values."""
        if not session.operators:
            return "No operator values have been established yet."

        lines = ["Known operator values:"]

        # Group by source
        by_source: Dict[OperatorSource, List[str]] = {}
        for op in session.operators.values():
            if op.source not in by_source:
                by_source[op.source] = []
            desc = self.OPERATOR_DESCRIPTIONS.get(op.canonical_name, op.canonical_name)
            by_source[op.source].append(
                f"  - {op.canonical_name} ({desc}): {op.value:.2f} (confidence: {op.confidence:.0%})"
            )

        # User confirmed first
        if OperatorSource.USER_CONFIRMED in by_source:
            lines.append("\nUser confirmed:")
            lines.extend(by_source[OperatorSource.USER_CONFIRMED])

        # LLM inferred
        if OperatorSource.LLM_INFERRED in by_source:
            lines.append("\nInferred from text:")
            lines.extend(by_source[OperatorSource.LLM_INFERRED])

        # Formula derived
        if OperatorSource.FORMULA_DERIVED in by_source:
            lines.append("\nDerived from calculations:")
            lines.extend(by_source[OperatorSource.FORMULA_DERIVED])

        # Historical
        if OperatorSource.HISTORICAL in by_source:
            lines.append("\nFrom previous context:")
            lines.extend(by_source[OperatorSource.HISTORICAL])

        return "\n".join(lines)

    def _build_missing_summary(self, session: SessionState) -> str:
        """Build summary of missing operators."""
        if not session.missing_operators:
            return "All core operators have been established."

        lines = [f"Missing {len(session.missing_operators)} core operators:"]

        for op_name in sorted(session.missing_operators):
            desc = self.OPERATOR_DESCRIPTIONS.get(op_name, op_name)
            lines.append(f"  - {op_name}: {desc}")

        return "\n".join(lines)

    def _build_historical_context(self, session: SessionState) -> str:
        """Build context from historical interactions."""
        lines = []

        if session.context.interaction_count > 1:
            lines.append(f"This is interaction #{session.context.interaction_count} in this session.")

        if session.context.topics_discussed:
            lines.append(f"Topics discussed: {', '.join(session.context.topics_discussed)}")

        if session.answered_questions:
            lines.append(f"\nPrevious questions answered ({len(session.answered_questions)}):")
            for q in session.answered_questions[-3:]:  # Last 3 questions
                lines.append(f"  Q: {q.get('question', 'Unknown')}")
                if 'answer' in q:
                    answer_preview = str(q['answer'])[:50]
                    lines.append(f"  A: {answer_preview}...")

        if session.inference_history:
            last_inference = session.inference_history[-1]
            lines.append(f"\nLast inference: {last_inference.get('operator_count', 0)} operators populated")

        if not lines:
            return "No historical context available."

        return "\n".join(lines)

    def _determine_priority_operators(self, session: SessionState) -> List[str]:
        """
        Determine which operators to prioritize for collection.

        Priority based on:
        1. Operators needed for critical formulas (S-level, transformation potential)
        2. Operators with high variance impact
        3. Operators that unlock dependent calculations
        """
        # Critical operators for core calculations
        critical = {'Psi', 'K', 'M', 'G', 'W', 'A', 'P', 'At', 'R', 'F'}

        # High-impact operators
        high_impact = {'E', 'S', 'Ce', 'Se', 'I', 'V'}

        # Find missing from each category
        missing = session.missing_operators

        priority = []

        # Critical missing first
        for op in critical:
            if op in missing:
                priority.append(op)

        # Then high-impact
        for op in high_impact:
            if op in missing and op not in priority:
                priority.append(op)

        # Fill with remaining missing
        for op in sorted(missing):
            if op not in priority:
                priority.append(op)

        return priority[:10]  # Top 10 priority operators

    def _build_full_context_prompt(
        self,
        session: SessionState,
        operator_summary: str,
        missing_summary: str,
        historical_context: str,
        priority_operators: List[str]
    ) -> str:
        """Build the full context prompt for LLM."""
        coverage = self.session_store.get_operator_coverage(session.session_id)

        prompt = f"""## Session Context

### Original Query
{session.context.original_query}

### Operator Coverage
- Coverage: {coverage['coverage_percent']:.1f}% ({coverage['populated']}/{coverage['total_core']} core operators)
- Average confidence: {coverage['average_confidence']:.0%}

### {operator_summary}

### {missing_summary}

### Priority Operators to Collect
The following operators should be prioritized for data collection:
{self._format_priority_list(priority_operators)}

### {historical_context}

### Instructions
ZERO-FALLBACK MODE: Do not assume or guess values for missing operators.
Only provide values for operators that have clear evidence in the user's text.
Mark any operators without clear evidence as "MISSING".
"""
        return prompt

    def _format_priority_list(self, priority_operators: List[str]) -> str:
        """Format priority operators as numbered list."""
        lines = []
        for i, op in enumerate(priority_operators, 1):
            desc = self.OPERATOR_DESCRIPTIONS.get(op, op)
            lines.append(f"{i}. {op} - {desc}")
        return "\n".join(lines)

    def build_pass1_context(self, session_id: str) -> Optional[str]:
        """
        Build context specifically for Pass 1 (evidence extraction).

        Args:
            session_id: Session identifier

        Returns:
            Context string for Pass 1 LLM prompt
        """
        session = self.session_store.get_session(session_id)
        if session is None:
            return None

        missing = session.missing_operators
        coverage = self.session_store.get_operator_coverage(session_id)

        prompt = f"""## Evidence Extraction Context

### Query to Analyze
{session.context.original_query}

### Current Data State
- Operators populated: {coverage['populated']}/{coverage['total_core']}
- Coverage: {coverage['coverage_percent']:.1f}%

### Operators Needing Evidence
Extract evidence for these {len(missing)} missing operators:

"""
        for op in sorted(missing):
            desc = self.OPERATOR_DESCRIPTIONS.get(op, op)
            prompt += f"- **{op}** ({desc})\n"

        prompt += """
### Instructions
For EACH operator above, search the query for any evidence that could indicate its value.
If no clear evidence exists, mark as "NO_EVIDENCE" - do NOT guess or use defaults.

Return observations in the format:
{
  "observations": [
    {
      "operator": "OPERATOR_NAME",
      "observed_value": 0.0-1.0 or null,
      "confidence": 0.0-1.0,
      "evidence": "Quote or describe the evidence",
      "reasoning": "Why this value"
    }
  ]
}
"""
        return prompt

    def build_pass2_context(
        self,
        session_id: str,
        inference_results: Dict[str, Any]
    ) -> Optional[str]:
        """
        Build context for Pass 2 (articulation).

        Args:
            session_id: Session identifier
            inference_results: Results from inference engine

        Returns:
            Context string for Pass 2 LLM prompt
        """
        session = self.session_store.get_session(session_id)
        if session is None:
            return None

        # Extract key results
        s_level = inference_results.get('s_level', {}).get('value')
        consciousness = inference_results.get('consciousness', {})
        bottlenecks = inference_results.get('bottlenecks', [])
        leverage = inference_results.get('leverage_points', [])

        prompt = f"""## Articulation Context

### Original Query
{session.context.original_query}

### Calculated Results

"""
        if s_level is not None:
            prompt += f"**S-Level**: {s_level:.1f}\n"
        else:
            prompt += "**S-Level**: Could not calculate (missing operators)\n"

        if consciousness:
            prompt += f"\n**Consciousness State**:\n"
            for key, value in consciousness.items():
                if value is not None:
                    prompt += f"- {key}: {value}\n"

        if bottlenecks:
            prompt += f"\n**Bottlenecks Identified** ({len(bottlenecks)}):\n"
            for b in bottlenecks[:5]:
                prompt += f"- {b.get('description', b)}\n"

        if leverage:
            prompt += f"\n**Leverage Points** ({len(leverage)}):\n"
            for l in leverage[:5]:
                prompt += f"- {l.get('description', l)}\n"

        # Data quality note
        coverage = self.session_store.get_operator_coverage(session_id)
        prompt += f"""
### Data Quality
- Operator coverage: {coverage['coverage_percent']:.1f}%
- Missing: {coverage['missing']} operators
- Average confidence: {coverage['average_confidence']:.0%}

### Instructions
Provide a response that:
1. Addresses the user's original query
2. Explains the consciousness assessment results
3. Notes any limitations due to missing data
4. Suggests how missing operators could be collected if needed
"""
        return prompt


# Factory function for easy instantiation
def create_context_assembler(session_store: Optional[SessionStore] = None) -> ContextAssembler:
    """
    Create a context assembler with the given or default session store.

    Args:
        session_store: Optional session store to use

    Returns:
        Configured ContextAssembler instance
    """
    from session_store import session_store as default_store
    return ContextAssembler(session_store or default_store)
