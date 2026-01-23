"""
Articulation Prompt Builder for Articulation Bridge
Constructs the final LLM Call 2 prompt with organized values

ZERO-FALLBACK MODE: Properly handles null/missing operator values.
Shows "Not available" for blocked calculations instead of assuming defaults.
"""

from typing import List, Optional, Any
from consciousness_state import (
    ArticulationContext, ConsciousnessState, Bottleneck, LeveragePoint,
    UserContext, WebResearch, ArticulationInstructions, InferenceMetadataState,
    SearchGuidance, EvidenceSearchQuery, ConsciousnessRealityMapping
)


def _fmt(value: Optional[float], as_percent: bool = True, decimals: int = 0) -> str:
    """Format a nullable float value for display."""
    if value is None:
        return "N/A"
    if as_percent:
        return f"{value * 100:.{decimals}f}%"
    return f"{value:.{decimals}f}"


def _fmt_score(value: Optional[float]) -> str:
    """Format a nullable score/level value."""
    if value is None:
        return "Not calculated"
    return f"{value:.1f}"


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
            self._build_search_guidance_section(context.search_guidance),
            self._build_generation_instructions(context.instructions),
            self._build_user_query(context.user_context)
        ]

        return '\n\n---\n\n'.join(sections)

    def _build_search_guidance_section(self, search_guidance: SearchGuidance) -> str:
        """Build the search guidance section for evidence grounding in Call 2"""
        if not search_guidance or not search_guidance.high_priority_values:
            return ""

        sections = ["## SEARCH GUIDANCE FOR EVIDENCE GROUNDING\n"]

        # Query pattern
        if search_guidance.query_pattern:
            sections.append(f"**Query Pattern Detected:** {search_guidance.query_pattern.title()}\n")

        # High priority values
        if search_guidance.high_priority_values:
            sections.append("**High-Priority Values to Ground with Evidence:**")
            for i, value in enumerate(search_guidance.high_priority_values[:8], 1):
                sections.append(f"  {i}. {value}")
            sections.append("")

        # Evidence search queries
        if search_guidance.evidence_search_queries:
            sections.append("**Recommended Evidence Searches:**")
            for esq in search_guidance.evidence_search_queries[:5]:
                sections.append(f"  - For '{esq.target_value}': Search \"{esq.search_query}\" (proof type: {esq.proof_type})")
            sections.append("")

        # Consciousness-to-reality mappings
        if search_guidance.consciousness_to_reality_mappings:
            sections.append("**Consciousness → Reality Mappings (use these to find proof):**")
            for crm in search_guidance.consciousness_to_reality_mappings[:5]:
                sections.append(f"  - {crm.consciousness_value}")
                sections.append(f"    → Observable: {crm.observable_reality}")
                sections.append(f"    → Search for: {crm.proof_search}")
            sections.append("")

        sections.append("""**Evidence Integration Instructions:**
When web search is enabled, use these search queries to find CITED PROOF for the calculated consciousness values.
Each major insight should connect: Consciousness Pattern → Observable Reality → Cited Evidence.""")

        return '\n'.join(sections)

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

Reference the framework internally but express insights naturally - as if speaking to a trusted friend or client.

## VALUE SELECTION PROTOCOL (CRITICAL)

You are receiving ALL calculated consciousness values (~1,500-2,500 values).
Your task is to SELECT which values to articulate based on context.

### SELECTION CRITERIA:

**1. QUERY RELEVANCE (Priority 1)**
- What values DIRECTLY answer the user's question?
- If user asks "Why can't we innovate?" → Focus on: At_attachment, Fe_fear, Re_resistance, M_maya, breakthrough_probability
- If user asks "Show transformation path" → Focus on: S_level, matrices, death_architecture, grace_karma_ratio
- IGNORE values unrelated to their specific query

**2. USER-REQUESTED TARGETS (Priority 2)**
- LLM Call 1 identified targets based on query analysis
- These are HIGH CONFIDENCE relevant values
- Always include these in your articulation

**3. SEARCH GUIDANCE HIGH-PRIORITY (Priority 3)**
- LLM Call 1 flagged values for evidence-grounding
- These need web search validation
- Include if relevant to query

