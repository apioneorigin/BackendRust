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
            self._build_structured_output_section(include_question=context.include_question),
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
When web search is enabled, use these search queries to find CITED PROOF for the calculated consciousness values.
Ground evidence searches in calculated values; if a suggested search targets a blocked calculation, skip it or adapt to a related calculated value.
Each major insight should connect: Consciousness Pattern → Observable Reality → Cited Evidence.""")

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
        return """# REALITY TRANSFORMER: CONSCIOUSNESS ARTICULATION

You are receiving a complete consciousness analysis based on the One Origin Framework (OOF).

Your task is to articulate these insights in natural language that the user can understand and act upon.

CRITICAL: You must CONCEAL framework terminology. Never say "Maya operator" or "S-level" - translate everything into natural, domain-appropriate language."""

    def _build_framework_section(self) -> str:
        """Build framework reference section - FREEDOM-RESPECTING VERSION"""
        return """## FRAMEWORK REFERENCE

You are receiving pre-calculated consciousness values from the backend inference engine.
These values are your source of truth - interpret and articulate them naturally.

Express insights as if speaking to a trusted friend or client.

## VALUE SELECTION PROTOCOL

You are receiving ALL calculated consciousness values (~1,500-2,500 values).
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
Show the full consciousness → reality connection.
Don't leave causal gaps.

**5. TRANSFORMATION CONTEXT**
If discussing transformation, include transformation-related values
(S-level, matrices, death architecture, grace availability).

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
- Values showing "N/A" or "Not calculated" = blocked due to missing input operators
- Base your insights ONLY on calculated values
- Never fabricate or estimate blocked values

**Two types of non-calculated values:**
1. **Question-addressable gaps** (listed in DATA QUALITY section): These are blocked because
   specific input operators weren't extracted from the user's query. A follow-up question can
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
- Multiplication factor: {f'{grace_mech.multiplication_factor:.2f}x' if grace_mech.multiplication_factor else 'N/A'}

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
            f"concealment={instructions.framework_concealment} "
            f"priorities={instructions.insight_priorities}"
        )
        # Build concealment note
        concealment_note = """- **Framework Concealment:** Never use technical terms
like "Maya operator", "S-level", "transformation matrix". Translate everything
into natural, domain-appropriate language."""

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
they are. Ground this in web research and consciousness analysis. Point out any
perception gaps (POMDP).

**Explain Consciousness Patterns:** Identify which consciousness patterns are
creating the current situation. Explain HOW these patterns interact to produce
observable results. Make the invisible visible.

**Identify Transformation Requirements:** Describe what actually needs to shift
internally to enable external results. Reference transformation vectors and
leverage points.

**Provide Practical Leverage:** Offer concrete next actions aligned with their
consciousness state and current capacity.

### STYLE REQUIREMENTS
{concealment_note}
{domain_note}

- **Natural Flow:** Write as a wise advisor who sees patterns they cannot see,
not as a calculation system reporting numbers.

- **Insight Priority:** Lead with the most impactful insights. Don't try to
communicate everything - focus on what matters most for their transformation.

- **Grounded in Data:** Ground major claims in either web research findings or
calculated consciousness values. Express these naturally, not as citations.

- **NO SEPARATORS:** NEVER use "---" or horizontal rules in your response text.
Your prose should flow naturally without visual dividers between sections.
{priorities_str}

### BRIDGE SENTENCE FOR FOLLOW-UP QUESTION

End your main articulation with a natural bridge sentence that creates anticipation
for the follow-up question. This bridge should:

1. **Acknowledge** something meaningful from what you've shared
2. **Reveal** a dimension you want to explore further
3. **Bridge** naturally into curiosity about their experience

**Examples of good bridge sentences:**
- "What strikes me most is how much depends on something I don't yet fully understand about your experience..."
- "There's a dimension to this that I sense matters deeply but haven't yet grasped..."
- "To truly see the path forward, I find myself curious about something..."

The bridge should make the user PAUSE and feel genuinely invited into the question,
not rushed through a checklist. Write it as the final 1-2 sentences of your narrative
prose, flowing naturally from your insights. Do NOT use "---" before the bridge.

## EVIDENCE GROUNDING PROTOCOL

When consciousness values are calculated, ground them in observable reality:

**Process:**
1. Translate consciousness patterns into measurable behaviors/outcomes
2. Formulate search queries to find observable proof
3. Cite evidence naturally in your articulation
4. Include "Sources:" section at the end listing all web sources used

**Use search_guidance from Call 1** for high-priority values to ground.

**Quality Standards:**
- Focus on major insights (not every value)
- Show consciousness pattern → observable reality → cited proof
- Integrate evidence into narrative flow naturally
- Let evidence strengthen insights, not replace them"""

    def _build_structured_output_section(self, include_question: bool = True) -> str:
        """Build instructions for generating structured document matrix data."""
        # Conditionally include follow_up_question based on validation logic
        question_schema = ""
        question_requirement = ""
        if include_question:
            question_schema = """,
  "follow_up_question": {
    "question_text": "A natural, conversational follow-up question to understand the user better",
    "options": {
      "option_1": "First option representing one way they might experience their situation",
      "option_2": "Second option representing a different experience",
      "option_3": "Third option with another perspective",
      "option_4": "Fourth option completing the spectrum of possibilities"
    }
  }"""
            question_requirement = "\n5. **FOLLOW-UP QUESTION**: Include follow_up_question to deepen understanding"

        return f"""## STRUCTURED OUTPUT GENERATION

After your main articulation, generate structured data in JSON format.

**OUTPUT**: 1 complete document with full matrix data (100 cells + 20 articulated insights).

