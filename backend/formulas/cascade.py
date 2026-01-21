"""
Cascade Cleanliness Component Formulas
Seven-level cascade from Self to Body with component calculations

The Heartfulness Cascade represents cleanliness at each level:
1. Self (Atman) - Pure witness consciousness
2. Ego (Ahamkara) - Identity structures
3. Memory (Chitta) - Stored impressions
4. Intellect (Buddhi) - Discrimination faculty
5. Mind (Manas) - Thought activity
6. Breath (Prana) - Life force
7. Body (Annamaya) - Physical form
"""

from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
import math


@dataclass
class CascadeLevel:
    """A single level in the cascade"""
    level: int
    name: str
    sanskrit: str
    cleanliness: float  # 0.0-1.0
    blockage: float     # 0.0-1.0
    flow_rate: float    # How well energy flows through
    description: str


@dataclass
class CascadeState:
    """Complete cascade state"""
    levels: List[CascadeLevel]
    overall_cleanliness: float
    primary_blockage: str
    flow_efficiency: float
    cleaning_priority: str


class CascadeCalculator:
    """
    Calculate cascade cleanliness at each of the 7 levels.
    Uses operator values to derive cleanliness scores.
    """

    LEVELS = [
        {'level': 1, 'name': 'Self', 'sanskrit': 'Atman'},
        {'level': 2, 'name': 'Ego', 'sanskrit': 'Ahamkara'},
        {'level': 3, 'name': 'Memory', 'sanskrit': 'Chitta'},
        {'level': 4, 'name': 'Intellect', 'sanskrit': 'Buddhi'},
        {'level': 5, 'name': 'Mind', 'sanskrit': 'Manas'},
        {'level': 6, 'name': 'Breath', 'sanskrit': 'Prana'},
        {'level': 7, 'name': 'Body', 'sanskrit': 'Annamaya'}
    ]

    def calculate_cascade(self, operators: Dict[str, float]) -> CascadeState:
        """Calculate complete cascade state from operator values"""
        levels = []

        for level_def in self.LEVELS:
            level_num = level_def['level']
            cleanliness = self._calculate_level_cleanliness(level_num, operators)
            blockage = 1.0 - cleanliness
            flow_rate = self._calculate_flow_rate(level_num, cleanliness, operators)

            levels.append(CascadeLevel(
                level=level_num,
                name=level_def['name'],
                sanskrit=level_def['sanskrit'],
                cleanliness=cleanliness,
                blockage=blockage,
                flow_rate=flow_rate,
                description=self._get_level_description(level_num, cleanliness)
            ))

        # Calculate overall metrics
        overall = sum(l.cleanliness for l in levels) / len(levels)
        flow_efficiency = self._calculate_overall_flow(levels)

        # Find primary blockage
        most_blocked = max(levels, key=lambda l: l.blockage)
        primary_blockage = most_blocked.name if most_blocked.blockage > 0.3 else "None significant"

        # Determine cleaning priority
        cleaning_priority = self._determine_cleaning_priority(levels)

        return CascadeState(
            levels=levels,
            overall_cleanliness=overall,
            primary_blockage=primary_blockage,
            flow_efficiency=flow_efficiency,
            cleaning_priority=cleaning_priority
        )

    def _calculate_level_cleanliness(
        self,
        level: int,
        operators: Dict[str, float]
    ) -> float:
        """Calculate cleanliness for a specific cascade level"""

        # Get operator values with defaults
        W = operators.get('W_witness', 0.5)
        A = operators.get('A_aware', 0.5)
        Ce = operators.get('Ce_celebration', 0.5)  # Cleaning/Celebration
        At = operators.get('At_attachment', 0.5)
        M = operators.get('M_maya', 0.5)
        Hf = operators.get('Hf_habit', 0.5)
        Sa = operators.get('Sa_samskara', 0.5) if 'Sa_samskara' in operators else 0.5
        K = operators.get('K_karma', 0.5)
        P = operators.get('P_presence', 0.5)
        F = operators.get('F_fear', 0.5)

        if level == 1:  # Self (Atman)
            # Self cleanliness = witness consciousness - maya veiling
            # Formula: C1 = W × (1 - M) × A^0.5
            return W * (1 - M * 0.7) * math.sqrt(A)

        elif level == 2:  # Ego (Ahamkara)
            # Ego cleanliness = low attachment, high witness
            # Formula: C2 = (1 - At) × (1 - asmita) × W^0.7
            asmita = At * M * 0.8  # Ego-identification approximation
            return (1 - At * 0.8) * (1 - asmita) * (W ** 0.7)

        elif level == 3:  # Memory (Chitta)
            # Memory cleanliness = low samskaras, high cleaning
            # Formula: C3 = Ce × (1 - Sa) × (1 - K × 0.5)
            return Ce * (1 - Sa * 0.7) * (1 - K * 0.4)

        elif level == 4:  # Intellect (Buddhi)
            # Intellect cleanliness = high awareness, low maya
            # Formula: C4 = A × (1 - M) × W^0.5
            return A * (1 - M * 0.8) * math.sqrt(W)

        elif level == 5:  # Mind (Manas)
            # Mind cleanliness = low habit force, low disturbance
            # Formula: C5 = (1 - Hf) × P × (1 - F × 0.5)
            return (1 - Hf * 0.7) * P * (1 - F * 0.4)

        elif level == 6:  # Breath (Prana)
            # Prana cleanliness = presence, low fear
            # Formula: C6 = P × (1 - F × 0.7) × Ce^0.5
            return P * (1 - F * 0.6) * math.sqrt(Ce)

        elif level == 7:  # Body (Annamaya)
            # Body cleanliness = aggregate of all higher levels
            # Formula: C7 = (Ce + P + (1 - At)) / 3 × stability
            stability = 1 - (At * 0.3 + F * 0.3 + Hf * 0.2)
            return ((Ce + P + (1 - At * 0.5)) / 3) * stability

        return 0.5

    def _calculate_flow_rate(
        self,
        level: int,
        cleanliness: float,
        operators: Dict[str, float]
    ) -> float:
        """Calculate how well energy flows through this level"""
        R = operators.get('R_resistance', 0.5)
        G = operators.get('G_grace', 0.5)

        # Flow = cleanliness × (1 - resistance) × (1 + grace bonus)
        base_flow = cleanliness * (1 - R * 0.6)
        grace_bonus = G * 0.3

        return min(1.0, base_flow * (1 + grace_bonus))

    def _calculate_overall_flow(self, levels: List[CascadeLevel]) -> float:
        """
        Calculate overall cascade flow efficiency.
        Flow is limited by the most blocked level (bottleneck).
        """
        if not levels:
            return 0.5

        # The cascade can't flow faster than its slowest point
        min_flow = min(l.flow_rate for l in levels)

        # But overall efficiency also depends on average
        avg_flow = sum(l.flow_rate for l in levels) / len(levels)

        # Weighted combination: bottleneck matters more
        return 0.7 * min_flow + 0.3 * avg_flow

    def _determine_cleaning_priority(self, levels: List[CascadeLevel]) -> str:
        """Determine which level should be prioritized for cleaning"""
        # Find most blocked level
        most_blocked = max(levels, key=lambda l: l.blockage)

        if most_blocked.blockage < 0.2:
            return "Maintenance only - cascade relatively clean"

        # Cleaning from subtle to gross is most effective
        # But severe blockages at any level need attention
        if most_blocked.blockage > 0.6:
            return f"Urgent: {most_blocked.name} ({most_blocked.sanskrit}) severely blocked"

        # Check for pattern of blockages
        upper_blocked = any(l.blockage > 0.4 for l in levels[:3])
        lower_blocked = any(l.blockage > 0.4 for l in levels[4:])

        if upper_blocked and not lower_blocked:
            return "Focus on subtle levels (Self, Ego, Memory) - root causes"
        elif lower_blocked and not upper_blocked:
            return "Focus on gross levels (Mind, Breath, Body) - symptoms"
        else:
            return f"Priority: {most_blocked.name} - most significant blockage"

    def _get_level_description(self, level: int, cleanliness: float) -> str:
        """Get description for a cascade level"""
        pct = cleanliness * 100

        descriptions = {
            1: {
                'low': "Self-awareness obscured by identification",
                'mid': "Partial witness consciousness available",
                'high': "Clear witness presence"
            },
            2: {
                'low': "Strong ego identification and defensiveness",
                'mid': "Ego present but not dominant",
                'high': "Healthy ego, minimal identification"
            },
            3: {
                'low': "Heavy impression load affecting perception",
                'mid': "Some clearing of old patterns",
                'high': "Memory clean, minimal reactive patterns"
            },
            4: {
                'low': "Discrimination clouded by conditioning",
                'mid': "Reasonable discernment capacity",
                'high': "Clear discriminative wisdom"
            },
            5: {
                'low': "Mind agitated with excessive thoughts",
                'mid': "Mind moderately settled",
                'high': "Calm, focused mental activity"
            },
            6: {
                'low': "Breath irregular, prana blocked",
                'mid': "Breath reasonably smooth",
                'high': "Breath free and vital"
            },
            7: {
                'low': "Body tense, holding patterns",
                'mid': "Body moderately relaxed",
                'high': "Body open and flowing"
            }
        }

        level_desc = descriptions.get(level, {'low': '', 'mid': '', 'high': ''})

        if pct < 40:
            return level_desc['low']
        elif pct < 70:
            return level_desc['mid']
        else:
            return level_desc['high']

    def calculate_cleaning_effect(
        self,
        current_state: CascadeState,
        cleaning_intensity: float,
        cleaning_duration_minutes: int
    ) -> Dict[str, Any]:
        """
        Estimate the effect of cleaning practice on cascade.

        Args:
            current_state: Current cascade state
            cleaning_intensity: 0.0-1.0 intensity of practice
            cleaning_duration_minutes: Duration in minutes

        Returns:
            Predicted changes to cascade
        """
        # Cleaning effect diminishes with time (logarithmic)
        time_factor = math.log(1 + cleaning_duration_minutes / 10) / 3

        # Intensity amplifies effect
        effect_multiplier = cleaning_intensity * time_factor

        predicted_changes = {}
        for level in current_state.levels:
            # More blocked levels have more room for improvement
            improvement_potential = level.blockage * effect_multiplier

            # But improvement is harder at subtle levels
            difficulty_factor = 1.0 - (level.level - 1) * 0.08

            predicted_improvement = improvement_potential * difficulty_factor

            predicted_changes[level.name] = {
                'current_cleanliness': level.cleanliness,
                'predicted_improvement': min(0.2, predicted_improvement),
                'predicted_cleanliness': min(1.0, level.cleanliness + predicted_improvement)
            }

        return {
            'predicted_changes': predicted_changes,
            'recommended_focus': current_state.cleaning_priority,
            'effect_strength': effect_multiplier
        }

    def get_klesha_mapping(self, operators: Dict[str, float]) -> Dict[str, float]:
        """
        Map cascade blockages to kleshas (afflictions).

        Kleshas:
        - Avidya (ignorance) - root of all kleshas
        - Asmita (ego-identification)
        - Raga (attachment)
        - Dvesha (aversion)
        - Abhinivesha (fear of death/change)
        """
        At = operators.get('At_attachment', 0.5)
        F = operators.get('F_fear', 0.5)
        M = operators.get('M_maya', 0.5)
        Av = operators.get('Av_aversion', 0.5) if 'Av_aversion' in operators else F * 0.8
        W = operators.get('W_witness', 0.5)

        return {
            'avidya': M * (1 - W),  # Ignorance = maya × low witness
            'asmita': At * M * 0.8,  # Ego-identification
            'raga': At,              # Attachment
            'dvesha': Av,            # Aversion
            'abhinivesha': F * 0.9   # Fear of change/death
        }
