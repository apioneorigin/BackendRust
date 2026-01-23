"""
Evidence Extraction Prompt Builder for Pass 1 LLM Call

Constructs prompts for the evidence extraction phase that:
- Incorporate session context (known operators, missing operators)
- Use priority analysis to focus extraction on high-impact operators
- Support both first-time and follow-up interactions
- Generate null-aware extraction that doesn't assume defaults

ZERO-FALLBACK MODE: Only extract operators that have clear evidence.
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass

from session_store import SessionState, OperatorSource
from priority_detector import PriorityAnalysis, PriorityLevel
from context_assembler import AssembledContext


# Load OOF Framework (same as used in main.py)
OOF_FRAMEWORK = ""
try:
    with open("OOF.txt", "r") as f:
        OOF_FRAMEWORK = f.read()
except FileNotFoundError:
    # Will be loaded from main.py context
    pass


@dataclass
class EvidencePromptConfig:
    """Configuration for evidence extraction prompt"""
    include_session_context: bool = True
    include_priority_guidance: bool = True
    strict_evidence_only: bool = True  # Don't infer without evidence
    max_operators_to_focus: int = 10   # Focus on top N priority operators


class EvidencePromptBuilder:
    """
    Builds prompts for Pass 1 evidence extraction.

    Integrates with session state to avoid re-asking for known operators
    and focuses extraction on missing high-priority operators.
    """

    # Core operators list with their canonical names and descriptions
    CORE_OPERATORS = {
        'Psi': ('Ψ', 'Consciousness - overall consciousness quality'),
        'K': ('K', 'Karma - past action patterns affecting present'),
        'M': ('M', 'Maya - illusion/veiling of reality'),
        'G': ('G', 'Grace - divine support and flow'),
        'W': ('W', 'Witness - capacity to observe without identification'),
        'A': ('A', 'Awareness - general mindfulness level'),
        'P': ('P', 'Presence - being in the now-moment'),
        'E': ('E', 'Equanimity - balance amidst change'),
        'V': ('V', 'Void - comfort with emptiness/uncertainty'),
        'L': ('L', 'Love - unconditional love capacity'),
        'R': ('R', 'Resistance - opposition to what is'),
        'At': ('At', 'Attachment - clinging to outcomes'),
        'Av': ('Av', 'Aversion - pushing away unpleasant'),
        'Se': ('Se', 'Service - orientation toward helping others'),
        'Ce': ('Ce', 'Cleaning/Celebration - inner purification'),
        'Su': ('Su', 'Suffering - current suffering level'),
        'As': ('As', 'Aspiration - drive toward growth'),
        'Fe': ('Fe', 'Faith - trust in the path'),
        'De': ('De', 'Devotion - heart connection to practice'),
        'Re': ('Re', 'Receptivity - openness to receiving'),
        'Hf': ('Hf', 'Habit Force - strength of conditioning'),
        'Sa': ('Sa', 'Samskara - deep impressions'),
        'Bu': ('Bu', 'Buddhi - discriminative intelligence'),
        'Ma': ('Ma', 'Manas - ordinary mind state'),
        'Ch': ('Ch', 'Chitta - memory-mind/subconscious'),
    }

    def __init__(self, oof_framework: Optional[str] = None):
        """Initialize with OOF framework text."""
        self.oof_framework = oof_framework or OOF_FRAMEWORK

    def build_evidence_prompt(
        self,
        user_query: str,
        session_state: Optional[SessionState] = None,
        priority_analysis: Optional[PriorityAnalysis] = None,
        config: Optional[EvidencePromptConfig] = None
    ) -> str:
        """
        Build the complete evidence extraction prompt.

        Args:
            user_query: The user's input query
            session_state: Current session state with known operators
            priority_analysis: Analysis of which operators to prioritize
            config: Prompt configuration options

        Returns:
            Complete prompt string for LLM
        """
        config = config or EvidencePromptConfig()

        sections = [
            self._build_header(),
            self._build_framework_section(),
        ]

        # Add session context if available
        if config.include_session_context and session_state:
            sections.append(self._build_session_context_section(session_state))

        # Add priority guidance if available
        if config.include_priority_guidance and priority_analysis:
            sections.append(self._build_priority_section(priority_analysis, config))

        sections.extend([
            self._build_extraction_rules(config),
            self._build_operator_reference(session_state),
            self._build_output_format(),
        ])

        return '\n\n'.join(sections)

    def _build_header(self) -> str:
        """Build the prompt header."""
        return """# EVIDENCE EXTRACTION - CONSCIOUSNESS ANALYSIS

