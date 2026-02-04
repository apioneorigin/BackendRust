"""
Tests for Prompt Concealment in articulation_prompt_builder.py.

Validates that framework terminology is properly concealed in generated prompts.
"""

import pytest
from articulation_prompt_builder import ArticulationPromptBuilder
from consciousness_state import (
    ArticulationContext, ConsciousnessState, UserContext, WebResearch,
    ArticulationInstructions, SearchGuidance,
    Tier1Values, Tier2Values, Tier3Values, Tier4Values, Tier5Values,
    CoreOperators, SLevel, Gunas, FiveActs, Chakras, DrivesInternalization,
    TransformationMatrices, DeathArchitecture, CoherenceMetrics,
    BreakthroughDynamics, PipelineFlow, GraceMechanics, PomdpGaps,
    TimelinePredictions, TransformationVectors,
)


def create_minimal_consciousness_state() -> ConsciousnessState:
    """Create a minimal consciousness state for testing."""
    return ConsciousnessState(
        tier1=Tier1Values(
            core_operators=CoreOperators(
                P_presence=0.7,
                A_aware=0.6,
                M_maya=0.3,
                At_attachment=0.4,
                G_grace=0.5,
                W_witness=0.6,
                S_surrender=0.5,
                Co_coherence=0.7,
                R_resistance=0.3,
                F_fear=0.2,
            ),
            s_level=SLevel(current=3.5, label="S3", transition_rate=0.1),
        ),
        tier2=Tier2Values(
            gunas=Gunas(sattva=0.5, rajas=0.3, tamas=0.2, dominant="sattva"),
            five_acts=FiveActs(
                srishti_creation=0.3,
                sthiti_maintenance=0.4,
                samhara_dissolution=0.1,
                tirodhana_concealment=0.1,
                anugraha_grace=0.1,
                dominant="sthiti_maintenance",
            ),
            chakras=Chakras(
                muladhara=0.6, svadhisthana=0.5, manipura=0.6,
                anahata=0.7, vishuddha=0.5, ajna=0.4, sahasrara=0.3,
            ),
            drives_internalization=DrivesInternalization(
                love_internal_pct=0.6, love_external_pct=0.4,
                peace_internal_pct=0.5, peace_external_pct=0.5,
                freedom_internal_pct=0.4, freedom_external_pct=0.6,
            ),
        ),
        tier3=Tier3Values(
            transformation_matrices=TransformationMatrices(
                truth_position="Seeker", truth_score=0.5,
                love_position="Giver", love_score=0.6,
                power_position="Earner", power_score=0.4,
                freedom_position="Keeper", freedom_score=0.5,
                creation_position="Builder", creation_score=0.5,
                time_position="Present", time_score=0.6,
                death_position="Aware", death_score=0.3,
            ),
            death_architecture=DeathArchitecture(active_process=None, depth=None),
            coherence_metrics=CoherenceMetrics(overall=0.7, fundamental=0.6, specification=0.8),
        ),
        tier4=Tier4Values(
            breakthrough_dynamics=BreakthroughDynamics(
                probability=0.3,
                tipping_point_distance=0.4,
                quantum_jump_prob=0.1,
                operators_at_threshold=[],
            ),
            pipeline_flow=PipelineFlow(flow_rate=0.5, manifestation_time="3-6 months"),
            grace_mechanics=GraceMechanics(availability=0.6, effectiveness=0.5, multiplication_factor=1.5),
            pomdp_gaps=PomdpGaps(reality_gap=0.2, observation_gap=0.3, belief_gap=0.2, severity=0.25),
        ),
        tier5=Tier5Values(
            timeline_predictions=TimelinePredictions(
                to_goal="6-12 months", to_next_s_level="18-24 months", evolution_rate=0.1
            ),
            transformation_vectors=TransformationVectors(
                current_state_summary="Building phase",
                target_state_summary="Integration phase",
                core_shift_required="Release attachment",
                primary_obstacle="Fear of change",
                primary_enabler="Trust capacity",
                leverage_point="Surrender practice",
            ),
        ),
        bottlenecks=[],
        leverage_points=[],
        calculated_values=[],
        non_calculated_question_addressable=[],
        non_calculated_context_addressable=[],
        missing_operator_priority=[],
    )