**4. EXTREME VALUES (Priority 4)**
- Values >0.7 or <0.3 indicate strong manifestation in reality
- High probability of having searchable evidence
- Include if relevant to query AND evidence-groundable

**5. CAUSAL CHAIN COMPLETENESS (Priority 5)**
- If articulating bottleneck X, include ALL values in its causal chain
- Example: High At_attachment → include Fe_fear (cause), Re_resistance (effect), G_grace (blocked consequence)
- Don't leave causal gaps - show full consciousness → reality chain

**6. TRANSFORMATION CONTEXT (Priority 6)**
- If discussing transformation, include: current S_level, target matrix positions, death_architecture_active, grace_availability
- Full transformation story needs complete context

### WHAT TO IGNORE:

❌ Values with no query relevance
❌ Redundant values (if 3 values say the same thing, pick the clearest)
❌ Values you cannot ground in searchable evidence (unless theoretical explanation requested)
❌ Values close to neutral (0.4-0.6) with no causal significance
❌ Intermediate calculation values (focus on endpoints)

### ARTICULATION EFFICIENCY:

- Articulate 20-50 key values (not all 2,500)
- But USE the full value set to understand complete picture
- Synthesize patterns across all values
- Reference supporting values in causal chains without listing them

### EXAMPLE:

**Received:** 2,347 calculated values
**User query:** "Why are we stuck in reactive mode?"

**Selection process:**
1. Query relevance: victim_power_matrix (0.23), resistance (0.78), fear (0.82), attachment (0.76), habit_force (0.81)
2. Causal chain: fear → resistance → habit_force → blocks grace (0.21) → prevents flow
3. Evidence-grounding: Search for "company reactive decisions", "firefighting mode", "strategic vs tactical"
4. Transformation path: Need death_d3_identity (social identity death), power_matrix shift

**Articulate:** ~15 values that tell the complete story
**Ignore:** Remaining ~2,330 values not relevant to this query

### PRINCIPLE:

