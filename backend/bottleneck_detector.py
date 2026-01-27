"""
Bottleneck Detector for Articulation Bridge
Identifies operators blocking progress based on value patterns

UNITY PRINCIPLE ENHANCEMENT:
- Tracks separation amplification for each bottleneck
- Identifies root separation patterns in causal chains
- Generates dual interventions (unity-aligned and separation-based)
"""

from typing import List, Dict, Any
from consciousness_state import ConsciousnessState, Bottleneck
from logging_config import consciousness_logger as logger

# Import unity principle constants and functions
from formulas.unity_principle import (
    UNITY_AMPLIFYING_OPERATORS,
    calculate_separation_amplification,
    generate_unity_intervention,
    generate_separation_intervention,
)


class BottleneckDetector:
    """
    Detect which operators are creating blockages in consciousness evolution.

    Bottleneck conditions:
    1. Attachment-related operators >0.8
    2. Flow-related operators <0.2
    3. Matrix positions at negative poles
    4. Inverse pair imbalances (high Maya + low Witness)
    """

    # Operators where high values indicate blockage
    ATTACHMENT_OPERATORS = [
        ('At_attachment', 'Attachment', 'attachment'),
        ('R_resistance', 'Resistance', 'resistance'),
        ('F_fear', 'Fear', 'fear'),
        ('K_karma', 'Karma', 'karma'),
        ('Hf_habit', 'Habit force', 'habit'),
        ('M_maya', 'Maya/Illusion', 'maya'),
    ]

    # Operators where low values indicate blockage
    FLOW_OPERATORS = [
        ('G_grace', 'Grace', 'grace'),
        ('S_surrender', 'Surrender', 'surrender'),
        ('W_witness', 'Witness consciousness', 'witness'),
        ('O_openness', 'Openness', 'openness'),
        ('Tr_trust', 'Trust', 'trust'),
        ('Co_coherence', 'Coherence', 'coherence'),
        ('V_void', 'Void/Emptiness', 'void'),
        ('Se_service', 'Service orientation', 'service'),
    ]

    # Inverse pairs: when first is high and second is low, creates blockage
    INVERSE_PAIRS = [
        ('M_maya', 'W_witness', 'High illusion with low witness creates reality distortion'),
        ('At_attachment', 'S_surrender', 'Strong attachment prevents surrender'),
        ('F_fear', 'Tr_trust', 'Fear blocks trust'),
        ('R_resistance', 'O_openness', 'Resistance blocks openness'),
        ('K_karma', 'G_grace', 'Heavy karma limits grace reception'),
        ('Hf_habit', 'Ce_cleaning', 'Habit patterns block celebration'),
    ]

    # Negative matrix positions that indicate blockages
    NEGATIVE_MATRIX_POSITIONS = {
        'truth': 'illusion',
        'love': 'separation',
        'power': 'victim',
        'freedom': 'bondage',
        'creation': 'destruction',
        'time': 'past_future',
        'death': 'clinging',
    }

    # Thresholds
    HIGH_THRESHOLD = 0.75  # Above this for attachment operators = bottleneck
    LOW_THRESHOLD = 0.25   # Below this for flow operators = bottleneck
    INVERSE_PAIR_DIFF = 0.4  # Difference threshold for inverse pairs

    def detect(self, state: ConsciousnessState) -> List[Bottleneck]:
        """
        Detect all bottlenecks in the consciousness state.
        Returns list of bottlenecks sorted by impact (high first).
        """
        logger.info("[BOTTLENECK] Starting bottleneck detection")
        bottlenecks: List[Bottleneck] = []

        # Get core operators as dict
        ops = state.tier1.core_operators
        ops_dict = {
            'P_presence': ops.P_presence,
            'A_aware': ops.A_aware,
            'E_equanimity': ops.E_equanimity,
            'Psi_quality': ops.Psi_quality,
            'M_maya': ops.M_maya,
            'M_manifest': ops.M_manifest,
            'W_witness': ops.W_witness,
            'I_intention': ops.I_intention,
            'At_attachment': ops.At_attachment,
            'Se_service': ops.Se_service,
            'Sh_shakti': ops.Sh_shakti,
            'G_grace': ops.G_grace,
            'S_surrender': ops.S_surrender,
            'D_dharma': ops.D_dharma,
            'K_karma': ops.K_karma,
            'Hf_habit': ops.Hf_habit,
            'V_void': ops.V_void,
            'T_time_past': ops.T_time_past,
            'T_time_present': ops.T_time_present,
            'T_time_future': ops.T_time_future,
            'Ce_cleaning': ops.Ce_cleaning,
            'Co_coherence': ops.Co_coherence,
            'R_resistance': ops.R_resistance,
            'F_fear': ops.F_fear,
            'J_joy': ops.J_joy,
            'Tr_trust': ops.Tr_trust,
            'O_openness': ops.O_openness,
        }

        # Check attachment operators (high values = bottleneck)
        bottlenecks.extend(self._check_attachment_operators(ops_dict))

        # Check flow operators (low values = bottleneck)
        bottlenecks.extend(self._check_flow_operators(ops_dict))

        # Check inverse pairs
        bottlenecks.extend(self._check_inverse_pairs(ops_dict))

        # Check matrix positions
        bottlenecks.extend(self._check_matrix_positions(state))

        # Check distortions (Tier 2)
        bottlenecks.extend(self._check_distortions(state))

        # Sort by impact (high first)
        impact_order = {'high': 0, 'medium': 1, 'low': 2}
        bottlenecks.sort(key=lambda b: (impact_order.get(b.impact) if b.impact in impact_order else 3, -b.value))

        high_count = sum(1 for b in bottlenecks if b.impact == 'high')
        root_count = sum(1 for b in bottlenecks if b.is_root_separation_pattern)
        logger.info(
            f"[BOTTLENECK] Detection complete: {len(bottlenecks)} bottlenecks "
            f"({high_count} high impact, {root_count} root separation patterns)"
        )
        for b in bottlenecks[:3]:
            logger.debug(f"[BOTTLENECK] Top: {b.variable} val={b.value:.2f} impact={b.impact} sep_amp={b.separation_amplification_score:.2f}")

        return bottlenecks

    def _check_attachment_operators(self, ops: Dict[str, float]) -> List[Bottleneck]:
        """Check for high attachment-type operators"""
        logger.debug(f"[_check_attachment_operators] checking {len(self.ATTACHMENT_OPERATORS)} operators")
        bottlenecks = []

        for var, name, category in self.ATTACHMENT_OPERATORS:
            value = ops.get(var)
            if value is None:
                continue
            if value > self.HIGH_THRESHOLD:
                logger.debug(f"[BOTTLENECK] Attachment bottleneck: {var}={value:.2f} > {self.HIGH_THRESHOLD}")
                impact = 'high' if value > 0.85 else 'medium'

                # Calculate separation amplification
                sep_amp = calculate_separation_amplification(var, value)
                is_root = sep_amp > 0.6

                # Generate interventions
                unity_int = generate_unity_intervention(var)
                sep_int = generate_separation_intervention(var)

                bottlenecks.append(Bottleneck(
                    variable=var,
                    value=value,
                    impact=impact,
                    description=f"{name} at {value:.0%} is creating resistance to transformation",
                    category=category,
                    separation_amplification_score=sep_amp,
                    is_root_separation_pattern=is_root,
                    unity_aligned_intervention=unity_int,
                    separation_based_intervention=sep_int
                ))

        logger.debug(f"[_check_attachment_operators] result: {len(bottlenecks)} bottlenecks")
        return bottlenecks

    def _check_flow_operators(self, ops: Dict[str, float]) -> List[Bottleneck]:
        """Check for low flow-type operators (unity-amplifying when high)"""
        logger.debug(f"[_check_flow_operators] checking {len(self.FLOW_OPERATORS)} operators")
        bottlenecks = []

        for var, name, category in self.FLOW_OPERATORS:
            value = ops.get(var)
            if value is None:
                continue
            if value < self.LOW_THRESHOLD:
                logger.debug(f"[BOTTLENECK] Flow bottleneck: {var}={value:.2f} < {self.LOW_THRESHOLD}")
                impact = 'high' if value < 0.15 else 'medium'

                # Low flow operators indicate reduced unity capacity
                # Separation amplification is inverse - low unity = high separation effect
                unity_base = UNITY_AMPLIFYING_OPERATORS.get(var)
                if unity_base is None:
                    continue
                sep_amp = (1.0 - value) * unity_base
                is_root = sep_amp > 0.6

                # Generate interventions for building unity capacity
                unity_int = generate_unity_intervention(var)
                sep_int = generate_separation_intervention(var)

                bottlenecks.append(Bottleneck(
                    variable=var,
                    value=value,
                    impact=impact,
                    description=f"Low {name} ({value:.0%}) limits capacity for transformation",
                    category=category,
                    separation_amplification_score=sep_amp,
                    is_root_separation_pattern=is_root,
                    unity_aligned_intervention=unity_int,
                    separation_based_intervention=sep_int
                ))

        logger.debug(f"[_check_flow_operators] result: {len(bottlenecks)} bottlenecks")
        return bottlenecks

    def _check_inverse_pairs(self, ops: Dict[str, float]) -> List[Bottleneck]:
        """Check for inverse pair imbalances (separation vs unity dynamics)"""
        logger.debug(f"[_check_inverse_pairs] checking {len(self.INVERSE_PAIRS)} pairs")
        bottlenecks = []

        for high_var, low_var, description in self.INVERSE_PAIRS:
            high_val = ops.get(high_var)
            low_val = ops.get(low_var)
            if high_val is None or low_val is None:
                continue

            # Check if first is high AND second is low
            if high_val > 0.6 and low_val < 0.4 and (high_val - low_val) > self.INVERSE_PAIR_DIFF:
                logger.debug(f"[BOTTLENECK] Inverse pair: {high_var}={high_val:.2f} vs {low_var}={low_val:.2f} (diff={high_val-low_val:.2f})")
                impact = 'high' if (high_val - low_val) > 0.5 else 'medium'

                # Inverse pairs are root separation patterns by definition
                # They represent the core Maya-Witness polarity
                sep_amp_high = calculate_separation_amplification(high_var, high_val)
                unity_base_low = UNITY_AMPLIFYING_OPERATORS.get(low_var)
                if sep_amp_high is None or unity_base_low is None:
                    continue
                sep_amp_low = (1.0 - low_val) * unity_base_low
                combined_sep_amp = (sep_amp_high + sep_amp_low) / 2.0

                # Generate dual interventions
                unity_int = f"Cultivate {low_var.split('_')[1]} while allowing {high_var.split('_')[1]} to naturally dissolve through awareness"
                sep_int = f"Work on reducing {high_var.split('_')[1]} through effort while building {low_var.split('_')[1]}"

                bottlenecks.append(Bottleneck(
                    variable=f"{high_var}|{low_var}",
                    value=(high_val - low_val),
                    impact=impact,
                    description=description,
                    category='inverse_pair',
                    separation_amplification_score=combined_sep_amp,
                    is_root_separation_pattern=True,  # Inverse pairs are always root patterns
                    unity_aligned_intervention=unity_int,
                    separation_based_intervention=sep_int
                ))

        logger.debug(f"[_check_inverse_pairs] result: {len(bottlenecks)} bottlenecks")
        return bottlenecks

    def _check_matrix_positions(self, state: ConsciousnessState) -> List[Bottleneck]:
        """Check for negative matrix positions (death architecture patterns)"""
        logger.debug("[_check_matrix_positions] checking 7 matrices")
        bottlenecks = []
        matrices = state.tier3.transformation_matrices

        matrix_checks = [
            ('truth', matrices.truth_position, matrices.truth_score, 'Truth'),
            ('love', matrices.love_position, matrices.love_score, 'Love'),
            ('power', matrices.power_position, matrices.power_score, 'Power'),
            ('freedom', matrices.freedom_position, matrices.freedom_score, 'Freedom'),
            ('creation', matrices.creation_position, matrices.creation_score, 'Creation'),
            ('time', matrices.time_position, matrices.time_score, 'Time'),
            ('death', matrices.death_position, matrices.death_score, 'Death'),
        ]

        # Unity interventions for each matrix type
        matrix_unity_interventions = {
            'truth': "Allow truth to reveal itself through stillness and witness consciousness",
            'love': "Recognize the underlying unity beneath apparent separation",
            'power': "Discover authentic power through surrender rather than control",
            'freedom': "Find freedom by releasing attachment to outcomes",
            'creation': "Align creative action with natural flow rather than forcing",
            'time': "Rest in present moment awareness beyond past/future narratives",
            'death': "Embrace impermanence as gateway to deeper aliveness",
        }

        matrix_separation_interventions = {
            'truth': "Work to distinguish truth from illusion through analysis",
            'love': "Practice connection exercises to overcome feelings of separation",
            'power': "Build personal power through discipline and effort",
            'freedom': "Identify and remove external constraints systematically",
            'creation': "Focus creative effort and push through blocks",
            'time': "Manage time better and stay focused on present tasks",
            'death': "Address fear of death through understanding and preparation",
        }

        for matrix_type, position, score, name in matrix_checks:
            negative_position = self.NEGATIVE_MATRIX_POSITIONS.get(matrix_type)
            if position == negative_position:
                impact = 'high' if score < 0.2 else 'medium'

                # Matrix positions at negative poles indicate deep separation patterns
                sep_amp = 1.0 - score  # Lower score = higher separation
                is_root = matrix_type in ['truth', 'death']  # Truth/illusion and death/clinging are root patterns

                bottlenecks.append(Bottleneck(
                    variable=f"matrix_{matrix_type}",
                    value=score,
                    impact=impact,
                    description=f"{name} matrix at '{position}' position ({score:.0%}) indicates blocked transformation",
                    category='matrix',
                    separation_amplification_score=sep_amp,
                    is_root_separation_pattern=is_root,
                    unity_aligned_intervention=matrix_unity_interventions.get(matrix_type),
                    separation_based_intervention=matrix_separation_interventions.get(matrix_type)
                ))

        logger.debug(f"[_check_matrix_positions] result: {len(bottlenecks)} bottlenecks")
        return bottlenecks

    def _check_distortions(self, state: ConsciousnessState) -> List[Bottleneck]:
        """Check Tier 2 distortions (kleshas) - root separation patterns"""
        logger.debug("[_check_distortions] checking tier 2 kleshas")
        bottlenecks = []
        distortions = state.tier2.distortions

        distortion_checks = [
            ('asmita', distortions.asmita, 'Ego-identification'),
            ('raga', distortions.raga, 'Attachment patterns'),
            ('dvesha', distortions.dvesha, 'Aversion patterns'),
            ('abhinivesha', distortions.abhinivesha, 'Fear of death/change'),
            ('avidya_total', distortions.avidya_total, 'Root ignorance'),
        ]

        # Kleshas are the root causes of separation in yogic philosophy
        klesha_unity_interventions = {
            'asmita': "Rest in awareness beyond the sense of separate self",
            'raga': "Notice how attachment creates suffering; allow preferences without grasping",
            'dvesha': "Recognize aversion as the flip side of attachment; find equanimity",
            'abhinivesha': "Contemplate the deathless nature of awareness itself",
            'avidya_total': "Cultivate viveka (discernment) through steady witness practice",
        }

        klesha_separation_interventions = {
            'asmita': "Work on ego boundaries and healthy self-concept",
            'raga': "Practice detachment exercises and reduce dependency",
            'dvesha': "Address aversions through gradual exposure and desensitization",
            'abhinivesha': "Confront mortality fears through philosophical study",
            'avidya_total': "Study and learn to distinguish real from unreal",
        }

        for var, value, name in distortion_checks:
            if value is None:
                continue
            if value > 0.7:
                impact = 'high' if value > 0.85 else 'medium'

                # Kleshas directly amplify separation - avidya is the root
                sep_amp = value  # Direct mapping: high klesha = high separation
                is_root = var == 'avidya_total'  # Avidya is the root of all kleshas

                bottlenecks.append(Bottleneck(
                    variable=f"distortion_{var}",
                    value=value,
                    impact=impact,
                    description=f"{name} at {value:.0%} is a deep-level obstruction",
                    category='klesha',
                    separation_amplification_score=sep_amp,
                    is_root_separation_pattern=is_root,
                    unity_aligned_intervention=klesha_unity_interventions.get(var),
                    separation_based_intervention=klesha_separation_interventions.get(var)
                ))

        logger.debug(f"[_check_distortions] result: {len(bottlenecks)} bottlenecks")
        return bottlenecks

    def get_summary(self, bottlenecks: List[Bottleneck]) -> Dict[str, Any]:
        """Get summary of bottleneck analysis"""
        logger.debug(f"[get_summary] summarizing {len(bottlenecks)} bottlenecks")
        if not bottlenecks:
            return {
                'total_count': 0,
                'high_impact_count': 0,
                'primary_bottleneck': None,
                'categories': {}
            }

        high_impact = [b for b in bottlenecks if b.impact == 'high']
        categories = {}
        for b in bottlenecks:
            categories[b.category] = categories.get(b.category, 0) + 1

        return {
            'total_count': len(bottlenecks),
            'high_impact_count': len(high_impact),
            'primary_bottleneck': bottlenecks[0] if bottlenecks else None,
            'categories': categories
        }