def create_minimal_context() -> ArticulationContext:
    """Create a minimal articulation context for testing."""
    return ArticulationContext(
        user_context=UserContext(
            identity="Professional",
            domain="Business",
            current_situation="Career transition",
            goal="Find meaningful work",
            constraints=[],
        ),
        web_research=WebResearch(
            searches_performed=[],
            key_facts=[],
            competitive_context=None,
            market_data=None,
            search_guidance=SearchGuidance(),
        ),
        consciousness_state=create_minimal_consciousness_state(),
        instructions=ArticulationInstructions(
            articulation_style="natural",
            domain_language=True,
            insight_priorities=["bottlenecks", "leverage_points"],
        ),
        search_guidance=SearchGuidance(),
        conversation_context=None,
        include_question=False,
        question_context=None,
    )


class TestHeaderConcealment:
    """Test that the header section conceals framework terminology."""

    def test_no_consciousness_articulation_in_header(self):
        """Header should use 'INSIGHT ARTICULATION' not 'CONSCIOUSNESS ARTICULATION'."""
        builder = ArticulationPromptBuilder()
        header = builder._build_header()
        assert "CONSCIOUSNESS ARTICULATION" not in header
        assert "INSIGHT ARTICULATION" in header

    def test_no_oof_in_header(self):
        """Header should not mention 'One Origin Framework' or 'OOF'."""
        builder = ArticulationPromptBuilder()
        header = builder._build_header()
        assert "One Origin Framework" not in header
        assert "OOF" not in header

    def test_no_conceal_instruction_in_header(self):
        """Header should not mention 'CONCEAL' as explicit instruction."""
        builder = ArticulationPromptBuilder()
        header = builder._build_header()
        assert "CONCEAL" not in header
        assert "Never say" not in header


class TestFrameworkSectionConcealment:
    """Test that the framework section conceals terminology."""

    def test_no_consciousness_values_in_framework_section(self):
        """Framework section should use 'inner state values' not 'consciousness values'."""
        builder = ArticulationPromptBuilder()
        section = builder._build_framework_section()
        assert "consciousness values" not in section
        assert "inner state values" in section

    def test_no_s_level_in_framework_section(self):
        """Framework section should use 'growth phase' not 'S-level'."""
        builder = ArticulationPromptBuilder()
        section = builder._build_framework_section()
        assert "S-level" not in section
        assert "growth phase" in section

    def test_no_death_architecture_in_framework_section(self):
        """Framework section should use 'dissolution patterns' not 'death architecture'."""
        builder = ArticulationPromptBuilder()
        section = builder._build_framework_section()
        assert "death architecture" not in section
        assert "dissolution patterns" in section