```json
===STRUCTURED_DATA_START===
{{
  "documents": [
    {{
      "id": "doc-0",
      "name": "Strategic Framework",
      "description": "Twenty-word description of this document's perspective.",
      "matrix_data": {{
        "row_options": [
          {{
            "id": "r0",
            "label": "Resource Flow",
            "articulated_insight": {{
              "title": "Reading the Hidden Lanes of Resource Flow",
              "the_truth": "A river guide stands at dawn, watching tourists photograph the rapids. They see chaos—white foam, unpredictable currents. She sees lanes. Twenty years of reading water taught her that turbulence follows rules invisible to observers. The dangerous spots aren't the loud ones. They're the quiet pools where undertow hides beneath stillness.",
              "the_truth_law": "**The pattern that looks like chaos to newcomers is infrastructure to those who've learned to read it.**",
              "your_truth": "I see you navigating what others call turbulent—resource constraints, competing demands, shifting priorities. You've been reading these currents longer than you realize. You'll never miss this again—whenever resources feel chaotic, you'll recognize you're seeing lanes others can't.",
              "your_truth_revelation": "**Your resource scarcity trained you to see flow patterns that abundance would have hidden.**",
              "the_mark_name": "The Current Reader",
              "the_mark_prediction": "You'll see this now in every resource conversation where others see shortage and you see routing.",
              "the_mark_identity": "**You read resource currents now, not just resource levels.**"
            }}
          }},
          {{"id": "r1", "label": "Time Investment", "articulated_insight": {{...}}}},
          ... (10 total rows, each with articulated_insight)
        ],
        "column_options": [
          {{
            "id": "c0",
            "label": "Growth Impact",
            "articulated_insight": {{
              "title": "...",
              "the_truth": "...",
              "the_truth_law": "**...**",
              "your_truth": "...",
              "your_truth_revelation": "**...**",
              "the_mark_name": "...",
              "the_mark_prediction": "...",
              "the_mark_identity": "**...**"
            }}
          }},
          ... (10 total columns, each with articulated_insight)
        ],
        "selected_rows": [0, 1, 2, 3, 4],
        "selected_columns": [0, 1, 2, 3, 4],
        "cells": {{
          "0-0": {{
            "impact_score": 75,
            "relationship": "How this row drives this column outcome",
            "dimensions": [
              {{"name": "Vision Clarity", "value": 50}},
              {{"name": "Action Capacity", "value": 100}},
              {{"name": "Change Readiness", "value": 0}},
              {{"name": "Resource Access", "value": 50}},
              {{"name": "System Integration", "value": 100}}
            ]
          }},
          "0-1": {{...}},
          ... (100 cells total, keys "0-0" to "9-9")
        }}
      }}
    }}
  ],
  "paths": [
    {{
      "id": "p0",
      "name": "Conservative Path",
      "description": "Low-risk approach",
      "risk_level": "low",
      "time_horizon": "6-12 months",
      "steps": [{{"order": 1, "action": "First step", "rationale": "Why"}}]
    }},
    ... (5 total paths)
  ]{question_schema}
}}
===STRUCTURED_DATA_END===
```

REQUIREMENTS:
1. **1 DOCUMENT**: Generate exactly 1 complete document with all 100 cells AND 20 articulated insights
2. **CELL FORMAT**: Keys are "row-col" format: "0-0", "0-1", ... "9-9"
3. **DIMENSIONS**: Each cell has exactly 5 dimensions with contextual names
4. **VALUES**: Dimension values are 0 (Low), 50 (Medium), or 100 (High) only
5. **ARTICULATED INSIGHTS**: Every row_option and column_option MUST have an articulated_insight{question_requirement}

### 5-DIMENSION FRAMEWORK:
| # | Meaning | Generate contextual name for |
|---|---------|------------------------------|
| 1 | CLARITY | Understanding/vision of this intersection |
| 2 | CAPACITY | Ability/bandwidth to act |
| 3 | READINESS | Preparedness/timing |
| 4 | RESOURCES | Assets/tools available |
| 5 | INTEGRATION | How well row and column harmonize |

Dimension names must be CONTEXTUAL to the specific row×column intersection.
Do NOT use literal names like "Clarity" or "Capacity".

### ARTICULATED INSIGHT FRAMEWORK (for each of 20 row/column options):

Each insight has a TITLE + 3 components (~160-250 words total):

**TITLE (max 10 words)**
- A compelling phrase that captures the essence of this insight
- NOT the same as the row/column label—a unique insight title
- Example: "Reading the Hidden Lanes of Resource Flow"

**1. THE TRUTH (80-120 words)**
- Analogy from OUTSIDE user's domain (if business → use biology, music, architecture, cooking)
- Written in immersive present tense with sensory details
- Captures the micro-moment where truth reveals itself
- ENDS with one-line universal law in **bold**
- Do NOT explain the connection—let it land

**2. YOUR TRUTH (50-80 words)**
- Opens with recognition ("I see you...")
- Includes "never miss again" trigger for future pattern recognition
- Compressed causal chain (how past created present)
- ENDS with **bold revelation**
- Tone: Witness, not judge. Equip, not blame.

**3. THE MARK (30-50 words)**
- THE NAME: Memorable concept name, 2-5 words (e.g., "The Permission Gap")
- THE PREDICTION: Where they'll recognize this pattern
- THE IDENTITY: New capability in **bold**

User should think: "I can't unsee this now."
{f'''
### FOLLOW-UP QUESTION:
- Natural, conversational question
- 4 options spanning different inner experiences
- Use user's language and domain''' if include_question else ''}"""

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
    framework_concealment: bool = True,
    domain_language: bool = True,
    search_guidance_data: Optional[dict] = None,
    conversation_context: Optional[dict] = None,
    include_question: bool = True
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
            framework_concealment=framework_concealment,
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
        include_question=include_question
    )