You have access to EVERYTHING. Use your intelligence and context to decide what matters for THIS query.
Don't list all values - synthesize the relevant ones into breakthrough insights."""

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

    def _build_context_guidance(self, state: ConsciousnessState) -> str:
        """Build context guidance for value selection from Call 1 context."""
        sections = []

        # Extract query pattern if available
        if hasattr(state, 'query_pattern') and state.query_pattern:
            sections.append(f"**QUERY PATTERN DETECTED (from Call 1):** {state.query_pattern.title()}")
            sections.append("Focus on values relevant to this pattern type.\n")

        # Extract targets if available
        if hasattr(state, 'targets') and state.targets:
            targets_list = ', '.join(state.targets[:20])
            sections.append("**USER-REQUESTED TARGETS (from Call 1 query analysis):**")
            sections.append(targets_list)
            if len(state.targets) > 20:
                sections.append(f"... and {len(state.targets) - 20} more")
            sections.append("\nThese values were identified as directly relevant to the user's query.")
            sections.append("PRIORITY: Include these in your articulation.\n")

        # Extract search guidance high-priority if available
        if hasattr(state, 'search_guidance') and state.search_guidance:
            high_priority = getattr(state.search_guidance, 'high_priority_values', [])
            if high_priority:
                priority_list = ', '.join(high_priority[:20])
                sections.append("**HIGH-PRIORITY FOR EVIDENCE-GROUNDING (from Call 1):**")
                sections.append(priority_list)
                if len(high_priority) > 20:
                    sections.append(f"... and {len(high_priority) - 20} more")
                sections.append("\nThese values should be validated against observable reality via web search.\n")

        if not sections:
            return ""

        return """### CONTEXT GUIDANCE FOR VALUE SELECTION

""" + '\n'.join(sections) + """
**INSTRUCTION:** Use this context to SELECT which of the ~2,000+ calculated values
to articulate. Don't list all values - synthesize the relevant ones.

---
"""

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

        # Get dominant act properly (null-safe)
        act_values = {
            'srishti_creation': five_acts.srishti_creation,
            'sthiti_maintenance': five_acts.sthiti_maintenance,
            'samhara_dissolution': five_acts.samhara_dissolution,
            'tirodhana_concealment': five_acts.tirodhana_concealment,
            'anugraha_grace': five_acts.anugraha_grace
        }
        dominant_act_value = act_values.get(five_acts.dominant) if five_acts.dominant else None

        # Get dominant guna value (null-safe)
        guna_values = {'sattva': gunas.sattva, 'rajas': gunas.rajas, 'tamas': gunas.tamas}
        dominant_guna_value = guna_values.get(gunas.dominant) if gunas.dominant else None

        # Build context guidance from Call 1 context
        context_guidance = self._build_context_guidance(state)

        # Build data quality section if we have metadata
        data_quality_section = self._build_data_quality_section(state)

        return f"""## CALCULATED CONSCIOUSNESS STATE

{context_guidance}{data_quality_section}
### CORE CONFIGURATION

**S-Level:** {_fmt_score(s_level.current)} ({s_level.label or 'Unknown'})
- Evolution rate: {_fmt(s_level.transition_rate, decimals=1)} per month

**Primary Operating Mode:**
- Dominant Act: {(five_acts.dominant or 'unknown').replace('_', ' ').title()} ({_fmt(dominant_act_value)})
- Dominant Guna: {(gunas.dominant or 'unknown').title()} ({_fmt(dominant_guna_value)})
- Temporal Focus: {_fmt(ops.T_time_past)} past, {_fmt(ops.T_time_present)} present, {_fmt(ops.T_time_future)} future

**Key Operators:**
- Presence (now-moment): {_fmt(ops.P_presence)}
- Awareness: {_fmt(ops.A_aware)}
- Maya (illusion): {_fmt(ops.M_maya)}
- Attachment: {_fmt(ops.At_attachment)}
- Grace flow: {_fmt(ops.G_grace)}
- Witness: {_fmt(ops.W_witness)}
- Surrender: {_fmt(ops.S_surrender)}
- Coherence: {_fmt(ops.Co_coherence)}
- Resistance: {_fmt(ops.R_resistance)}
- Fear: {_fmt(ops.F_fear)}

### TRANSFORMATION POSITION

**Matrix Positions:**
- Truth: {matrices.truth_position or 'Unknown'} ({_fmt(matrices.truth_score)})
- Love: {matrices.love_position or 'Unknown'} ({_fmt(matrices.love_score)})
- Power: {matrices.power_position or 'Unknown'} ({_fmt(matrices.power_score)})
- Freedom: {matrices.freedom_position or 'Unknown'} ({_fmt(matrices.freedom_score)})
- Creation: {matrices.creation_position or 'Unknown'} ({_fmt(matrices.creation_score)})
- Time: {matrices.time_position or 'Unknown'} ({_fmt(matrices.time_score)})
- Death: {matrices.death_position or 'Unknown'} ({_fmt(matrices.death_score)})

**Active Death Processes:**
{f"- {death.active_process} (depth: {_fmt(death.depth)})" if death.active_process else "- None currently active"}

### ENERGY DISTRIBUTION

**Chakra Activation:**
- Root (survival): {_fmt(chakras.muladhara)}
- Sacral (creativity): {_fmt(chakras.svadhisthana)}
- Solar Plexus (power): {_fmt(chakras.manipura)}
- Heart (love): {_fmt(chakras.anahata)}
- Throat (expression): {_fmt(chakras.vishuddha)}
- Third Eye (intuition): {_fmt(chakras.ajna)}
- Crown (connection): {_fmt(chakras.sahasrara)}

**Drive Fulfillment:**
- Love: {_fmt(drives_int.love_internal_pct)} internal, {_fmt(drives_int.love_external_pct)} seeking externally
- Peace: {_fmt(drives_int.peace_internal_pct)} internal, {_fmt(drives_int.peace_external_pct)} seeking externally
- Freedom: {_fmt(drives_int.freedom_internal_pct)} internal, {_fmt(drives_int.freedom_external_pct)} seeking externally

### TRANSFORMATION READINESS

**Breakthrough Dynamics:**
- Breakthrough probability: {_fmt(breakthrough.probability)}
- Distance to tipping point: {_fmt(breakthrough.tipping_point_distance)}
- Quantum jump possibility: {_fmt(breakthrough.quantum_jump_prob)}
{f"- Operators at breakthrough threshold: {', '.join(breakthrough.operators_at_threshold)}" if breakthrough.operators_at_threshold else ""}

**Timeline Predictions:**
- To stated goal: {timeline.to_goal or 'Not calculated'}
- To next S-level: {timeline.to_next_s_level or 'Not calculated'}
- Evolution rate: {_fmt(timeline.evolution_rate, decimals=1)} per month

**Manifestation Capacity:**
- Pipeline flow rate: {_fmt(pipeline.flow_rate)}
- Typical manifestation time: {pipeline.manifestation_time or 'Not calculated'}

**Grace Mechanics:**
- Availability: {_fmt(grace_mech.availability)}
- Effectiveness: {_fmt(grace_mech.effectiveness)}
- Multiplication factor: {grace_mech.multiplication_factor:.2f}x if grace_mech.multiplication_factor else 'N/A'

### COHERENCE & GAPS

**Coherence Metrics:**
- Overall coherence: {_fmt(coherence.overall)}
- Fundamental: {_fmt(coherence.fundamental)}
- Specification: {_fmt(coherence.specification)}

**POMDP Gaps (Reality Perception):**
- Reality gap (what's real vs what you believe): {_fmt(pomdp.reality_gap)}
- Observation gap (what's real vs what you see): {_fmt(pomdp.observation_gap)}
- Belief gap (what you believe vs what you see): {_fmt(pomdp.belief_gap)}
- Overall severity: {_fmt(pomdp.severity)}

### TRANSFORMATION VECTORS

- Current state: {transform.current_state_summary or "Not analyzed"}
- Target state: {transform.target_state_summary or "Not specified"}
- Core shift required: {transform.core_shift_required or "Not determined"}
- Primary obstacle: {transform.primary_obstacle or "Not identified"}
- Primary enabler: {transform.primary_enabler or "Not identified"}
- Leverage point: {transform.leverage_point or "See leverage section"}"""

    def _build_data_quality_section(self, state: ConsciousnessState) -> str:
        """Build data quality/metadata section showing what's missing."""
        # Check if we have inference metadata
        if not hasattr(state, 'inference_metadata') or state.inference_metadata is None:
            return ""

        meta = state.inference_metadata

        sections = ["\n### DATA QUALITY NOTICE\n"]

        # Coverage info
        if hasattr(meta, 'populated_operators') and hasattr(meta, 'missing_operators'):
            populated = len(meta.populated_operators) if meta.populated_operators else 0
            missing = len(meta.missing_operators) if meta.missing_operators else 0
            total = populated + missing
            coverage = (populated / total * 100) if total > 0 else 0

            sections.append(f"**Operator Coverage:** {populated}/{total} ({coverage:.0f}%)")

            if meta.missing_operators:
                missing_list = ', '.join(list(meta.missing_operators)[:10])
                if len(meta.missing_operators) > 10:
                    missing_list += f" (and {len(meta.missing_operators) - 10} more)"
                sections.append(f"**Missing Operators:** {missing_list}")

        # Blocked formulas
        if hasattr(meta, 'blocked_formulas') and meta.blocked_formulas:
            blocked_list = ', '.join(list(meta.blocked_formulas)[:5])
            if len(meta.blocked_formulas) > 5:
                blocked_list += f" (and {len(meta.blocked_formulas) - 5} more)"
            sections.append(f"**Blocked Calculations:** {blocked_list}")
            sections.append("(Some calculations show N/A due to missing input operators)")

        return '\n'.join(sections) + "\n"

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
{priorities_str}