class TestConsciousnessStateSectionConcealment:
    """Test that the consciousness state section conceals terminology."""

    def test_section_header_concealed(self):
        """Should use 'CALCULATED INNER STATE' not 'CALCULATED CONSCIOUSNESS STATE'."""
        builder = ArticulationPromptBuilder()
        context = create_minimal_context()
        section = builder._build_consciousness_state_section(context.consciousness_state)
        assert "CONSCIOUSNESS STATE" not in section
        assert "INNER STATE" in section

    def test_s_level_concealed(self):
        """Should use 'Growth Phase' not 'S-Level'."""
        builder = ArticulationPromptBuilder()
        context = create_minimal_context()
        section = builder._build_consciousness_state_section(context.consciousness_state)
        assert "**S-Level:**" not in section
        assert "**Growth Phase:**" in section

    def test_maya_concealed(self):
        """Should use 'Blind spots' not 'Maya (illusion)'."""
        builder = ArticulationPromptBuilder()
        context = create_minimal_context()
        section = builder._build_consciousness_state_section(context.consciousness_state)
        assert "Maya (illusion)" not in section
        assert "Blind spots" in section

    def test_grace_flow_concealed(self):
        """Should use 'Flow and breakthroughs' not 'Grace flow'."""
        builder = ArticulationPromptBuilder()
        context = create_minimal_context()
        section = builder._build_consciousness_state_section(context.consciousness_state)
        assert "Grace flow" not in section
        assert "Flow and breakthroughs" in section

    def test_death_processes_concealed(self):
        """Should use 'Active Dissolution Processes' not 'Active Death Processes'."""
        builder = ArticulationPromptBuilder()
        context = create_minimal_context()
        section = builder._build_consciousness_state_section(context.consciousness_state)
        assert "Active Death Processes" not in section
        assert "Active Dissolution Processes" in section

    def test_chakra_concealed(self):
        """Should use 'Energy Centers' not 'Chakra Activation'."""
        builder = ArticulationPromptBuilder()
        context = create_minimal_context()
        section = builder._build_consciousness_state_section(context.consciousness_state)
        assert "Chakra Activation" not in section
        assert "Energy Centers" in section

    def test_grace_mechanics_concealed(self):
        """Should use 'Flow Mechanics' not 'Grace Mechanics'."""
        builder = ArticulationPromptBuilder()
        context = create_minimal_context()
        section = builder._build_consciousness_state_section(context.consciousness_state)
        assert "Grace Mechanics" not in section
        assert "Flow Mechanics" in section

    def test_pomdp_concealed(self):
        """Should use 'Reality Perception Gaps' not 'POMDP Gaps'."""
        builder = ArticulationPromptBuilder()
        context = create_minimal_context()
        section = builder._build_consciousness_state_section(context.consciousness_state)
        assert "POMDP Gaps" not in section
        assert "Reality Perception Gaps" in section

    def test_operators_concealed(self):
        """Should use 'Key Factors' not 'Key Operators'."""
        builder = ArticulationPromptBuilder()
        context = create_minimal_context()
        section = builder._build_consciousness_state_section(context.consciousness_state)
        assert "Key Operators" not in section
        assert "Key Factors" in section


class TestGenerationInstructionsConcealment:
    """Test that generation instructions conceal terminology."""

    def test_no_consciousness_analysis_in_instructions(self):
        """Should use 'deep pattern analysis' not 'consciousness analysis'."""
        builder = ArticulationPromptBuilder()
        context = create_minimal_context()
        section = builder._build_generation_instructions(context.instructions)
        assert "consciousness analysis" not in section
        assert "deep pattern analysis" in section

    def test_no_consciousness_patterns_in_instructions(self):
        """Should use 'inner patterns' not 'consciousness patterns'."""
        builder = ArticulationPromptBuilder()
        context = create_minimal_context()
        section = builder._build_generation_instructions(context.instructions)
        assert "consciousness patterns" not in section.lower()
        assert "inner patterns" in section.lower()

    def test_no_consciousness_state_in_instructions(self):
        """Should use 'inner state' not 'consciousness state' in instructions."""
        builder = ArticulationPromptBuilder()
        context = create_minimal_context()
        section = builder._build_generation_instructions(context.instructions)
        assert "consciousness state" not in section
        assert "inner state" in section


class TestFullPromptConcealment:
    """Test that the full prompt conceals all framework terminology."""

    def test_full_prompt_no_framework_terms(self):
        """Full prompt should not contain any framework-specific terms."""
        builder = ArticulationPromptBuilder()
        context = create_minimal_context()
        prompt = builder.build_prompt(context)

        # Framework terms that should NOT appear
        forbidden_terms = [
            "One Origin Framework",
            "OOF",
            "Maya operator",
            "Maya (illusion)",
            "S-Level:",
            "Chakra Activation",
            "Grace flow:",
            "Grace Mechanics:",
            "POMDP Gaps",
            "Active Death Processes",
            "Death Architecture",
            "CONSCIOUSNESS ARTICULATION",
            "consciousness values",
            "consciousness analysis",
        ]

        for term in forbidden_terms:
            assert term not in prompt, f"Found forbidden term in prompt: {term}"

    def test_full_prompt_has_concealed_terms(self):
        """Full prompt should contain the properly concealed terms."""
        builder = ArticulationPromptBuilder()
        context = create_minimal_context()
        prompt = builder.build_prompt(context)

        # Concealed terms that SHOULD appear
        expected_terms = [
            "INSIGHT ARTICULATION",
            "inner state",
            "Growth Phase",
            "Energy Centers",
            "Flow Mechanics",
            "Reality Perception Gaps",
            "Key Factors",
            "deep pattern analysis",
        ]

        for term in expected_terms:
            assert term in prompt, f"Missing expected concealed term: {term}"