You are the Reality Transformer evidence extraction engine.
Your task is to analyze the user's query and extract consciousness operator values based on CLEAR EVIDENCE ONLY.

CRITICAL PRINCIPLES:
1. ZERO-FALLBACK: Do NOT guess or assume default values. Only extract operators you have clear evidence for.
2. If you cannot determine an operator's value with reasonable confidence, mark it as "unable_to_determine"
3. Use web search to gather real data to support your analysis
4. Higher confidence requires stronger evidence"""

    def _build_framework_section(self) -> str:
        """Build framework reference section."""
        return f"""## OOF FRAMEWORK REFERENCE

=== OOF FRAMEWORK ===
{self.oof_framework}
=== END OOF FRAMEWORK ===

Use this framework to understand operator meanings and value ranges."""

    def _build_session_context_section(self, session: SessionState) -> str:
        """Build section showing what we already know from session."""
        if not session or not session.operators:
            return """## SESSION CONTEXT

This is a new session. No prior operator values are known.
You must extract all operators from the current query."""

        known_ops = []
        for op_name, op_value in session.operators.items():
            source = op_value.source.value
            conf = op_value.confidence
            known_ops.append(f"- {op_name}: {op_value.value:.2f} (source: {source}, confidence: {conf:.2f})")

        known_str = '\n'.join(known_ops) if known_ops else "- None"

        missing_str = ', '.join(session.missing_operators) if session.missing_operators else "None"

        return f"""## SESSION CONTEXT

**Already Known Operators:**
{known_str}

**Missing Operators:** {missing_str}