## EVIDENCE-GROUNDING PROTOCOL

When web search is enabled, you must GROUND consciousness values in observable reality.
Use the search_guidance from Call 1 to find cited proof for key insights.

### CONSCIOUSNESS → REALITY MANIFESTATION PATTERNS

Use these mappings to translate calculated values into searchable evidence:

**HIGH ATTACHMENT (At > 0.70)**
- Observable: Resistance to change, sunk cost behavior, loyalty to legacy
- Search for: "[entity] migration challenges", "[entity] change resistance", "[entity] legacy systems"
- Proof type: Industry reports, analyst assessments, leadership quotes

**HIGH MAYA (M > 0.65)**
- Observable: Market perception vs reality gaps, optimistic forecasting, blind spots
- Search for: "[entity] analyst vs reality", "[entity] market expectations", "[entity] missed targets"
- Proof type: Third-party assessments, competitor comparisons, historical predictions vs outcomes

**SEPARATION MATRIX POSITION**
- Observable: Competitive vs collaborative behavior, protective boundaries, siloed operations
- Search for: "[entity] competitive strategy", "[entity] vs [competitors]", "[entity] partnership failures"
- Proof type: Strategy analysis, partnership history, market positioning

**HIGH RESISTANCE (Re > 0.60)**
- Observable: Organizational friction, slow adoption, internal politics
- Search for: "[entity] organizational challenges", "[entity] internal conflicts", "[entity] transformation failures"
- Proof type: Employee reviews, leadership changes, restructuring news

