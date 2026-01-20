"""
Bottleneck Detector for Articulation Bridge
Identifies operators blocking progress based on value patterns
"""

from typing import List, Dict, Any
from consciousness_state import ConsciousnessState, Bottleneck


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
        ('Hf_habit', 'Ce_celebration', 'Habit patterns block celebration'),
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
            'Ce_celebration': ops.Ce_celebration,
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
        bottlenecks.sort(key=lambda b: (impact_order.get(b.impact, 3), -b.value))

        return bottlenecks

    def _check_attachment_operators(self, ops: Dict[str, float]) -> List[Bottleneck]:
        """Check for high attachment-type operators"""
        bottlenecks = []

        for var, name, category in self.ATTACHMENT_OPERATORS:
            value = ops.get(var, 0.5)
            if value > self.HIGH_THRESHOLD:
                impact = 'high' if value > 0.85 else 'medium'
                bottlenecks.append(Bottleneck(
                    variable=var,
                    value=value,
                    impact=impact,
                    description=f"{name} at {value:.0%} is creating resistance to transformation",
                    category=category
                ))

        return bottlenecks

    def _check_flow_operators(self, ops: Dict[str, float]) -> List[Bottleneck]:
        """Check for low flow-type operators"""
        bottlenecks = []

        for var, name, category in self.FLOW_OPERATORS:
            value = ops.get(var, 0.5)
            if value < self.LOW_THRESHOLD:
                impact = 'high' if value < 0.15 else 'medium'
                bottlenecks.append(Bottleneck(
                    variable=var,
                    value=value,
                    impact=impact,
                    description=f"Low {name} ({value:.0%}) limits capacity for transformation",
                    category=category
                ))

        return bottlenecks

    def _check_inverse_pairs(self, ops: Dict[str, float]) -> List[Bottleneck]:
        """Check for inverse pair imbalances"""
        bottlenecks = []

        for high_var, low_var, description in self.INVERSE_PAIRS:
            high_val = ops.get(high_var, 0.5)
            low_val = ops.get(low_var, 0.5)

            # Check if first is high AND second is low
            if high_val > 0.6 and low_val < 0.4 and (high_val - low_val) > self.INVERSE_PAIR_DIFF:
                impact = 'high' if (high_val - low_val) > 0.5 else 'medium'
                bottlenecks.append(Bottleneck(
                    variable=f"{high_var}|{low_var}",
                    value=(high_val - low_val),
                    impact=impact,
                    description=description,
                    category='inverse_pair'
                ))

        return bottlenecks

    def _check_matrix_positions(self, state: ConsciousnessState) -> List[Bottleneck]:
        """Check for negative matrix positions"""
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

        for matrix_type, position, score, name in matrix_checks:
            negative_position = self.NEGATIVE_MATRIX_POSITIONS.get(matrix_type)
            if position == negative_position:
                impact = 'high' if score < 0.2 else 'medium'
                bottlenecks.append(Bottleneck(
                    variable=f"matrix_{matrix_type}",
                    value=score,
                    impact=impact,
                    description=f"{name} matrix at '{position}' position ({score:.0%}) indicates blocked transformation",
                    category='matrix'
                ))

        return bottlenecks

    def _check_distortions(self, state: ConsciousnessState) -> List[Bottleneck]:
        """Check Tier 2 distortions (kleshas)"""
        bottlenecks = []
        distortions = state.tier2.distortions

        distortion_checks = [
            ('asmita', distortions.asmita, 'Ego-identification'),
            ('raga', distortions.raga, 'Attachment patterns'),
            ('dvesha', distortions.dvesha, 'Aversion patterns'),
            ('abhinivesha', distortions.abhinivesha, 'Fear of death/change'),
            ('avidya_total', distortions.avidya_total, 'Root ignorance'),
        ]

        for var, value, name in distortion_checks:
            if value > 0.7:
                impact = 'high' if value > 0.85 else 'medium'
                bottlenecks.append(Bottleneck(
                    variable=f"distortion_{var}",
                    value=value,
                    impact=impact,
                    description=f"{name} at {value:.0%} is a deep-level obstruction",
                    category='klesha'
                ))

        return bottlenecks

    def get_summary(self, bottlenecks: List[Bottleneck]) -> Dict[str, Any]:
        """Get summary of bottleneck analysis"""
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
