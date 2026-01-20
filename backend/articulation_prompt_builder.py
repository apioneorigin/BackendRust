"""
Articulation Prompt Builder for Articulation Bridge
Constructs the final LLM Call 2 prompt with organized values
"""

from typing import List, Optional
from consciousness_state import (
    ArticulationContext, ConsciousnessState, Bottleneck, LeveragePoint,
    UserContext, WebResearch, ArticulationInstructions
)


class ArticulationPromptBuilder:
    """
    Build complete prompt for LLM Call 2.
    Input: Organized consciousness state + context from Call 1
    Output: Complete prompt string for articulation
    """

    def build_prompt(self, context: ArticulationContext) -> str:
        """
        Build the complete articulation prompt from organized values.
        """
        sections = [
            self._build_header(),
            self._build_framework_section(),
            self._build_context_section(context.user_context, context.web_research),
            self._build_consciousness_state_section(context.consciousness_state),
            self._build_bottleneck_section(context.consciousness_state.bottlenecks),
            self._build_leverage_section(context.consciousness_state.leverage_points),
            self._build_generation_instructions(context.instructions),
            self._build_user_query(context.user_context)
        ]

        return '\n\n---\n\n'.join(sections)

    def _build_header(self) -> str:
        """Build the prompt header"""
        return """# REALITY TRANSFORMER: CONSCIOUSNESS ARTICULATION

You are receiving a complete consciousness analysis based on the One Origin Framework (OOF).

Your task is to articulate these insights in natural language that the user can understand and act upon.

CRITICAL: You must CONCEAL framework terminology. Never say "Maya operator" or "S-level" - translate everything into natural, domain-appropriate language."""

    def _build_framework_section(self) -> str:
        """Build framework reference section"""
        return """## FRAMEWORK REFERENCE

The OOF.txt framework document is available in your context. Use it for:
- Operator definitions and interpretation ranges
- Transformation matrix meanings
- S-level characteristics
- Consciousness physics principles

Reference the framework internally but express insights naturally - as if speaking to a trusted friend or client."""

    def _build_context_section(
        self,
        user_context: UserContext,
        web_research: WebResearch
    ) -> str:
        """Build user context and web research section"""
        constraints_str = '\n'.join(f"- {c}" for c in user_context.constraints) if user_context.constraints else "- None specified"

        searches_str = ""
        if web_research.searches_performed:
            searches_str = '\n'.join(
                f"- \"{s.get('query', 'N/A')}\": {s.get('summary', 'N/A')}"
                for s in web_research.searches_performed
            )
        else:
            searches_str = "- No web searches performed"

        facts_str = '\n'.join(f"- {f}" for f in web_research.key_facts) if web_research.key_facts else "- No additional facts"

        competitive_str = ""
        if web_research.competitive_context:
            competitive_str = f"\n**Competitive Context:**\n{web_research.competitive_context}"

        return f"""## USER CONTEXT

**Identity:** {user_context.identity or "Not specified"}

**Domain:** {user_context.domain or "General"}

**Current Situation:**
{user_context.current_situation or "Not described"}

**Goal:**
{user_context.goal or "Not specified"}

**Constraints:**
{constraints_str}

## WEB RESEARCH FINDINGS

**Searches Performed:**
{searches_str}

**Key Facts:**
{facts_str}
{competitive_str}"""

    def _build_consciousness_state_section(self, state: ConsciousnessState) -> str:
        """Build the consciousness state section with organized values"""
        ops = state.tier1.core_operators
        drives = state.tier1.drives
        s_level = state.tier1.s_level

        # Tier 2 values
        gunas = state.tier2.gunas
        five_acts = state.tier2.five_acts
        chakras = state.tier2.chakras
        drives_int = state.tier2.drives_internalization

        # Tier 3 values
        matrices = state.tier3.transformation_matrices
        death = state.tier3.death_architecture
        coherence = state.tier3.coherence_metrics

        # Tier 4 values
        breakthrough = state.tier4.breakthrough_dynamics
        pipeline = state.tier4.pipeline_flow
        grace_mech = state.tier4.grace_mechanics
        pomdp = state.tier4.pomdp_gaps

        # Tier 5 values
        timeline = state.tier5.timeline_predictions
        transform = state.tier5.transformation_vectors

        # Get dominant act properly
        act_values = {
            'srishti_creation': five_acts.srishti_creation,
            'sthiti_maintenance': five_acts.sthiti_maintenance,
            'samhara_dissolution': five_acts.samhara_dissolution,
            'tirodhana_concealment': five_acts.tirodhana_concealment,
            'anugraha_grace': five_acts.anugraha_grace
        }
        dominant_act_value = act_values.get(five_acts.dominant, 0.5)

        # Get dominant guna value
        guna_values = {'sattva': gunas.sattva, 'rajas': gunas.rajas, 'tamas': gunas.tamas}
        dominant_guna_value = guna_values.get(gunas.dominant, 0.33)

        return f"""## CALCULATED CONSCIOUSNESS STATE

### CORE CONFIGURATION

**S-Level:** {s_level.current:.1f} ({s_level.label})
- Evolution rate: {s_level.transition_rate * 100:.1f}% per month

**Primary Operating Mode:**
- Dominant Act: {five_acts.dominant.replace('_', ' ').title()} ({dominant_act_value * 100:.0f}%)
- Dominant Guna: {gunas.dominant.title()} ({dominant_guna_value * 100:.0f}%)
- Temporal Focus: {ops.T_time_past * 100:.0f}% past, {ops.T_time_present * 100:.0f}% present, {ops.T_time_future * 100:.0f}% future

**Key Operators:**
- Presence (now-moment): {ops.P_presence * 100:.0f}%
- Awareness: {ops.A_aware * 100:.0f}%
- Maya (illusion): {ops.M_maya * 100:.0f}%
- Attachment: {ops.At_attachment * 100:.0f}%
- Grace flow: {ops.G_grace * 100:.0f}%
- Witness: {ops.W_witness * 100:.0f}%
- Surrender: {ops.S_surrender * 100:.0f}%
- Coherence: {ops.Co_coherence * 100:.0f}%
- Resistance: {ops.R_resistance * 100:.0f}%
- Fear: {ops.F_fear * 100:.0f}%

### TRANSFORMATION POSITION

**Matrix Positions:**
- Truth: {matrices.truth_position} ({matrices.truth_score * 100:.0f}%)
- Love: {matrices.love_position} ({matrices.love_score * 100:.0f}%)
- Power: {matrices.power_position} ({matrices.power_score * 100:.0f}%)
- Freedom: {matrices.freedom_position} ({matrices.freedom_score * 100:.0f}%)
- Creation: {matrices.creation_position} ({matrices.creation_score * 100:.0f}%)
- Time: {matrices.time_position} ({matrices.time_score * 100:.0f}%)
- Death: {matrices.death_position} ({matrices.death_score * 100:.0f}%)

**Active Death Processes:**
{f"- {death.active_process} (depth: {death.depth * 100:.0f}%)" if death.active_process else "- None currently active"}

### ENERGY DISTRIBUTION

**Chakra Activation:**
- Root (survival): {chakras.muladhara * 100:.0f}%
- Sacral (creativity): {chakras.svadhisthana * 100:.0f}%
- Solar Plexus (power): {chakras.manipura * 100:.0f}%
- Heart (love): {chakras.anahata * 100:.0f}%
- Throat (expression): {chakras.vishuddha * 100:.0f}%
- Third Eye (intuition): {chakras.ajna * 100:.0f}%
- Crown (connection): {chakras.sahasrara * 100:.0f}%

**Drive Fulfillment:**
- Love: {drives_int.love_internal_pct:.0f}% internal, {drives_int.love_external_pct:.0f}% seeking externally
- Peace: {drives_int.peace_internal_pct:.0f}% internal, {drives_int.peace_external_pct:.0f}% seeking externally
- Freedom: {drives_int.freedom_internal_pct:.0f}% internal, {drives_int.freedom_external_pct:.0f}% seeking externally

### TRANSFORMATION READINESS

**Breakthrough Dynamics:**
- Breakthrough probability: {breakthrough.probability * 100:.0f}%
- Distance to tipping point: {breakthrough.tipping_point_distance * 100:.0f}%
- Quantum jump possibility: {breakthrough.quantum_jump_prob * 100:.0f}%
{f"- Operators at breakthrough threshold: {', '.join(breakthrough.operators_at_threshold)}" if breakthrough.operators_at_threshold else ""}

**Timeline Predictions:**
- To stated goal: {timeline.to_goal}
- To next S-level: {timeline.to_next_s_level}
- Evolution rate: {timeline.evolution_rate * 100:.1f}% per month

**Manifestation Capacity:**
- Pipeline flow rate: {pipeline.flow_rate * 100:.0f}%
- Typical manifestation time: {pipeline.manifestation_time}

**Grace Mechanics:**
- Availability: {grace_mech.availability * 100:.0f}%
- Effectiveness: {grace_mech.effectiveness * 100:.0f}%
- Multiplication factor: {grace_mech.multiplication_factor:.2f}x

### COHERENCE & GAPS

**Coherence Metrics:**
- Overall coherence: {coherence.overall * 100:.0f}%
- Fundamental: {coherence.fundamental * 100:.0f}%
- Specification: {coherence.specification * 100:.0f}%

**POMDP Gaps (Reality Perception):**
- Reality gap (what's real vs what you believe): {pomdp.reality_gap * 100:.0f}%
- Observation gap (what's real vs what you see): {pomdp.observation_gap * 100:.0f}%
- Belief gap (what you believe vs what you see): {pomdp.belief_gap * 100:.0f}%
- Overall severity: {pomdp.severity * 100:.0f}%

### TRANSFORMATION VECTORS

- Current state: {transform.current_state_summary or "Not analyzed"}
- Target state: {transform.target_state_summary or "Not specified"}
- Core shift required: {transform.core_shift_required or "Not determined"}
- Primary obstacle: {transform.primary_obstacle or "Not identified"}
- Primary enabler: {transform.primary_enabler or "Not identified"}
- Leverage point: {transform.leverage_point or "See leverage section"}"""

    def _build_bottleneck_section(self, bottlenecks: List[Bottleneck]) -> str:
        """Build the bottleneck analysis section"""
        if not bottlenecks:
            return """## BOTTLENECK ANALYSIS

No major bottlenecks detected. Transformation pathway is relatively clear."""

        high_impact = [b for b in bottlenecks if b.impact == 'high']
        medium_impact = [b for b in bottlenecks if b.impact == 'medium']

        sections = ["## BOTTLENECK ANALYSIS\n"]

        if high_impact:
            sections.append("**HIGH IMPACT BOTTLENECKS:**")
            for b in high_impact[:3]:
                sections.append(f"- [{b.category.upper()}] {b.description}")

        if medium_impact:
            sections.append("\n**MEDIUM IMPACT BOTTLENECKS:**")
            for b in medium_impact[:3]:
                sections.append(f"- [{b.category}] {b.description}")

        return '\n'.join(sections)

    def _build_leverage_section(self, leverage_points: List[LeveragePoint]) -> str:
        """Build the leverage opportunities section"""
        if not leverage_points:
            return """## LEVERAGE OPPORTUNITIES

No high-multiplier opportunities currently active. Focus on clearing bottlenecks to activate leverage."""

        sections = ["## LEVERAGE OPPORTUNITIES\n"]

        for i, lp in enumerate(leverage_points[:3], 1):
            sections.append(f"""**{i}. {lp.description}** ({lp.multiplier}x multiplier)
   Activation: {lp.activation_requirement}
   Operators: {', '.join(lp.operators_involved)}""")

        return '\n\n'.join(sections)

    def _build_generation_instructions(self, instructions: ArticulationInstructions) -> str:
        """Build generation instructions for the LLM"""
        concealment_note = ""
        if instructions.framework_concealment:
            concealment_note = """
- **Framework Concealment:** Do NOT mention operators by name, S-levels, or framework terminology. Translate everything into natural domain-appropriate language.
  - Instead of "Maya operator at 70%", say "seeing success as external rather than internal"
  - Instead of "S3 consciousness", say "achievement-focused mindset"
  - Instead of "Grace flow low", say "not receiving the support that's available"
"""
        else:
            concealment_note = "- Framework terminology is allowed if it helps clarity."

        domain_note = ""
        if instructions.domain_language:
            domain_note = """
- **Domain Language:** Use vocabulary and framing natural to their industry/domain. Speak their language, not consciousness physics language.
  - For business: Use terms like ROI, market position, competitive advantage
  - For personal: Use terms like fulfillment, relationships, growth
  - For spiritual: Use accessible terms, not jargon
"""
        else:
            domain_note = "- General language is fine."

        priorities_str = ""
        if instructions.insight_priorities:
            priorities_str = "\n**Priority Insights to Emphasize:**\n" + '\n'.join(
                f"- {p.replace('_', ' ').title()}"
                for p in instructions.insight_priorities
            )

        return f"""## ARTICULATION INSTRUCTIONS

Generate a response that accomplishes the following:

### 1. CURRENT REALITY ANALYSIS
Express where the user actually is right now (not where they think they are).
Ground this in both the web research data and consciousness analysis.
Point out any gaps between believed state and actual state (POMDP gaps).

### 2. STRUCTURAL GAP IDENTIFICATION
Explain what's between their current position and stated goal.
This is NOT superficial obstacles - it's the consciousness structure creating the gap.
Reference the matrix positions and transformation requirements.

### 3. ROOT CAUSE EXPLANATION
Identify which consciousness patterns are creating the current situation.
Explain HOW these patterns interact to produce observable results.
Make the invisible visible - show them what they can't see from their current position.

### 4. TRANSFORMATION PATHWAY
Describe what actually needs to shift (not just what actions to take).
Reference the transformation vector, leverage points, and grace mechanics.
Be specific about what internal changes enable external results.

### 5. PRACTICAL LEVERAGE
Provide concrete next actions aligned with their consciousness state.
These should activate the identified leverage points.
Respect their current capacity - don't suggest actions requiring development they don't have.

### STYLE REQUIREMENTS
{concealment_note}
{domain_note}
- **Natural Flow:** Write as if you're a wise advisor who sees patterns they cannot see, not as a calculation system reporting numbers.

- **Insight Priority:** Lead with the most impactful insights. Don't try to communicate everything - focus on what matters most for their transformation.

- **Grounded in Data:** Every major claim should tie back to either web research findings or calculated consciousness values. But express these naturally, not as citations.
{priorities_str}"""

    def _build_user_query(self, user_context: UserContext) -> str:
        """Build the user query section"""
        return f"""## USER'S ORIGINAL QUERY

"{user_context.goal or user_context.current_situation or 'Transform my situation'}"

---

Now generate your response, following all articulation instructions above.
Express insights with wisdom and warmth. Speak truth without judgment.
Guide without controlling. Illuminate without overwhelming."""


def build_articulation_context(
    user_identity: str,
    domain: str,
    goal: str,
    current_situation: str,
    consciousness_state: ConsciousnessState,
    web_research_summary: str = "",
    key_facts: Optional[List[str]] = None,
    framework_concealment: bool = True,
    domain_language: bool = True
) -> ArticulationContext:
    """
    Helper function to build ArticulationContext from components.
    """
    return ArticulationContext(
        user_context=UserContext(
            identity=user_identity,
            domain=domain,
            current_situation=current_situation,
            goal=goal,
            constraints=[]
        ),
        web_research=WebResearch(
            searches_performed=[{"query": "context research", "summary": web_research_summary}] if web_research_summary else [],
            key_facts=key_facts or [],
            competitive_context=None,
            market_data=None
        ),
        consciousness_state=consciousness_state,
        instructions=ArticulationInstructions(
            articulation_style="natural",
            framework_concealment=framework_concealment,
            domain_language=domain_language,
            insight_priorities=[
                "structural_gaps",
                "bottlenecks",
                "leverage_points",
                "transformation_pathway"
            ]
        )
    )