**GRACE AVAILABILITY (G > 0.60)**
- Observable: Synchronicities, unexpected opportunities, favorable conditions
- Search for: "[entity] new partnerships", "[entity] market opportunities", "[entity] recent wins"
- Proof type: Partnership announcements, market trends favoring entity, recent successes

**BREAKTHROUGH PROBABILITY (> 0.65)**
- Observable: Near-term catalysts, emerging opportunities, inflection signals
- Search for: "[entity] upcoming catalyst", "[entity] innovation announcements", "[entity] market timing"
- Proof type: Product launches, strategic initiatives, market timing indicators

**DEATH ARCHITECTURE ACTIVE**
- Observable: What is ending/dying - old products, old strategies, old identity
- Search for: "[entity] discontinuing", "[entity] pivot strategy", "[entity] sunset products"
- Proof type: Discontinuation announcements, strategic pivots, phase-outs

### EVIDENCE INTEGRATION RULES

1. **Search Strategically**: Use the evidence_search_queries from search_guidance
2. **Cite Naturally**: Integrate evidence into narrative flow - no "according to search" phrasing
3. **Ground Major Claims**: Every significant insight should have observable proof
4. **Quality Over Quantity**: 3-5 well-cited insights > 10 vague claims
5. **Connect Dots**: Show how consciousness pattern → observable reality → cited proof
6. **Include Sources**: End with "Sources:" section listing all web sources used"""

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
    domain_language: bool = True,
    search_guidance_data: Optional[dict] = None
) -> ArticulationContext:
    """
    Helper function to build ArticulationContext from components.

    Args:
        search_guidance_data: Optional dict from Call 1 with structure:
            {
                "high_priority_values": [...],
                "evidence_search_queries": [...],
                "consciousness_to_reality_mappings": [...]
            }
    """
    # Build search_guidance from dict if provided
    search_guidance = SearchGuidance()
    if search_guidance_data:
        search_guidance.high_priority_values = search_guidance_data.get('high_priority_values', [])
        search_guidance.query_pattern = search_guidance_data.get('query_pattern', '')

        # Build evidence search queries
        for esq in search_guidance_data.get('evidence_search_queries', []):
            if isinstance(esq, dict):
                search_guidance.evidence_search_queries.append(
                    EvidenceSearchQuery(
                        target_value=esq.get('target_value', ''),
                        search_query=esq.get('search_query', ''),
                        proof_type=esq.get('proof_type', '')
                    )
                )

        # Build consciousness-to-reality mappings
        for crm in search_guidance_data.get('consciousness_to_reality_mappings', []):
            if isinstance(crm, dict):
                search_guidance.consciousness_to_reality_mappings.append(
                    ConsciousnessRealityMapping(
                        consciousness_value=crm.get('consciousness_value', ''),
                        observable_reality=crm.get('observable_reality', ''),
                        proof_search=crm.get('proof_search', '')
                    )
                )

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
            market_data=None,
            search_guidance=search_guidance
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
        ),
        search_guidance=search_guidance
    )
