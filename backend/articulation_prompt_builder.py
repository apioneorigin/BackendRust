"""
Articulation Prompt Builder for Articulation Bridge
Constructs the final LLM Call 2 prompt with organized values

ZERO-FALLBACK MODE: Properly handles null/missing operator values.
Shows "Not available" for blocked calculations instead of assuming defaults.
"""

from typing import List, Optional, Dict
from consciousness_state import (
    ArticulationContext, ConsciousnessState, Bottleneck, LeveragePoint,
    UserContext, WebResearch, ArticulationInstructions,
    SearchGuidance, EvidenceSearchQuery, ConsciousnessRealityMapping,
    ConversationHistoryContext,
)
from logging_config import articulation_logger as logger
from utils.framework_translation import (
    translate_s_level_label,
    translate_act_name,
    translate_operator,
    translate_death_code,
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

        UNITY PRINCIPLE: Now includes unity metrics and dual pathway sections.
        CONTINUITY: Now includes conversation history and file context.
        """
        logger.info("[PROMPT_BUILDER] Building articulation prompt")

        sections = [
            self._build_header(),
            self._build_framework_section(),
            self._build_conversation_context_section(context.conversation_context),  # Conversation history + files
            self._build_context_section(context.user_context, context.web_research),
            self._build_consciousness_state_section(context.consciousness_state),
            self._build_unity_metrics_section(context.consciousness_state),
            self._build_dual_pathway_section(context.consciousness_state),
            self._build_bottleneck_section(context.consciousness_state.bottlenecks),
            self._build_leverage_section(context.consciousness_state.leverage_points),
            self._build_search_guidance_section(context.search_guidance),
            self._build_generation_instructions(context.instructions),
            self._build_structured_output_section(
                include_question=context.include_question,
                question_context=context.question_context
            ),
            self._build_user_query(context.user_context)
        ]

        # Filter out empty sections
        all_count = len(sections)
        sections = [s for s in sections if s and s.strip()]
        prompt = '\n\n---\n\n'.join(sections)

        logger.info(
            f"[PROMPT_BUILDER] Prompt built: {len(sections)}/{all_count} sections, "
            f"{len(prompt)} chars total"
        )

        return prompt

    def _build_search_guidance_section(self, search_guidance: SearchGuidance) -> str:
        """Build the search guidance section for evidence grounding in Call 2"""
        if not search_guidance or not search_guidance.high_priority_values:
            logger.debug("[_build_search_guidance_section] skipped: no search guidance or no high-priority values")
            return ""

        priority_count = len(search_guidance.high_priority_values)
        query_count = len(search_guidance.evidence_search_queries) if search_guidance.evidence_search_queries else None
        mapping_count = len(search_guidance.consciousness_to_reality_mappings) if search_guidance.consciousness_to_reality_mappings else None
        logger.debug(
            f"[_build_search_guidance_section] guidance present: "
            f"priorities={priority_count} queries={query_count} "
            f"mappings={mapping_count} pattern={search_guidance.query_pattern}"
        )

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
When web search is enabled, use these search queries to find CITED PROOF for the calculated inner state values.
Ground evidence searches in calculated values; if a suggested search targets a blocked calculation, skip it or adapt to a related calculated value.
Each major insight should connect: Inner Pattern → Observable Reality → Cited Evidence.""")

        return '\n'.join(sections)

    def _build_conversation_context_section(self, conversation_context: Optional[ConversationHistoryContext]) -> str:
        """Build conversation history and file context section.

        This provides continuity across multi-turn conversations and incorporates
        information from uploaded files for domain-specific analysis.
        """
        if not conversation_context:
            return ""

        sections = ["## CONVERSATION CONTEXT\n"]
        has_content = False

        # Add conversation summary if available (for long conversations)
        if conversation_context.conversation_summary:
            has_content = True
            sections.append(f"""**Previous Conversation Summary:**
{conversation_context.conversation_summary}
""")

        # Add file context if available
        if conversation_context.file_summaries:
            has_content = True
            sections.append("**Uploaded Files:**")
            sections.append("The user has provided the following files. Use this information for context-aware analysis:\n")
            for i, f in enumerate(conversation_context.file_summaries[:5], 1):  # Max 5 files
                file_name = f.get('name', 'Unknown')
                file_type = f.get('type', 'unknown')
                file_summary = f.get('summary', '')[:2000]  # Truncate
                sections.append(f"**{i}. {file_name}** ({file_type})")
                sections.append(f"{file_summary}\n")

        # Add conversation history if available
        if conversation_context.messages:
            has_content = True
            sections.append("**Recent Conversation History:**")
            sections.append("Use this history to maintain continuity and build on previous insights:\n")
            for msg in conversation_context.messages[-8:]:  # Last 8 messages
                role = msg.get('role', 'unknown').upper()
                content = msg.get('content', '')[:800]  # Truncate long messages
                sections.append(f"[{role}]: {content}\n")

        # Add answered questions context (user's choices inform analysis)
        if conversation_context.question_answers:
            has_content = True
            sections.append("**User's Answered Questions:**")
            sections.append("The user has answered these clarifying questions. Use their choices to refine your analysis:\n")
            for qa in conversation_context.question_answers:
                question = qa.get('question', '')
                answer = qa.get('selected_answer', '')
                sections.append(f"Q: {question}")
                sections.append(f"A: {answer}\n")

        # Add matrix state context (user's selected dimensions for analysis focus)
        if conversation_context.matrix_state:
            has_content = True
            ms = conversation_context.matrix_state
            row_labels = ms.get('selected_row_labels', [])
            col_labels = ms.get('selected_column_labels', [])
            total_rows = ms.get('total_rows_available', 0)
            total_cols = ms.get('total_columns_available', 0)
            cell_values = ms.get('cell_values', [])
            # Document count metadata
            active_doc_name = ms.get('active_document_name', 'Primary Document')
            total_docs = ms.get('total_documents', 1)
            populated_docs = ms.get('populated_documents', 1)

            sections.append("**User's Matrix Focus Selection:**")
            sections.append(f"Active Document: {active_doc_name} ({populated_docs} of {total_docs} documents fully populated)")
            sections.append(f"The user has chosen to focus on specific dimensions from the transformation matrix.")
            sections.append(f"Selected Row Dimensions ({len(row_labels)} of {total_rows} available): {', '.join(row_labels)}")
            sections.append(f"Selected Column Dimensions ({len(col_labels)} of {total_cols} available): {', '.join(col_labels)}")

            # Include cell values and dimensions if available
            if cell_values:
                sections.append("\n**Current Matrix Cell Values (user's focus area):**")
                for cv in cell_values[:25]:  # All 25 selected cells (5x5 grid)
                    row = cv.get('row', '')
                    col = cv.get('column', '')
                    impact = cv.get('impact_score', 50)
                    relationship = cv.get('relationship', '')
                    dims = cv.get('dimensions', '')
                    rel_str = f" - {relationship}" if relationship else ""
                    sections.append(f"• {row} × {col}: Impact {impact}%{rel_str} | {dims}")

            sections.append("\nPrioritize insights related to these selected dimensions and their current values in your analysis.\n")

        if not has_content:
            return ""

        sections.append("""**CONTINUITY INSTRUCTIONS:**
- Reference specific information from uploaded files when relevant
- Build on insights from previous messages rather than starting fresh
- Maintain consistency with any analysis or recommendations from earlier in the conversation
- Use domain-specific terminology found in the uploaded documents
- IMPORTANT: Incorporate the user's answered questions into your analysis - their choices reveal priorities and preferences
- IMPORTANT: Focus analysis on the user's selected matrix dimensions - they indicate areas of priority
""")

        logger.debug(
            f"[_build_conversation_context_section] messages={len(conversation_context.messages)} "
            f"files={len(conversation_context.file_summaries)} "
            f"summary={'yes' if conversation_context.conversation_summary else 'no'}"
        )

        return '\n'.join(sections)

    def _build_header(self) -> str:
        """Build the prompt header"""
        return """# REALITY TRANSFORMER: INSIGHT ARTICULATION

You are receiving a complete deep pattern analysis based on our analytical methodology.

Your task is to articulate these insights in natural language that the user can understand and act upon.

Express all insights using natural, domain-appropriate language that feels like wisdom from a trusted advisor."""

    def _build_framework_section(self) -> str:
        """Build framework reference section - FREEDOM-RESPECTING VERSION"""
        return """## METHODOLOGY REFERENCE

You are receiving pre-calculated inner state values from the backend inference engine.
These values are your source of truth - interpret and articulate them naturally.

Express insights as if speaking to a trusted friend or client.

## VALUE SELECTION PROTOCOL

You are receiving ALL calculated inner state values (~1,500-2,500 values).
Your task is to SELECT which values to articulate based on context.

### SELECTION PRINCIPLES:

**1. QUERY RELEVANCE (Priority 1)**
Select values that directly answer the user's specific question.
Focus on what matters for THIS query, not generic patterns.

**2. USER-REQUESTED TARGETS (Priority 2)**
LLM Call 1 identified targets based on query analysis.
These are high-confidence relevant values - include them.

**3. SEARCH GUIDANCE HIGH-PRIORITY (Priority 3)**
LLM Call 1 flagged values for evidence-grounding.
Include these if relevant to the query.

**4. CAUSAL CHAIN COMPLETENESS**
If articulating bottleneck X, include ALL values in its causal chain.
Show the full inner pattern → reality connection.
Don't leave causal gaps.

**5. TRANSFORMATION CONTEXT**
If discussing transformation, include transformation-related values
(growth phase, matrices, dissolution patterns, flow availability).

### ARTICULATION EFFICIENCY:

- Articulate 20-50 key values (not all 2,500)
- USE the full value set to understand the complete picture
- Synthesize patterns across all values
- Reference supporting values without listing them all

### PRINCIPLE:

You have access to EVERYTHING. Use your intelligence and context to decide
what matters for THIS query. Don't list all values - synthesize the relevant
ones into breakthrough insights.

### CALCULATED VS NON-CALCULATED VALUES:

- Values showing actual numbers = successfully calculated from user's data
- Values showing "N/A" or "Not calculated" = blocked due to missing input factors
- Base your insights ONLY on calculated values
- Never fabricate or estimate blocked values

**Two types of non-calculated values:**
1. **Question-addressable gaps** (listed in DATA QUALITY section): These are blocked because
   specific input factors weren't extracted from the user's query. A follow-up question can
   fill these. Reference them as: "to assess X, I'd need to understand more about Y in your experience"
2. **Context-addressable gaps** (listed in DATA QUALITY section): These are blocked because
   upstream calculations they depend on couldn't complete. These cannot be filled by asking
   questions. Reference them naturally: "based on what's available..." without drawing attention
   to the gap."""

    def _build_context_section(
        self,
        user_context: UserContext,
        web_research: WebResearch
    ) -> str:
        """Build user context and web research section"""
        logger.debug(
            f"[_build_context_section] identity={user_context.identity} "
            f"domain={user_context.domain} "
            f"goal_len={len(user_context.goal or '')} "
            f"constraints={len(user_context.constraints) if user_context.constraints else None} "
            f"searches={len(web_research.searches_performed) if web_research.searches_performed else None} "
            f"facts={len(web_research.key_facts) if web_research.key_facts else None}"
        )
        constraints_str = '\n'.join(f"- {c}" for c in user_context.constraints) if user_context.constraints else "- None specified"

        searches_str = ""
        if web_research.searches_performed:
            searches_str = '\n'.join(
                f"- \"{s.get('query')}\": {s.get('summary')}"
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
        logger.debug("[_build_consciousness_state_section] entry")
        ops = state.tier1.core_operators
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

        # Log operator population details
        op_fields = [
            ops.P_presence, ops.A_aware, ops.M_maya, ops.At_attachment,
            ops.G_grace, ops.W_witness, ops.S_surrender, ops.Co_coherence,
            ops.R_resistance, ops.F_fear, ops.E_equanimity, ops.Se_service,
            ops.D_dharma, ops.K_karma, ops.I_intention, ops.Hf_habit,
        ]
        populated_count = sum(1 for v in op_fields if v is not None)
        none_count = len(op_fields) - populated_count
        logger.debug(
            f"[_build_consciousness_state_section] operators: populated={populated_count} "
            f"none={none_count} s_level={s_level.current} "
            f"dominant_act={five_acts.dominant} dominant_guna={gunas.dominant}"
        )

        return f"""## CALCULATED INNER STATE

{context_guidance}{data_quality_section}
### CORE CONFIGURATION

**Growth Phase:** {_fmt_score(s_level.current)} ({translate_s_level_label(s_level.current)})
- Evolution rate: {_fmt(s_level.transition_rate, decimals=1)} per month

**Primary Operating Mode:**
- Dominant Phase: {translate_act_name(five_acts.dominant)} ({_fmt(dominant_act_value)})
- Dominant Energy: {(gunas.dominant or 'unknown').title()} ({_fmt(dominant_guna_value)})
- Temporal Focus: {_fmt(ops.T_time_past)} past, {_fmt(ops.T_time_present)} present, {_fmt(ops.T_time_future)} future

**Key Factors:**
- Present-moment awareness: {_fmt(ops.P_presence)}
- Self-awareness: {_fmt(ops.A_aware)}
- Blind spots: {_fmt(ops.M_maya)}
- Clinging patterns: {_fmt(ops.At_attachment)}
- Flow and breakthroughs: {_fmt(ops.G_grace)}
- Objective perspective: {_fmt(ops.W_witness)}
- Letting go capacity: {_fmt(ops.S_surrender)}
- Inner alignment: {_fmt(ops.Co_coherence)}
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
- Dissolution: {matrices.death_position or 'Unknown'} ({_fmt(matrices.death_score)})

**Active Dissolution Processes:**
{f"- {translate_death_code(death.active_process)} (depth: {_fmt(death.depth)})" if death.active_process else "- None currently active"}

### ENERGY DISTRIBUTION

**Energy Centers:**
- Root (stability): {_fmt(chakras.muladhara)}
- Sacral (creativity): {_fmt(chakras.svadhisthana)}
- Solar Plexus (drive): {_fmt(chakras.manipura)}
- Heart (connection): {_fmt(chakras.anahata)}
- Throat (expression): {_fmt(chakras.vishuddha)}
- Insight center: {_fmt(chakras.ajna)}
- Higher connection: {_fmt(chakras.sahasrara)}

**Drive Fulfillment:**
- Love: {_fmt(drives_int.love_internal_pct)} internal, {_fmt(drives_int.love_external_pct)} seeking externally
- Peace: {_fmt(drives_int.peace_internal_pct)} internal, {_fmt(drives_int.peace_external_pct)} seeking externally
- Freedom: {_fmt(drives_int.freedom_internal_pct)} internal, {_fmt(drives_int.freedom_external_pct)} seeking externally

### TRANSFORMATION READINESS

**Breakthrough Dynamics:**
- Breakthrough probability: {_fmt(breakthrough.probability)}
- Distance to tipping point: {_fmt(breakthrough.tipping_point_distance)}
- Breakthrough jump possibility: {_fmt(breakthrough.quantum_jump_prob)}
{f"- Factors at breakthrough threshold: {', '.join(translate_operator(op) for op in breakthrough.operators_at_threshold)}" if breakthrough.operators_at_threshold else ""}

**Timeline Predictions:**
- To stated goal: {timeline.to_goal or 'Not calculated'}
- To next growth phase: {timeline.to_next_s_level or 'Not calculated'}
- Evolution rate: {_fmt(timeline.evolution_rate, decimals=1)} per month

**Manifestation Capacity:**
- Pipeline flow rate: {_fmt(pipeline.flow_rate)}
- Typical manifestation time: {pipeline.manifestation_time or 'Not calculated'}

**Flow Mechanics:**
- Availability: {_fmt(grace_mech.availability)}
- Effectiveness: {_fmt(grace_mech.effectiveness)}
- Amplification factor: {f'{grace_mech.multiplication_factor:.2f}x' if grace_mech.multiplication_factor else 'N/A'}

### ALIGNMENT & GAPS

**Alignment Metrics:**
- Overall alignment: {_fmt(coherence.overall)}
- Fundamental: {_fmt(coherence.fundamental)}
- Specification: {_fmt(coherence.specification)}

**Reality Perception Gaps:**
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

    def _build_unity_metrics_section(self, state: ConsciousnessState) -> str:
        """
        Build the Unity Principle metrics section.

        FRAMEWORK CONCEALMENT: Express Jeevatma-Paramatma dynamics in natural language.
        User never sees terms like "separation distance" - translate to accessible concepts.
        """
        # Check if unity metrics are available
        if not hasattr(state, 'unity_metrics') or state.unity_metrics is None:
            logger.debug("[_build_unity_metrics_section] skipped: unity_metrics not present")
            return ""

        um = state.unity_metrics

        if all(v is not None for v in [um.separation_distance, um.unity_vector, um.percolation_quality, um.distortion_field]):
            logger.debug(
                f"[_build_unity_metrics_section] unity data present: "
                f"sep_dist={um.separation_distance:.3f} vector={um.unity_vector:.3f} "
                f"percolation={um.percolation_quality:.3f} distortion={um.distortion_field:.3f} "
                f"direction={um.net_direction}"
            )
        else:
            logger.debug("[_build_unity_metrics_section] unity data partial: some metrics are None")

        # Skip if any key metrics are None (not calculated)
        if any(v is None for v in [um.unity_vector, um.separation_distance, um.percolation_quality]):
            logger.debug("[_build_unity_metrics_section] skipped: key metrics are None")
            return ""

        # Translate unity_vector to direction description
        if um.unity_vector > 0.3:
            direction_desc = "strongly moving toward alignment and flow"
        elif um.unity_vector > 0.1:
            direction_desc = "gradually moving toward alignment"
        elif um.unity_vector > -0.1:
            direction_desc = "in a neutral holding pattern"
        elif um.unity_vector > -0.3:
            direction_desc = "experiencing some resistance and contraction"
        else:
            direction_desc = "in a pattern of effort-based striving"

        # Translate separation distance to experience description
        if um.separation_distance < 0.2:
            separation_desc = "deep sense of connection and support"
        elif um.separation_distance < 0.4:
            separation_desc = "periodic access to flow states and synchronicity"
        elif um.separation_distance < 0.6:
            separation_desc = "fluctuating between effort and ease"
        elif um.separation_distance < 0.8:
            separation_desc = "primarily effort-based with occasional breakthroughs"
        else:
            separation_desc = "strong sense of separation and struggle"

        # Translate percolation quality
        if um.percolation_quality > 0.7:
            percolation_desc = "Support and resources flow easily when needed"
        elif um.percolation_quality > 0.5:
            percolation_desc = "Support is available but sometimes blocked"
        elif um.percolation_quality > 0.3:
            percolation_desc = "Resources often feel scarce or delayed"
        else:
            percolation_desc = "Feeling of having to generate everything through effort"

        return f"""### CONSCIOUSNESS DYNAMICS

**Current Experience Pattern:**
- {separation_desc.capitalize()}
- Direction: {direction_desc}

**Resource Flow:**
- {percolation_desc}
- Distortion factor: {_fmt(um.distortion_field)} (how much perception is filtered)

**Net Movement:** {um.net_direction.replace('_', ' ').title() if um.net_direction else 'Neutral'}"""

    def _build_dual_pathway_section(self, state: ConsciousnessState) -> str:
        """
        Build the dual pathway analysis section.

        FRAMEWORK CONCEALMENT: Express separation vs unity pathways as
        "effort-based" vs "flow-based" approaches to goals.
        """
        # Check if dual pathways are available
        if not hasattr(state, 'dual_pathways') or state.dual_pathways is None:
            logger.debug("[_build_dual_pathway_section] skipped: dual_pathways not present")
            return ""

        dp = state.dual_pathways

        # Skip if pathway probabilities are None (not calculated)
        if dp.separation_pathway.initial_success_probability is None and dp.unity_pathway.initial_success_probability is None:
            logger.debug("[_build_dual_pathway_section] skipped: pathway probabilities are None (not calculated)")
            return ""

        logger.debug(
            f"[_build_dual_pathway_section] pathway data present: "
            f"recommended={dp.recommended_pathway} "
            f"sep_success={dp.separation_pathway.initial_success_probability} "
            f"unity_success={dp.unity_pathway.initial_success_probability} "
            f"crossover={dp.crossover_point_months}"
        )

        # Build comparison
        sep = dp.separation_pathway
        uni = dp.unity_pathway

        # Translate recommended pathway
        if dp.recommended_pathway == 'unity':
            recommendation = "The flow-based approach is recommended - it may start slower but creates lasting results"
        elif dp.recommended_pathway == 'separation':
            recommendation = "The effort-based approach may be needed initially to build momentum"
        else:
            if dp.optimal_blend_ratio is not None:
                recommendation = f"A blend is recommended - {_fmt(dp.optimal_blend_ratio)} effort with {_fmt(1 - dp.optimal_blend_ratio)} flow"
            else:
                recommendation = "A blend of effort and flow is recommended"

        # Crossover description
        if dp.crossover_point_months and dp.crossover_point_months > 0:
            crossover_desc = f"Flow-based approach overtakes effort-based around month {dp.crossover_point_months:.0f}"
        else:
            crossover_desc = "Timeline depends on current state and goal complexity"

        return f"""### TWO PATHS TO YOUR GOAL

**Effort-Based Approach (Pushing Through):**
- Initial success probability: {_fmt(sep.initial_success_probability)}
- Long-term sustainability: {_fmt(sep.sustainability_probability)}
- Fulfillment quality if achieved: {_fmt(sep.fulfillment_quality)}
- Tendency: Results may fade over time (decay: {_fmt(sep.decay_rate)}/year)

**Flow-Based Approach (Aligned Action):**
- Initial success probability: {_fmt(uni.initial_success_probability)}
- Long-term sustainability: {_fmt(uni.sustainability_probability)}
- Fulfillment quality if achieved: {_fmt(uni.fulfillment_quality)}
- Tendency: Results compound over time (growth: {_fmt(uni.compound_rate)}/year)

**Comparison:**
- {crossover_desc}
- {recommendation}"""

    def _build_data_quality_section(self, state: ConsciousnessState) -> str:
        """Build data quality/metadata section showing calculated vs non-calculated buckets."""
        sections = ["\n### DATA QUALITY NOTICE\n"]
        has_content = False

        calc_count = len(state.calculated_values)
        q_count = len(state.non_calculated_question_addressable)
        c_count = len(state.non_calculated_context_addressable)
        total = calc_count + q_count + c_count

        if total > 0:
            has_content = True
            coverage = calc_count / total * 100
            sections.append(f"**Calculation Coverage:** {calc_count}/{total} metrics computed ({coverage:.0f}%)")

            if q_count > 0:
                q_list = ', '.join(state.non_calculated_question_addressable[:15])
                if q_count > 15:
                    q_list += f" (and {q_count - 15} more)"
                sections.append(f"\n**Question-Addressable Gaps ({q_count} metrics):** {q_list}")
                sections.append(
                    "These metrics are blocked because specific input operators weren't extracted "
                    "from the user's query. A follow-up constellation question can fill these gaps. "
                    "Reference as: \"to assess X, I'd need to understand more about Y in your experience.\""
                )

            if c_count > 0:
                c_list = ', '.join(state.non_calculated_context_addressable[:15])
                if c_count > 15:
                    c_list += f" (and {c_count - 15} more)"
                sections.append(f"\n**Context-Addressable Gaps ({c_count} metrics):** {c_list}")
                sections.append(
                    "These metrics are blocked because upstream calculations they depend on "
                    "couldn't complete. Not fixable by asking questions. Reference naturally: "
                    "\"based on what's available...\" without drawing attention to the gap."
                )

        # Missing operator priority from LLM Call 1
        if state.missing_operator_priority:
            has_content = True
            priority_list = ', '.join(state.missing_operator_priority[:10])
            sections.append(f"\n**Priority Missing Operators:** {priority_list}")
            sections.append("(These operators were identified as most important but could not be extracted from user input)")

        if not has_content:
            logger.debug("[_build_data_quality_section] skipped: no quality data available")
            return ""

        logger.debug(
            f"[_build_data_quality_section] calculated={calc_count} "
            f"question_addressable={q_count} context_addressable={c_count} "
            f"priority_missing={len(state.missing_operator_priority)}"
        )
        return '\n'.join(sections) + "\n"

    def _build_bottleneck_section(self, bottlenecks: List[Bottleneck]) -> str:
        """
        Build the bottleneck analysis section with Unity Principle enhancement.

        UNITY PRINCIPLE: Show both separation-based and unity-aligned interventions.
        Identify root separation patterns vs surface symptoms.
        """
        if not bottlenecks:
            logger.debug("[_build_bottleneck_section] no bottlenecks detected")
            return """## BOTTLENECK ANALYSIS

No major bottlenecks detected. Transformation pathway is relatively clear."""

        high_impact = [b for b in bottlenecks if b.impact == 'high']
        medium_impact = [b for b in bottlenecks if b.impact == 'medium']
        logger.debug(
            f"[_build_bottleneck_section] bottleneck_count={len(bottlenecks)} "
            f"high={len(high_impact)} medium={len(medium_impact)}"
        )

        # Identify root separation patterns
        root_patterns = [b for b in bottlenecks if getattr(b, 'is_root_separation_pattern', False)]

        sections = ["## BOTTLENECK ANALYSIS\n"]

        # Highlight root patterns first
        if root_patterns:
            sections.append("**ROOT PATTERNS (Address These First):**")
            for b in root_patterns[:2]:
                sections.append(f"- {b.description}")
                if getattr(b, 'unity_aligned_intervention', ''):
                    sections.append(f"  → Flow approach: {b.unity_aligned_intervention}")
            sections.append("")

        if high_impact:
            sections.append("**HIGH IMPACT BOTTLENECKS:**")
            for b in high_impact[:3]:
                root_marker = " [ROOT]" if getattr(b, 'is_root_separation_pattern', False) else ""
                sections.append(f"- [{b.category.upper()}]{root_marker} {b.description}")
                # Show both intervention types if available
                if getattr(b, 'unity_aligned_intervention', '') and getattr(b, 'separation_based_intervention', ''):
                    sections.append(f"  → Flow approach: {b.unity_aligned_intervention}")
                    sections.append(f"  → Effort approach: {b.separation_based_intervention}")

        if medium_impact:
            sections.append("\n**MEDIUM IMPACT BOTTLENECKS:**")
            for b in medium_impact[:3]:
                sections.append(f"- [{b.category}] {b.description}")
                if getattr(b, 'unity_aligned_intervention', ''):
                    sections.append(f"  → Flow approach: {b.unity_aligned_intervention}")

        return '\n'.join(sections)

    def _build_leverage_section(self, leverage_points: List[LeveragePoint]) -> str:
        """
        Build the leverage opportunities section with Unity Principle enhancement.

        UNITY PRINCIPLE: Show pathway type and effective impact for each leverage point.
        """
        if not leverage_points:
            logger.debug("[_build_leverage_section] no leverage points detected")
            return """## LEVERAGE OPPORTUNITIES

No high-multiplier opportunities currently active. Focus on clearing bottlenecks to activate leverage."""

        logger.debug(f"[_build_leverage_section] leverage_point_count={len(leverage_points)}")
        sections = ["## LEVERAGE OPPORTUNITIES\n"]

        for i, lp in enumerate(leverage_points[:3], 1):
            # Get enhanced fields with defaults
            pathway_type = getattr(lp, 'pathway_type', 'neutral')
            unity_alignment = getattr(lp, 'unity_alignment', 0.0)
            approach_desc = getattr(lp, 'approach_description', '')

            # Translate pathway type
            if pathway_type == 'unity':
                pathway_label = "Flow-based"
            elif pathway_type == 'separation':
                pathway_label = "Effort-based"
            else:
                pathway_label = "Balanced"

            sections.append(f"""**{i}. {lp.description}** ({lp.multiplier}x multiplier)
   Type: {pathway_label} leverage
   Activation: {lp.activation_requirement}""")

            if approach_desc:
                sections.append(f"   Approach: {approach_desc}")

            if unity_alignment != 0.0:
                alignment_desc = "aligned with natural flow" if unity_alignment > 0.2 else "requires sustained effort" if unity_alignment < -0.2 else "neutral"
                sections.append(f"   Dynamics: {alignment_desc.capitalize()}")

        return '\n\n'.join(sections)

    def _build_generation_instructions(self, instructions: ArticulationInstructions) -> str:
        """Build generation instructions - FREEDOM-RESPECTING VERSION"""
        logger.debug(
            f"[_build_generation_instructions] style={instructions.articulation_style} "
            f"priorities={instructions.insight_priorities}"
        )
        # Build style note
        style_note = """- **Natural Language:** Express all insights using natural,
domain-appropriate language that feels like wisdom from a trusted advisor."""

        # Build domain note if available
        domain_note = ""
        if hasattr(instructions, 'domain_context') and instructions.domain_context:
            domain_note = f"""- **Domain Adaptation:** User is in {instructions.domain_context}
domain. Use appropriate terminology and examples."""

        # Build priorities string if available
        priorities_str = ""
        if instructions.insight_priorities:
            priorities_str = "\n**Priority Insights to Emphasize:**\n" + '\n'.join(
                f"- {p.replace('_', ' ').title()}"
                for p in instructions.insight_priorities
            )

        return f"""## ARTICULATION INSTRUCTIONS

### ARTICULATION GOALS

Your response should accomplish these goals (structure naturally based on context):

**Show Current Reality:** Express where the user actually is vs where they think
they are. Ground this in web research and deep pattern analysis. Point out any
perception gaps.

**Explain Inner Patterns:** Identify which inner patterns are
creating the current situation. Explain HOW these patterns interact to produce
observable results. Make the invisible visible.

**Identify Transformation Requirements:** Describe what actually needs to shift
internally to enable external results. Reference transformation vectors and
leverage points.

**Provide Practical Leverage:** Offer concrete next actions aligned with their
inner state and current capacity.

### STYLE REQUIREMENTS
{style_note}
{domain_note}

- **Natural Flow:** Write as a wise advisor who sees patterns they cannot see,
not as a calculation system reporting numbers.

- **Insight Priority:** Lead with the most impactful insights. Don't try to
communicate everything - focus on what matters most for their transformation.

- **Grounded in Data:** Ground major claims in either web research findings or
calculated inner state values. Express these naturally, not as citations.

- **NO SEPARATORS:** NEVER use "---" or horizontal rules in your response text.
Your prose should flow naturally without visual dividers between sections.
{priorities_str}

### BRIDGE SENTENCE FOR FOLLOW-UP QUESTION

End your main articulation with a natural bridge sentence that creates anticipation
for the follow-up question. This bridge should emerge organically from the specific
insights and context of THIS conversation - never use templated or formulaic phrasing.

**Requirements:**
- The bridge must be UNIQUE to the user's specific situation and what you've just shared
- Draw directly from the inner patterns, insights, or discoveries revealed
- Reference specific details from their context (their domain, challenges, opportunities)
- Let the bridge arise naturally from the logical flow of your articulation

**What to AVOID:**
- Generic phrases like "I find myself curious about..." or "There's a dimension..."
- Any sentence that could apply to ANY user or ANY conversation
- Formulaic structures that feel like templates

The bridge should make the user PAUSE and feel genuinely invited into the question,
not rushed through a checklist. Write it as the final 1-2 sentences of your narrative
prose, flowing naturally from your specific insights about THEIR situation.
Do NOT use "---" before the bridge.

## EVIDENCE GROUNDING PROTOCOL

When inner state values are calculated, ground them in observable reality:

**Process:**
1. Translate inner patterns into measurable behaviors/outcomes
2. Formulate search queries to find observable proof
3. Cite evidence naturally in your articulation
4. Include "Sources:" section at the end listing all web sources used

**Use search_guidance from Call 1** for high-priority values to ground.

**Quality Standards:**
- Focus on major insights (not every value)
- Show inner pattern → observable reality → cited proof
- Integrate evidence into narrative flow naturally
- Let evidence strengthen insights, not replace them"""

    def _build_structured_output_section(
        self,
        include_question: bool = True,
        question_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build instructions for generating structured document matrix data."""
        # Build question schema and instructions based on 2-priority structure
        question_schema = ""
        question_requirement = ""
        question_instructions = ""

        if include_question:
            question_schema = """,
  "follow_up_question": {
    "question_text": "A natural, conversational follow-up question",
    "options": {
      "option_1": "First option",
      "option_2": "Second option",
      "option_3": "Third option",
      "option_4": "Fourth option"
    }
  }"""
            question_requirement = "\n5. **FOLLOW-UP QUESTION**: Include follow_up_question (MANDATORY)"

            # Build detailed question instructions based on priority
            question_instructions = self._build_question_instructions(question_context)

        return f"""## STRUCTURED OUTPUT GENERATION

After your main articulation, generate structured data in JSON format.

**OUTPUT**: 1 document with row/column labels and insight titles only. NO cells, NO full insights.

```json
===STRUCTURED_DATA_START===
{{
  "documents": [
    {{
      "id": "doc-0",
      "name": "Strategic Framework",
      "matrix_data": {{
        "row_options": [
          {{"id": "r0", "label": "Resource Flow", "insight_title": "The Hidden Lanes in Resource Chaos"}},
          {{"id": "r1", "label": "Time Investment", "insight_title": "Velocity Through Clarity"}},
          {{"id": "r2", "label": "Team Dynamics", "insight_title": "The Permission Gap"}},
          {{"id": "r3", "label": "Market Position", "insight_title": "Reading the Current"}},
          {{"id": "r4", "label": "Innovation Pace", "insight_title": "The Momentum Paradox"}},
          {{"id": "r5", "label": "Customer Focus", "insight_title": "Seeing Through Their Eyes"}},
          {{"id": "r6", "label": "Operational Flow", "insight_title": "The Invisible Architecture"}},
          {{"id": "r7", "label": "Strategic Clarity", "insight_title": "North Star Navigation"}},
          {{"id": "r8", "label": "Resource Leverage", "insight_title": "Multiplier Moments"}},
          {{"id": "r9", "label": "Growth Vectors", "insight_title": "Compound Trajectory"}}
        ],
        "column_options": [
          {{"id": "c0", "label": "Growth Impact", "insight_title": "The Scaling Pattern"}},
          {{"id": "c1", "label": "Risk Exposure", "insight_title": "Hidden Fault Lines"}},
          {{"id": "c2", "label": "Team Capacity", "insight_title": "Bandwidth Reality"}},
          {{"id": "c3", "label": "Market Response", "insight_title": "Signal in Noise"}},
          {{"id": "c4", "label": "Innovation Speed", "insight_title": "Acceleration Windows"}},
          {{"id": "c5", "label": "Customer Value", "insight_title": "Value Perception Shift"}},
          {{"id": "c6", "label": "Operational Cost", "insight_title": "Hidden Drag Forces"}},
          {{"id": "c7", "label": "Strategic Fit", "insight_title": "Alignment Geometry"}},
          {{"id": "c8", "label": "Resource Needs", "insight_title": "Investment Leverage"}},
          {{"id": "c9", "label": "Time to Impact", "insight_title": "Velocity Vectors"}}
        ],
        "selected_rows": [0, 1, 2, 3, 4],
        "selected_columns": [0, 1, 2, 3, 4]
      }}
    }}
  ],
  "presets": [
    {{
      "id": "p0",
      "name": "Conservative Path",
      "description": "Low-risk approach",
      "risk_level": "low",
      "time_horizon": "6-12 months",
      "steps": [{{"order": 1, "action": "First step", "rationale": "Why"}}]
    }},
    ... (5 total presets)
  ]{question_schema}
}}
===STRUCTURED_DATA_END===
```

REQUIREMENTS:
1. **1 DOCUMENT**: Generate exactly 1 document with 10 rows and 10 columns
2. **ROW/COLUMN LABELS**: Max 3 words each, contextual to user's situation
3. **INSIGHT TITLES**: Max 10 words each, compelling phrase capturing essence (different from label)
4. **SELECTED**: Recommend which 5 rows and 5 columns to display via selected_rows/selected_columns indices
5. **NO CELLS**: Do NOT generate cells - those are generated separately on user action
6. **NO FULL INSIGHTS**: Only generate insight_title, not the full articulated_insight object
7. **5 PRESETS**: Generate 5 strategic presets with steps{question_requirement}
{question_instructions}"""

    def _build_question_instructions(self, question_context: Optional[Dict[str, Any]]) -> str:
        """
        Build detailed question generation instructions based on 2-priority structure.

        Priority 1 (OPERATOR_EXTRACTION): Missing tier-1 operators
        Priority 2 (INTERPRETATION): All tier-1 available, need interpretation + higher tiers
        """
        if not question_context:
            # Fallback to generic instructions
            return """
### FOLLOW-UP QUESTION (MANDATORY):
Generate a natural, conversational follow-up question with 4 answer options.
Each option should reveal different aspects of the user's inner experience."""

        priority_name = question_context.get('priority_name', 'OPERATOR_EXTRACTION')

        if priority_name == 'OPERATOR_EXTRACTION':
            return self._build_operator_extraction_question_instructions(question_context)
        else:
            return self._build_interpretation_question_instructions(question_context)

    def _build_operator_extraction_question_instructions(self, question_context: Dict[str, Any]) -> str:
        """Build instructions for Priority 1: Operator Extraction questions."""
        missing_count = question_context.get('missing_count', 0)
        missing_with_desc = question_context.get('missing_with_descriptions', [])
        prioritized = question_context.get('prioritized_missing', [])

        # Format the missing operators list (show top 15)
        missing_list = '\n'.join(f"  - {desc}" for desc in missing_with_desc[:15])
        if len(missing_with_desc) > 15:
            missing_list += f"\n  ... and {len(missing_with_desc) - 15} more"

        return f"""
### FOLLOW-UP QUESTION (MANDATORY) - PRIORITY 1: FACTOR EXTRACTION

**SITUATION:** {missing_count} core inner factors are still missing.

**MISSING FACTORS TO EXTRACT:**
{missing_list}

**YOUR TASK:** Generate a question + 4 answer options designed so that ANY answer
the user chooses reveals values for MAXIMUM missing factors.

**DESIGN REQUIREMENTS:**
1. **Question Bridge:** Create a natural bridge sentence that flows from your response
   into a question about the user's inner experience
2. **4 Mutually Exclusive Options:** Each option represents a DIFFERENT inner state/experience
3. **Maximum Extraction:** Each option, if chosen, should allow extraction of 5-10 different
   factor values (not the same ones across options)
4. **Natural Language:** Use user's domain language, not technical terms
5. **Diagnostic Power:** Options should span the spectrum of possible experiences

**OPTION DESIGN EXAMPLE:**
- Option 1: Represents high clinging + fear-driven state → extracts attachment, fear, resistance values
- Option 2: Represents letting go + trust state → extracts surrender, trust, flow values
- Option 3: Represents analytical detachment → extracts perspective, discernment, balance values
- Option 4: Represents active engagement → extracts intention, energy, presence values

**REMEMBER:** User can only choose ONE answer. Make every option count for extraction."""

    def _build_interpretation_question_instructions(self, question_context: Dict[str, Any]) -> str:
        """Build instructions for Priority 2: Interpretation + Higher Tiers questions."""
        higher_tier_targets = question_context.get('higher_tier_targets', [])
        targets_list = '\n'.join(f"  - {t}" for t in higher_tier_targets)

        return f"""
### FOLLOW-UP QUESTION (MANDATORY) - PRIORITY 2: INTERPRETATION + HIGHER TIERS

**SITUATION:** All 25 core factors are available. Now we need:
1. User's interpretation of the insights shared
2. Data to calculate higher-tier derived values

**HIGHER-TIER CALCULATIONS NEEDED:**
{targets_list}

**YOUR TASK:** Generate a question + 4 answer options that reveal:
- How the user relates to/interprets what you've shared
- Information to refine inner state calculations

**DESIGN REQUIREMENTS:**
1. **Question Bridge:** Natural transition asking how insights landed/resonate
2. **4 Interpretation Modes:** Each option represents a different way of receiving the response
3. **Calculation Value:** Each option should map to different higher-tier configurations
4. **Validation:** Options help validate whether the articulation hit the mark

**OPTION DESIGN EXAMPLE:**
- Option 1: "This confirms what I sensed but couldn't articulate" → high clarity, low resistance
- Option 2: "This challenges my assumptions in uncomfortable ways" → active processing, ego engagement
- Option 3: "I need to sit with this before I can respond" → integration mode, void tolerance
- Option 4: "This opens possibilities I hadn't considered" → expansion, openness activation

**REMEMBER:** This is about understanding HOW they receive truth, not just WHAT they think."""

    def _build_user_query(self, user_context: UserContext) -> str:
        """Build the user query section"""
        query_text = user_context.goal or user_context.current_situation or 'Transform my situation'
        logger.debug(f"[_build_user_query] query_length={len(query_text)}")
        return f"""## USER'S ORIGINAL QUERY

"{user_context.goal or user_context.current_situation or 'Transform my situation'}"

---

Now generate your response in TWO parts:

1. **FIRST**: Your main articulation - insights, analysis, and guidance
2. **THEN**: The structured JSON data block (===STRUCTURED_DATA_START=== ... ===STRUCTURED_DATA_END===)

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
    domain_language: bool = True,
    search_guidance_data: Optional[dict] = None,
    conversation_context: Optional[dict] = None,
    include_question: bool = True,
    question_context: Optional[Dict[str, Any]] = None
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
        conversation_context: Optional dict with conversation history and files:
            {
                "messages": [{"role": "user"|"assistant", "content": "..."}],
                "file_summaries": [{"name": "...", "summary": "...", "type": "..."}],
                "conversation_summary": "..."
            }
    """
    # Build search_guidance from dict if provided
    search_guidance = SearchGuidance()
    if search_guidance_data:
        search_guidance.high_priority_values = search_guidance_data.get('high_priority_values')
        search_guidance.query_pattern = search_guidance_data.get('query_pattern')

        # Build evidence search queries
        for esq in search_guidance_data.get('evidence_search_queries', []):
            if isinstance(esq, dict):
                search_guidance.evidence_search_queries.append(
                    EvidenceSearchQuery(
                        target_value=esq.get('target_value'),
                        search_query=esq.get('search_query'),
                        proof_type=esq.get('proof_type')
                    )
                )

        # Build consciousness-to-reality mappings
        for crm in search_guidance_data.get('consciousness_to_reality_mappings', []):
            if isinstance(crm, dict):
                search_guidance.consciousness_to_reality_mappings.append(
                    ConsciousnessRealityMapping(
                        consciousness_value=crm.get('consciousness_value'),
                        observable_reality=crm.get('observable_reality'),
                        proof_search=crm.get('proof_search')
                    )
                )

    # Build conversation history context if provided
    conv_history_context = None
    if conversation_context:
        conv_history_context = ConversationHistoryContext(
            messages=conversation_context.get('messages', []),
            file_summaries=conversation_context.get('file_summaries', []),
            conversation_summary=conversation_context.get('conversation_summary'),
            question_answers=conversation_context.get('question_answers', []),
            matrix_state=conversation_context.get('matrix_state')
        )
        msg_count = len(conv_history_context.messages)
        file_count = len(conv_history_context.file_summaries)
        qa_count = len(conv_history_context.question_answers)
        has_matrix = conv_history_context.matrix_state is not None
        logger.info(f"[ARTICULATION_CONTEXT] Conversation context: {msg_count} messages, {file_count} files, {qa_count} answered questions, matrix={'yes' if has_matrix else 'no'}")

    logger.info(
        f"[ARTICULATION_CONTEXT] Building context: domain={domain} "
        f"goal='{goal[:60]}...' "
        f"search_guidance={'present' if search_guidance_data else 'None'} "
        f"web_research={'yes' if web_research_summary else 'no'}"
    )
    logger.debug(
        f"[ARTICULATION_CONTEXT] State: S-level={consciousness_state.tier1.s_level.current} "
        f"bottlenecks={len(consciousness_state.bottlenecks)} "
        f"leverage_points={len(consciousness_state.leverage_points)} "
        f"unity_metrics={'present' if consciousness_state.unity_metrics else 'None'}"
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
            domain_language=domain_language,
            insight_priorities=[
                "structural_gaps",
                "bottlenecks",
                "leverage_points",
                "transformation_pathway"
            ]
        ),
        search_guidance=search_guidance,
        conversation_context=conv_history_context,
        include_question=include_question,
        question_context=question_context
    )