IMPORTANT:
- You do NOT need to re-extract operators we already have (unless the query provides clearly different information)
- Focus on extracting the MISSING operators from the current query
- If the user's situation has changed, you may update known operators with new values"""

    def _build_priority_section(
        self,
        analysis: PriorityAnalysis,
        config: EvidencePromptConfig
    ) -> str:
        """Build section highlighting priority operators to extract."""
        if not analysis or not analysis.prioritized_operators:
            return ""

        # Get top priority operators
        critical = [p for p in analysis.prioritized_operators if p.priority_level == PriorityLevel.CRITICAL]
        high = [p for p in analysis.prioritized_operators if p.priority_level == PriorityLevel.HIGH]

        sections = ["## PRIORITY EXTRACTION GUIDANCE\n"]
        sections.append("Focus your evidence gathering on these HIGH IMPACT operators:\n")

        if critical:
            sections.append("**CRITICAL PRIORITY (required for core calculations):**")
            for p in critical[:5]:
                sections.append(f"- {p.operator_name}: {p.reason}")

        if high:
            sections.append("\n**HIGH PRIORITY:**")
            for p in high[:5]:
                sections.append(f"- {p.operator_name}: {p.reason}")

        sections.append(f"\nThese operators unlock the most calculations. Prioritize finding evidence for them.")

        return '\n'.join(sections)

    def _build_extraction_rules(self, config: EvidencePromptConfig) -> str:
        """Build evidence extraction rules."""
        strict_note = ""
        if config.strict_evidence_only:
            strict_note = """
STRICT EVIDENCE MODE:
- Every value MUST be backed by specific evidence from query or web research
- If evidence is ambiguous, use lower confidence (0.3-0.5)
- If no evidence exists, mark as "unable_to_determine" - do NOT guess
- It's better to have fewer confident values than many uncertain ones"""

        return f"""## EXTRACTION RULES

1. IDENTITY ASSUMPTION:
   - Assume the MOST FAMOUS/LIKELY interpretation of any name
   - "Nirma" → Nirma Ltd (Indian FMCG company)
   - "Apple" → Apple Inc (technology company)
   - DO NOT ask for clarification - assume and proceed

2. WEB SEARCH REQUIREMENTS:
   - Use web_search EXTENSIVELY to research the entity
   - Search for: current position, challenges, recent news, market data
   - Use search results to inform operator calculations

3. VALUE ASSIGNMENT:
   - All values are 0.0 to 1.0
   - Include confidence level (0.0-1.0) for each operator
   - Provide reasoning that ties to specific evidence
{strict_note}

4. HANDLING UNCERTAINTY:
   - Unknown/uncertain → mark as "unable_to_determine"
   - Low evidence → confidence 0.3-0.4
   - Moderate evidence → confidence 0.5-0.7
   - Strong evidence → confidence 0.8-1.0"""

    def _build_operator_reference(self, session: Optional[SessionState] = None) -> str:
        """Build operator reference list, marking known ones."""
        lines = ["## OPERATOR REFERENCE\n"]
        lines.append("The 25 core operators (extract those with clear evidence):\n")

        known_ops = set()
        if session and session.operators:
            known_ops = set(session.operators.keys())

        for canonical, (symbol, description) in self.CORE_OPERATORS.items():
            status = " [KNOWN]" if canonical in known_ops else ""
            lines.append(f"- {symbol} ({canonical}): {description}{status}")

        return '\n'.join(lines)

    def _build_output_format(self) -> str:
        """Build output format specification."""
        return """## OUTPUT FORMAT

Return valid JSON with this structure:

{
  "user_identity": "detailed description based on query + research",
  "goal": "their goal informed by research context",
  "s_level": "S1-S8 estimated consciousness level",
  "web_research_summary": "key insights from web research",
  "search_queries_used": ["query1", "query2", ...],
  "key_facts": [
    {"fact": "specific fact from research", "source": "source name", "relevance": "how it affects operators"}
  ],
  "observations": [
    {"var": "W", "value": 0.65, "confidence": 0.8, "reasoning": "specific evidence..."},
    {"var": "At", "value": 0.55, "confidence": 0.6, "reasoning": "specific evidence..."},
    {"var": "UNABLE", "value": null, "confidence": 0, "reasoning": "No evidence for operator X"}
  ],
  "unable_to_determine": ["list", "of", "operator", "names", "without", "evidence"],
  "operators_updated": ["list of operators that changed from session values"],
  "targets": ["Transformation targets from analysis"],
  "relevant_oof_components": ["OOF components relevant to situation"]
}

CRITICAL:
- Include ONLY operators you have evidence for in observations
- List operators without evidence in "unable_to_determine"
- Do NOT include default values for missing operators"""

    def build_follow_up_prompt(
        self,
        user_response: str,
        original_query: str,
        session_state: SessionState,
        question_context: Dict[str, Any]
    ) -> str:
        """
        Build prompt for follow-up questions (when user answered questions).

        Args:
            user_response: User's answer to our questions
            original_query: The original user query
            session_state: Current session state
            question_context: Context about what questions were asked

        Returns:
            Prompt for extracting values from user's answers
        """
        return f"""# FOLLOW-UP EVIDENCE EXTRACTION

The user was asked clarifying questions to gather missing operator values.
Your task is to extract operator values from their response.

## ORIGINAL CONTEXT
Original query: "{original_query}"

## QUESTIONS ASKED
{self._format_questions(question_context)}

## USER'S RESPONSE
"{user_response}"

## EXTRACTION TASK

Parse the user's response and extract operator values.
Map their answers to the appropriate operators and values.

For each answer:
1. Identify which operator(s) it relates to
2. Determine the appropriate value (0.0-1.0)
3. Assign confidence based on clarity of response

Return JSON:
{{
  "extracted_operators": [
    {{"var": "W", "value": 0.7, "confidence": 0.85, "reasoning": "User clearly indicated..."}},
    ...
  ],
  "clarifications_needed": ["list any remaining unclear operators"],
  "user_insights": "any additional insights from their response"
}}"""

    def _format_questions(self, question_context: Dict[str, Any]) -> str:
        """Format questions that were asked."""
        questions = question_context.get('questions', [])
        if not questions:
            return "No specific questions were asked."

        lines = []
        for i, q in enumerate(questions, 1):
            lines.append(f"{i}. {q.get('question_text', 'Unknown question')}")
            lines.append(f"   Targeting operators: {', '.join(q.get('target_operators', []))}")

        return '\n'.join(lines)


def create_evidence_prompt_builder(oof_framework: Optional[str] = None) -> EvidencePromptBuilder:
    """Create an evidence prompt builder instance."""
    return EvidencePromptBuilder(oof_framework)
