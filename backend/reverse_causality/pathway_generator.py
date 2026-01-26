"""
Pathway Generator
Generates 3-5 viable transformation pathways from current state to desired state

Each pathway represents a different strategy:
1. Direct Path - Fastest but potentially unstable
2. Gradual Path - Slower but stable evolution
3. Grace Path - High surrender, relies on grace activation
4. Effort Path - Disciplined practice-based approach
5. Hybrid Path - Balanced combination

Pathways respect:
- Sacred Chain constraints (can't skip S-levels)
- Energy sustainability
- Fractal coherence requirements (85% minimum)
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import math

from logging_config import get_logger
logger = get_logger('reverse_causality.pathways')


@dataclass
class PathwayStep:
    """A single step in a transformation pathway"""
    order: int
    operator_changes: Dict[str, Tuple[float, float]]  # operator -> (current, target)
    description: str
    duration_estimate: str  # "days", "weeks", "months"
    energy_required: float  # 0-1
    difficulty: float  # 0-1
    practices: List[str]  # Recommended practices
    indicators: List[str]  # Signs of progress


@dataclass
class TransformationPathway:
    """Complete transformation pathway"""
    id: str
    name: str
    strategy: str  # "direct", "gradual", "grace", "effort", "hybrid"
    description: str

    steps: List[PathwayStep]

    total_duration_estimate: str
    overall_difficulty: float
    stability_score: float  # 0-1, higher = more stable
    grace_dependency: float  # 0-1, higher = more grace-dependent
    effort_required: float  # 0-1

    side_effects: List[str]  # Potential side effects
    risks: List[str]  # Potential risks
    benefits: List[str]  # Unique benefits of this path

    success_probability: float
    recommended_for: List[str]  # Personality types / situations


class PathwayGenerator:
    """
    Generate multiple viable pathways between consciousness states.
    """

    # Pathway archetypes
    PATHWAY_TYPES = {
        'direct': {
            'name': 'Direct Transformation',
            'description': 'Fastest path with aggressive operator changes',
            'stability': 0.5,
            'grace_dependency': 0.3,
            'effort': 0.8,
            'recommended_for': ['high energy', 'urgent need', 'experienced practitioners']
        },
        'gradual': {
            'name': 'Gradual Evolution',
            'description': 'Slow, stable progression with small incremental changes',
            'stability': 0.9,
            'grace_dependency': 0.3,
            'effort': 0.5,
            'recommended_for': ['beginners', 'those valuing stability', 'sustainable change']
        },
        'grace': {
            'name': 'Grace-Centered Path',
            'description': 'Relies on surrender and grace activation for transformation',
            'stability': 0.7,
            'grace_dependency': 0.9,
            'effort': 0.4,
            'recommended_for': ['spiritually oriented', 'high surrender capacity', 'stuck on effort']
        },
        'effort': {
            'name': 'Disciplined Practice Path',
            'description': 'Systematic practice-based transformation',
            'stability': 0.8,
            'grace_dependency': 0.2,
            'effort': 0.9,
            'recommended_for': ['disciplined types', 'structured approach', 'action-oriented']
        },
        'hybrid': {
            'name': 'Balanced Hybrid Path',
            'description': 'Combines effort and surrender for balanced transformation',
            'stability': 0.75,
            'grace_dependency': 0.5,
            'effort': 0.6,
            'recommended_for': ['most people', 'balanced approach', 'flexible practitioners']
        }
    }

    # Practices mapped to operator changes
    OPERATOR_PRACTICES = {
        'P_presence': ['meditation', 'mindfulness', 'breath awareness', 'body scanning'],
        'A_aware': ['self-inquiry', 'journaling', 'therapy', 'shadow work'],
        'W_witness': ['meditation', 'witness meditation', 'observing thoughts'],
        'I_intention': ['goal setting', 'visualization', 'affirmations', 'clarity exercises'],
        'At_attachment': ['letting go practices', 'non-attachment meditation', 'cleaning'],
        'Se_service': ['selfless service', 'volunteering', 'acts of kindness'],
        'G_grace': ['prayer', 'surrender practice', 'transmission', 'satsang'],
        'S_surrender': ['surrender meditation', 'trust exercises', 'letting go'],
        'D_dharma': ['purpose exploration', 'values clarification', 'life mission work'],
        'Co_coherence': ['heart coherence', 'HeartMath', 'coherent breathing'],
        'F_fear': ['fear processing', 'exposure therapy', 'courage practices'],
        'R_resistance': ['acceptance practice', 'flow exercises', 'yielding practice'],
        'O_openness': ['new experiences', 'curiosity cultivation', 'beginner mind'],
        'J_joy': ['gratitude practice', 'celebration', 'play', 'nature immersion'],
        'V_void': ['void meditation', 'emptiness practice', 'silence retreats'],
        'Sh_shakti': ['energy practices', 'yoga', 'breathwork', 'movement'],
        'Ce_cleaning': ['cleaning practice', 'morning meditation', 'evening review'],
        'Hf_habit': ['habit disruption', 'pattern interrupts', 'new routines'],
        'E_equanimity': ['equanimity meditation', 'non-reactivity practice'],
        'Tr_trust': ['trust exercises', 'vulnerability practice', 'faith cultivation'],
        'K_karma': ['karma yoga', 'selfless action', 'cleaning', 'grace invocation'],
        'M_maya': ['reality inquiry', 'illusion piercing', 'truth seeking'],
    }

    def __init__(self):
        pass

    def generate_pathways(
        self,
        current_operators: Dict[str, float],
        required_operators: Dict[str, float],
        current_s_level: float,
        target_s_level: float,
        constraints: Optional[Dict[str, Any]] = None,
        num_pathways: int = 5
    ) -> List[TransformationPathway]:
        """
        Generate multiple viable pathways from current to required state.

        Args:
            current_operators: Current Tier 1 operator values
            required_operators: Required Tier 1 operator values
            current_s_level: Current S-level
            target_s_level: Target S-level (optional, inferred if not given)
            constraints: Optional constraints on the pathway
            num_pathways: Number of pathways to generate (1-5)

        Returns:
            List of TransformationPathway objects
        """
        logger.debug(f"[generate_pathways] outcome operators={len(current_operators)} num_pathways={num_pathways}")
        pathways = []

        # Calculate total gap
        total_gap = self._calculate_gap(current_operators, required_operators)
        s_level_gap = target_s_level - current_s_level

        # Generate each pathway type
        pathway_types = ['direct', 'gradual', 'grace', 'effort', 'hybrid']

        for i, ptype in enumerate(pathway_types[:num_pathways]):
            pathway = self._generate_pathway(
                pathway_type=ptype,
                current_operators=current_operators,
                required_operators=required_operators,
                total_gap=total_gap,
                s_level_gap=s_level_gap,
                constraints=constraints,
                pathway_index=i
            )
            pathways.append(pathway)

        logger.debug(f"[generate_pathways] result: {len(pathways)} pathways generated")
        return pathways

    def _generate_pathway(
        self,
        pathway_type: str,
        current_operators: Dict[str, float],
        required_operators: Dict[str, float],
        total_gap: float,
        s_level_gap: float,
        constraints: Optional[Dict[str, Any]],
        pathway_index: int
    ) -> TransformationPathway:
        """
        Generate a single pathway of a specific type.
        """
        logger.debug(f"[_generate_pathway] type={pathway_type} gap={total_gap:.3f} s_gap={s_level_gap:.3f}")
        config = self.PATHWAY_TYPES[pathway_type]

        # Determine step count based on pathway type
        if pathway_type == 'direct':
            num_steps = max(2, int(total_gap * 3))
        elif pathway_type == 'gradual':
            num_steps = max(4, int(total_gap * 8))
        else:
            num_steps = max(3, int(total_gap * 5))

        num_steps = min(num_steps, 7)  # Cap at 7 steps

        # Generate steps
        steps = self._generate_steps(
            pathway_type=pathway_type,
            current_operators=current_operators,
            required_operators=required_operators,
            num_steps=num_steps
        )

        # Calculate total duration
        total_duration = self._estimate_total_duration(steps, pathway_type)

        # Calculate success probability
        success_prob = self._calculate_success_probability(
            pathway_type=pathway_type,
            total_gap=total_gap,
            s_level_gap=s_level_gap,
            num_steps=num_steps
        )

        # Generate side effects, risks, benefits
        side_effects = self._identify_side_effects(pathway_type, required_operators)
        risks = self._identify_risks(pathway_type, total_gap, s_level_gap)
        benefits = self._identify_benefits(pathway_type)

        return TransformationPathway(
            id=f"pathway_{pathway_type}_{pathway_index}",
            name=config['name'],
            strategy=pathway_type,
            description=config['description'],
            steps=steps,
            total_duration_estimate=total_duration,
            overall_difficulty=sum(s.difficulty for s in steps) / len(steps),
            stability_score=config['stability'],
            grace_dependency=config['grace_dependency'],
            effort_required=config['effort'],
            side_effects=side_effects,
            risks=risks,
            benefits=benefits,
            success_probability=success_prob,
            recommended_for=config['recommended_for']
        )

    def _generate_steps(
        self,
        pathway_type: str,
        current_operators: Dict[str, float],
        required_operators: Dict[str, float],
        num_steps: int
    ) -> List[PathwayStep]:
        """
        Generate the steps for a pathway.
        """
        logger.debug(f"[_generate_steps] type={pathway_type} num_steps={num_steps}")
        steps = []

        # Calculate changes needed for each operator
        changes_needed = {}
        for op, req_val in required_operators.items():
            curr_val = current_operators.get(op)
            if curr_val is None:
                continue
            if abs(req_val - curr_val) > 0.05:
                changes_needed[op] = (curr_val, req_val)

        # Sort by priority based on pathway type
        sorted_ops = self._prioritize_operators(changes_needed, pathway_type)

        # Distribute changes across steps
        ops_per_step = max(1, len(sorted_ops) // num_steps)

        current_state = current_operators.copy()

        for step_idx in range(num_steps):
            # Select operators for this step
            start_idx = step_idx * ops_per_step
            end_idx = start_idx + ops_per_step

            if step_idx == num_steps - 1:
                # Last step gets remaining operators
                step_ops = sorted_ops[start_idx:]
            else:
                step_ops = sorted_ops[start_idx:end_idx]

            if not step_ops:
                continue

            # Calculate changes for this step
            step_changes = {}
            for op in step_ops:
                curr_val, req_val = changes_needed[op]

                # Interpolate based on step and pathway type
                if pathway_type == 'direct':
                    # Larger changes per step
                    progress = min(1.0, (step_idx + 1) / num_steps * 1.3)
                elif pathway_type == 'gradual':
                    # Smaller, more even changes
                    progress = (step_idx + 1) / num_steps
                elif pathway_type == 'grace':
                    # Back-loaded (grace activates later)
                    progress = ((step_idx + 1) / num_steps) ** 0.7
                else:
                    # Linear
                    progress = (step_idx + 1) / num_steps

                target_val = curr_val + (req_val - curr_val) * progress
                step_changes[op] = (current_state.get(op, curr_val), target_val)

                # Update current state for next step
                current_state[op] = target_val

            # Determine step characteristics
            difficulty = self._calculate_step_difficulty(step_changes, pathway_type)
            duration = self._estimate_step_duration(step_changes, pathway_type)
            energy = self._calculate_energy_required(step_changes, pathway_type)
            practices = self._get_practices_for_step(step_changes, pathway_type)
            indicators = self._get_indicators_for_step(step_changes)
            description = self._generate_step_description(step_changes, step_idx, pathway_type)

            steps.append(PathwayStep(
                order=step_idx + 1,
                operator_changes=step_changes,
                description=description,
                duration_estimate=duration,
                energy_required=energy,
                difficulty=difficulty,
                practices=practices,
                indicators=indicators
            ))

        return steps

    def _prioritize_operators(
        self,
        changes_needed: Dict[str, Tuple[float, float]],
        pathway_type: str
    ) -> List[str]:
        """
        Prioritize operators based on pathway type.
        """
        # Define priority groups for different pathway types
        priorities = {
            'direct': {
                'first': ['I_intention', 'Co_coherence', 'At_attachment', 'R_resistance'],
                'second': ['A_aware', 'W_witness', 'F_fear', 'M_maya'],
                'third': ['G_grace', 'S_surrender', 'V_void']
            },
            'gradual': {
                'first': ['P_presence', 'A_aware', 'O_openness'],
                'second': ['At_attachment', 'F_fear', 'R_resistance'],
                'third': ['G_grace', 'S_surrender', 'W_witness']
            },
            'grace': {
                'first': ['S_surrender', 'G_grace', 'O_openness'],
                'second': ['At_attachment', 'R_resistance', 'Tr_trust'],
                'third': ['V_void', 'Ce_cleaning', 'Se_service']
            },
            'effort': {
                'first': ['I_intention', 'Sh_shakti', 'D_dharma'],
                'second': ['Hf_habit', 'A_aware', 'Co_coherence'],
                'third': ['At_attachment', 'R_resistance', 'F_fear']
            },
            'hybrid': {
                'first': ['A_aware', 'I_intention', 'S_surrender'],
                'second': ['At_attachment', 'Co_coherence', 'G_grace'],
                'third': ['W_witness', 'V_void', 'R_resistance']
            }
        }

        logger.debug(f"[_prioritize_operators] type={pathway_type} changes={len(changes_needed)}")
        priority_map = priorities.get(pathway_type, priorities['hybrid'])

        # Sort operators by priority and change magnitude
        sorted_ops = []

        for priority_level in ['first', 'second', 'third']:
            level_ops = []
            for op in priority_map[priority_level]:
                if op in changes_needed:
                    curr, req = changes_needed[op]
                    magnitude = abs(req - curr)
                    level_ops.append((op, magnitude))

            # Sort within level by magnitude
            level_ops.sort(key=lambda x: -x[1])
            sorted_ops.extend([op for op, _ in level_ops])

        # Add any remaining operators
        for op in changes_needed:
            if op not in sorted_ops:
                sorted_ops.append(op)

        return sorted_ops

    def _calculate_step_difficulty(
        self,
        changes: Dict[str, Tuple[float, float]],
        pathway_type: str
    ) -> float:
        """
        Calculate difficulty of a step.
        """
        # Operator difficulty weights
        difficult_ops = {
            'At_attachment': 0.8, 'K_karma': 0.8, 'G_grace': 0.7,
            'V_void': 0.7, 'S_surrender': 0.7, 'Hf_habit': 0.6,
            'F_fear': 0.6, 'M_maya': 0.6
        }

        total_difficulty = 0
        for op, (curr, target) in changes.items():
            change_mag = abs(target - curr)
            op_difficulty = difficult_ops.get(op)
            if op_difficulty is None:
                continue
            total_difficulty += change_mag * op_difficulty

        # Normalize
        avg_difficulty = total_difficulty / max(1, len(changes))

        # Adjust for pathway type
        if pathway_type == 'direct':
            avg_difficulty *= 1.2
        elif pathway_type == 'gradual':
            avg_difficulty *= 0.7

        result = min(1.0, avg_difficulty)
        logger.debug(f"[_calculate_step_difficulty] result: {result:.3f}")
        return result

    def _estimate_step_duration(
        self,
        changes: Dict[str, Tuple[float, float]],
        pathway_type: str
    ) -> str:
        """
        Estimate duration for a step.
        """
        total_change = sum(abs(t - c) for c, t in changes.values())

        # Base duration in days
        base_days = total_change * 30

        # Adjust for pathway type
        if pathway_type == 'direct':
            days = base_days * 0.6
        elif pathway_type == 'gradual':
            days = base_days * 1.5
        elif pathway_type == 'grace':
            days = base_days * 0.8
        else:
            days = base_days

        if days < 7:
            result = "days"
        elif days < 30:
            result = "weeks"
        elif days < 90:
            result = "1-2 months"
        else:
            result = "months"
        logger.debug(f"[_estimate_step_duration] result: {result} (days={days:.1f})")
        return result

    def _calculate_energy_required(
        self,
        changes: Dict[str, Tuple[float, float]],
        pathway_type: str
    ) -> float:
        """
        Calculate energy required for a step.
        """
        total_change = sum(abs(t - c) for c, t in changes.values())

        energy = total_change * 0.5

        if pathway_type == 'effort':
            energy *= 1.3
        elif pathway_type == 'grace':
            energy *= 0.7

        return min(1.0, energy)

    def _get_practices_for_step(
        self,
        changes: Dict[str, Tuple[float, float]],
        pathway_type: str
    ) -> List[str]:
        """
        Get recommended practices for a step.
        """
        practices = set()

        for op in changes:
            op_practices = self.OPERATOR_PRACTICES.get(op, [])
            # Add 1-2 practices per operator
            for practice in op_practices[:2]:
                practices.add(practice)

        # Add pathway-specific practices
        if pathway_type == 'grace':
            practices.add('prayer')
            practices.add('surrender practice')
        elif pathway_type == 'effort':
            practices.add('daily discipline')
            practices.add('structured routine')
        elif pathway_type == 'gradual':
            practices.add('gentle consistency')
            practices.add('patience practice')

        return list(practices)[:5]

    def _get_indicators_for_step(
        self,
        changes: Dict[str, Tuple[float, float]]
    ) -> List[str]:
        """
        Generate progress indicators for a step.
        """
        indicators = []

        indicator_map = {
            'P_presence': 'Increased present-moment awareness',
            'A_aware': 'Deeper self-understanding',
            'W_witness': 'Ability to observe thoughts without identification',
            'I_intention': 'Clearer sense of direction',
            'At_attachment': 'Feeling lighter about outcomes',
            'F_fear': 'Reduced anxiety and worry',
            'R_resistance': 'Greater acceptance of what is',
            'G_grace': 'Synchronicities and unexpected help',
            'S_surrender': 'Sense of being carried',
            'Co_coherence': 'More inner harmony',
            'O_openness': 'Curiosity about new possibilities',
            'J_joy': 'Spontaneous happiness arising',
            'V_void': 'Comfort with not-knowing',
            'Sh_shakti': 'Increased energy and vitality',
            'Se_service': 'Natural desire to help others',
        }

        for op in changes:
            if op in indicator_map:
                indicators.append(indicator_map[op])

        return indicators[:4]

    def _generate_step_description(
        self,
        changes: Dict[str, Tuple[float, float]],
        step_idx: int,
        pathway_type: str
    ) -> str:
        """
        Generate human-readable description for a step.
        """
        # Get main operators being changed
        main_ops = list(changes.keys())[:3]

        op_names = {
            'P_presence': 'presence', 'A_aware': 'awareness',
            'W_witness': 'witness consciousness', 'I_intention': 'intention',
            'At_attachment': 'non-attachment', 'F_fear': 'courage',
            'R_resistance': 'acceptance', 'G_grace': 'grace receptivity',
            'S_surrender': 'surrender', 'Co_coherence': 'coherence',
            'O_openness': 'openness', 'J_joy': 'joy',
            'V_void': 'void tolerance', 'Sh_shakti': 'energy',
            'Se_service': 'service', 'D_dharma': 'purpose alignment',
            'Hf_habit': 'habit transformation', 'Ce_cleaning': 'cleaning practice',
            'K_karma': 'karma release', 'M_maya': 'clarity'
        }

        focus_areas = [op_names.get(op, op) for op in main_ops]

        if pathway_type == 'direct':
            action = "Intensively develop"
        elif pathway_type == 'gradual':
            action = "Gently cultivate"
        elif pathway_type == 'grace':
            action = "Open to"
        elif pathway_type == 'effort':
            action = "Systematically build"
        else:
            action = "Balance and develop"

        return f"Step {step_idx + 1}: {action} {', '.join(focus_areas)}"

    def _estimate_total_duration(
        self,
        steps: List[PathwayStep],
        pathway_type: str
    ) -> str:
        """
        Estimate total pathway duration.
        """
        # Sum step durations
        duration_days = 0

        for step in steps:
            if step.duration_estimate == "days":
                duration_days += 5
            elif step.duration_estimate == "weeks":
                duration_days += 21
            elif step.duration_estimate == "1-2 months":
                duration_days += 45
            else:
                duration_days += 90

        if duration_days < 30:
            return "2-4 weeks"
        elif duration_days < 90:
            return "1-3 months"
        elif duration_days < 180:
            return "3-6 months"
        elif duration_days < 365:
            return "6-12 months"
        else:
            return "1-2 years"

    def _calculate_success_probability(
        self,
        pathway_type: str,
        total_gap: float,
        s_level_gap: float,
        num_steps: int
    ) -> float:
        """
        Calculate success probability for a pathway.
        """
        # Base probability
        base = 0.8

        # Reduce for larger gaps
        gap_factor = 1 - (total_gap * 0.3)

        # S-level gap impact
        s_level_factor = 1 - (s_level_gap * 0.15)

        # Step count impact (more steps = higher success)
        step_factor = 1 + (num_steps * 0.02)

        # Pathway type adjustment
        type_factor = {
            'direct': 0.85,
            'gradual': 1.1,
            'grace': 0.9,
            'effort': 1.0,
            'hybrid': 1.0
        }.get(pathway_type)
        if type_factor is None:
            return None

        probability = base * gap_factor * s_level_factor * step_factor * type_factor

        result = max(0.2, min(0.95, probability))
        logger.debug(f"[_calculate_success_probability] result: {result:.3f} type={pathway_type}")
        return result

    def _identify_side_effects(
        self,
        pathway_type: str,
        required_operators: Dict[str, float]
    ) -> List[str]:
        """
        Identify potential side effects of the transformation.
        """
        effects = []

        # Common transformation side effects
        v_void = required_operators.get('V_void')
        if v_void is not None and v_void > 0.6:
            effects.append("Temporary disorientation as old structures dissolve")

        s_surrender = required_operators.get('S_surrender')
        if s_surrender is not None and s_surrender > 0.7:
            effects.append("Initial loss of sense of control")

        at_attachment = required_operators.get('At_attachment')
        if at_attachment is not None and at_attachment < 0.3:
            effects.append("Relationships may shift as attachment patterns change")

        # Pathway-specific effects
        if pathway_type == 'direct':
            effects.append("Potential for temporary emotional intensity")
            effects.append("May need extra rest during integration")
        elif pathway_type == 'grace':
            effects.append("Periods of waiting and uncertainty")

        logger.debug(f"[_identify_side_effects] result: {len(effects[:3])} effects for type={pathway_type}")
        return effects[:3]

    def _identify_risks(
        self,
        pathway_type: str,
        total_gap: float,
        s_level_gap: float
    ) -> List[str]:
        """
        Identify potential risks of the pathway.
        """
        risks = []

        if pathway_type == 'direct' and total_gap > 0.5:
            risks.append("Risk of burnout from intense change")
            risks.append("Potential instability if changes not integrated")

        if s_level_gap > 2:
            risks.append("Large consciousness gap may require intermediate goals")

        if pathway_type == 'grace' and total_gap > 0.4:
            risks.append("Grace may not activate on expected timeline")

        if not risks:
            risks.append("Minimal identified risks with proper support")

        logger.debug(f"[_identify_risks] result: {len(risks[:3])} risks for type={pathway_type}")
        return risks[:3]

    def _identify_benefits(self, pathway_type: str) -> List[str]:
        """
        Identify unique benefits of this pathway type.
        """
        benefits = {
            'direct': [
                "Fastest path to transformation",
                "Momentum builds quickly",
                "Clear sense of progress"
            ],
            'gradual': [
                "Highly sustainable changes",
                "Minimal disruption to life",
                "Deep integration of changes"
            ],
            'grace': [
                "Transformation beyond personal effort",
                "Unexpected breakthroughs possible",
                "Deepens spiritual connection"
            ],
            'effort': [
                "Clear structure and accountability",
                "Builds discipline and strength",
                "Tangible sense of accomplishment"
            ],
            'hybrid': [
                "Balances effort and surrender",
                "Flexible and adaptable",
                "Good for most situations"
            ]
        }

        return benefits.get(pathway_type, ["Balanced transformation approach"])

    def _calculate_gap(
        self,
        current: Dict[str, float],
        required: Dict[str, float]
    ) -> float:
        """
        Calculate total gap between current and required states.
        """
        total_gap = 0
        for op, req_val in required.items():
            curr_val = current.get(op)
            if curr_val is None:
                continue
            total_gap += abs(req_val - curr_val)

        # Normalize by number of operators
        return total_gap / max(1, len(required))
