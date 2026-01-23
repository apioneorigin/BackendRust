"""
Realism Engine - 60 Reality Types
Different reality frameworks experienced at different consciousness levels

Reality types organize by S-level clusters:
- S1-S2: Survival/Biological realisms (dirty, naturalistic, material, physical)
- S3-S4: Social/Achievement realisms (economic, professional, psychological)
- S5-S6: Service/Flow realisms (emotional, holistic, integrated)
- S7-S8: Unity/Transcendent realisms (witness, grace, universal, absolute)

Each realism type has:
- Characteristic operator patterns
- Typical manifestation style
- Limitations and possibilities
- Transformation requirements
"""

from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
import math


@dataclass
class RealismType:
    """A type of reality perception/construction"""
    name: str
    category: str
    s_level_range: Tuple[float, float]
    description: str
    operator_signature: Dict[str, float]  # Expected operator patterns
    manifestation_style: str
    limitations: List[str]
    possibilities: List[str]


@dataclass
class RealismProfile:
    """Individual's realism profile"""
    active_realisms: List[str]
    dominant_realism: Optional[str]
    dominant_weight: Optional[float]
    realism_blend: Dict[str, float]
    coherence: Optional[float]  # How well realisms integrate
    evolution_direction: str
    recommended_expansion: List[str]
    missing_operators: Set[str] = field(default_factory=set)


class RealismEngine:
    """
    Calculate realism types and their interactions.
    Models how consciousness constructs reality at different levels.
    """

    # 60 Realism Types organized by S-level clusters
    REALISM_TYPES = {
        # ============ S1-S2: SURVIVAL/BIOLOGICAL ============
        'dirty': RealismType(
            name='Dirty Realism',
            category='biological',
            s_level_range=(1.0, 2.5),
            description='Raw, unfiltered reality of survival needs',
            operator_signature={'F_fear': 0.7, 'At_attachment': 0.8, 'P_presence': 0.3},
            manifestation_style='immediate, reactive, body-based',
            limitations=['Limited long-term thinking', 'Fear-driven choices'],
            possibilities=['Strong survival instincts', 'Grounded in body']
        ),
        'naturalistic': RealismType(
            name='Naturalistic Realism',
            category='biological',
            s_level_range=(1.0, 2.5),
            description='Reality as natural processes and cycles',
            operator_signature={'P_presence': 0.5, 'Co_coherence': 0.4, 'A_aware': 0.4},
            manifestation_style='cyclical, organic, patient',
            limitations=['May resist intervention', 'Passive approach'],
            possibilities=['Harmony with nature', 'Sustainable patterns']
        ),
        'biological': RealismType(
            name='Biological Realism',
            category='biological',
            s_level_range=(1.0, 2.0),
            description='Reality through body and instinct',
            operator_signature={'P_presence': 0.4, 'F_fear': 0.5, 'Sh_shakti': 0.5},
            manifestation_style='somatic, instinctual, visceral',
            limitations=['Limited abstract thinking', 'Reactive'],
            possibilities=['Strong intuition', 'Physical vitality']
        ),
        'survival': RealismType(
            name='Survival Realism',
            category='biological',
            s_level_range=(1.0, 1.5),
            description='Reality as threat/safety binary',
            operator_signature={'F_fear': 0.8, 'R_resistance': 0.6, 'At_attachment': 0.7},
            manifestation_style='defensive, protective, vigilant',
            limitations=['Cannot relax', 'Limited trust'],
            possibilities=['Quick threat response', 'Resourcefulness']
        ),
        'scarcity': RealismType(
            name='Scarcity Realism',
            category='biological',
            s_level_range=(1.0, 2.0),
            description='Reality as limited resources',
            operator_signature={'At_attachment': 0.8, 'F_fear': 0.6, 'O_openness': 0.2},
            manifestation_style='hoarding, competitive, anxious',
            limitations=['Cannot see abundance', 'Zero-sum thinking'],
            possibilities=['Efficient resource use', 'Practicality']
        ),
        'material': RealismType(
            name='Material Realism',
            category='biological',
            s_level_range=(1.5, 2.5),
            description='Reality as physical matter',
            operator_signature={'P_presence': 0.4, 'M_maya': 0.6, 'At_attachment': 0.5},
            manifestation_style='concrete, tangible, measurable',
            limitations=['Misses subtle dimensions', 'Reductionist'],
            possibilities=['Practical accomplishment', 'Physical mastery']
        ),
        'physical': RealismType(
            name='Physical Realism',
            category='biological',
            s_level_range=(1.5, 2.5),
            description='Reality through sensory experience',
            operator_signature={'P_presence': 0.5, 'A_aware': 0.4, 'Psi_quality': 0.3},
            manifestation_style='sensory, embodied, concrete',
            limitations=['May miss non-physical reality'],
            possibilities=['Strong grounding', 'Embodiment']
        ),
        'sensory': RealismType(
            name='Sensory Realism',
            category='biological',
            s_level_range=(1.5, 2.5),
            description='Reality as sense perceptions',
            operator_signature={'A_aware': 0.5, 'P_presence': 0.5, 'O_openness': 0.4},
            manifestation_style='perceptual, aesthetic, experiential',
            limitations=['Surface-level perception'],
            possibilities=['Rich sensory experience', 'Aesthetic appreciation']
        ),

        # ============ S2-S3: SEEKING/EMOTIONAL ============
        'emotional': RealismType(
            name='Emotional Realism',
            category='seeking',
            s_level_range=(2.0, 3.5),
            description='Reality colored by emotional states',
            operator_signature={'At_attachment': 0.6, 'J_joy': 0.5, 'F_fear': 0.4},
            manifestation_style='feeling-based, reactive, personal',
            limitations=['Emotional volatility affects perception'],
            possibilities=['Deep feeling capacity', 'Empathy']
        ),
        'romantic': RealismType(
            name='Romantic Realism',
            category='seeking',
            s_level_range=(2.0, 3.5),
            description='Reality idealized through longing',
            operator_signature={'At_attachment': 0.7, 'I_intention': 0.6, 'M_maya': 0.5},
            manifestation_style='idealized, passionate, dramatic',
            limitations=['May miss reality as-is'],
            possibilities=['Inspiration', 'Vision', 'Passion']
        ),
        'psychological': RealismType(
            name='Psychological Realism',
            category='seeking',
            s_level_range=(2.5, 4.0),
            description='Reality as mental/emotional patterns',
            operator_signature={'A_aware': 0.6, 'W_witness': 0.4, 'At_attachment': 0.5},
            manifestation_style='analytical, introspective, therapeutic',
            limitations=['May over-analyze', 'Mental loops'],
            possibilities=['Self-understanding', 'Pattern recognition']
        ),
        'relational': RealismType(
            name='Relational Realism',
            category='seeking',
            s_level_range=(2.5, 4.0),
            description='Reality through relationships',
            operator_signature={'Se_service': 0.5, 'Co_coherence': 0.5, 'At_attachment': 0.5},
            manifestation_style='interpersonal, connected, social',
            limitations=['Dependent on others', 'Boundary issues'],
            possibilities=['Deep connection', 'Support systems']
        ),

        # ============ S3-S4: ACHIEVEMENT/SOCIAL ============
        'social': RealismType(
            name='Social Realism',
            category='achievement',
            s_level_range=(3.0, 4.5),
            description='Reality as social structures and roles',
            operator_signature={'Co_coherence': 0.6, 'At_attachment': 0.5, 'D_dharma': 0.4},
            manifestation_style='role-based, conventional, structured',
            limitations=['Conformity', 'Status anxiety'],
            possibilities=['Social intelligence', 'Networking']
        ),
        'economic': RealismType(
            name='Economic Realism',
            category='achievement',
            s_level_range=(3.0, 4.5),
            description='Reality as exchange and value',
            operator_signature={'I_intention': 0.6, 'At_attachment': 0.5, 'M_manifest': 0.5},
            manifestation_style='transactional, strategic, growth-oriented',
            limitations=['Reduces to economics', 'Commodification'],
            possibilities=['Wealth creation', 'Resource optimization']
        ),
        'political': RealismType(
            name='Political Realism',
            category='achievement',
            s_level_range=(3.0, 4.5),
            description='Reality as power dynamics',
            operator_signature={'I_intention': 0.7, 'R_resistance': 0.4, 'Co_coherence': 0.4},
            manifestation_style='strategic, influential, power-aware',
            limitations=['May become manipulative'],
            possibilities=['Effective leadership', 'Change agency']
        ),
        'achievement': RealismType(
            name='Achievement Realism',
            category='achievement',
            s_level_range=(3.0, 4.0),
            description='Reality as goals and accomplishments',
            operator_signature={'I_intention': 0.8, 'At_attachment': 0.6, 'Sh_shakti': 0.6},
            manifestation_style='goal-driven, ambitious, productive',
            limitations=['Never enough', 'Burnout'],
            possibilities=['High accomplishment', 'Impact']
        ),
        'professional': RealismType(
            name='Professional Realism',
            category='achievement',
            s_level_range=(3.0, 4.5),
            description='Reality through career/expertise',
            operator_signature={'D_dharma': 0.5, 'I_intention': 0.6, 'Co_coherence': 0.5},
            manifestation_style='skilled, specialized, credentialed',
            limitations=['Identity tied to work'],
            possibilities=['Expertise', 'Professional excellence']
        ),
        'competitive': RealismType(
            name='Competitive Realism',
            category='achievement',
            s_level_range=(3.0, 4.0),
            description='Reality as competition',
            operator_signature={'I_intention': 0.7, 'R_resistance': 0.5, 'At_attachment': 0.6},
            manifestation_style='winning-focused, comparative, driven',
            limitations=['Zero-sum mindset', 'Exhausting'],
            possibilities=['Peak performance', 'Excellence']
        ),
        'strategic': RealismType(
            name='Strategic Realism',
            category='achievement',
            s_level_range=(3.5, 5.0),
            description='Reality as strategic landscape',
            operator_signature={'A_aware': 0.6, 'I_intention': 0.7, 'W_witness': 0.4},
            manifestation_style='calculated, planned, long-term',
            limitations=['May miss spontaneous opportunities'],
            possibilities=['Effective planning', 'Vision realization']
        ),

        # ============ S4-S5: SERVICE/TRANSITION ============
        'service': RealismType(
            name='Service Realism',
            category='service',
            s_level_range=(4.0, 5.5),
            description='Reality as opportunity to serve',
            operator_signature={'Se_service': 0.8, 'At_attachment': 0.3, 'G_grace': 0.5},
            manifestation_style='giving, contributing, supportive',
            limitations=['May neglect self'],
            possibilities=['Fulfillment through service', 'Impact']
        ),
        'purposeful': RealismType(
            name='Purposeful Realism',
            category='service',
            s_level_range=(4.0, 5.5),
            description='Reality as purpose expression',
            operator_signature={'D_dharma': 0.7, 'I_intention': 0.6, 'Se_service': 0.5},
            manifestation_style='mission-driven, meaningful, directed',
            limitations=['Rigidity about purpose'],
            possibilities=['Clear direction', 'Meaningful life']
        ),
        'ethical': RealismType(
            name='Ethical Realism',
            category='service',
            s_level_range=(4.0, 5.5),
            description='Reality through moral framework',
            operator_signature={'D_dharma': 0.7, 'A_aware': 0.6, 'Se_service': 0.5},
            manifestation_style='principled, just, fair',
            limitations=['May become judgmental'],
            possibilities=['Integrity', 'Moral clarity']
        ),
        'systemic': RealismType(
            name='Systemic Realism',
            category='service',
            s_level_range=(4.0, 5.5),
            description='Reality as interconnected systems',
            operator_signature={'Co_coherence': 0.7, 'A_aware': 0.6, 'W_witness': 0.5},
            manifestation_style='holistic, connected, patterned',
            limitations=['Can be overwhelming'],
            possibilities=['Systems thinking', 'Leverage points']
        ),

        # ============ S5-S6: FLOW/INTEGRATED ============
        'flow': RealismType(
            name='Flow Realism',
            category='integrated',
            s_level_range=(5.0, 6.5),
            description='Reality as flowing process',
            operator_signature={'P_presence': 0.7, 'S_surrender': 0.6, 'Sh_shakti': 0.6},
            manifestation_style='fluid, effortless, adaptive',
            limitations=['May lack structure'],
            possibilities=['Effortless action', 'Flow states']
        ),
        'integrated': RealismType(
            name='Integrated Realism',
            category='integrated',
            s_level_range=(5.0, 6.5),
            description='Reality as integrated whole',
            operator_signature={'Co_coherence': 0.8, 'A_aware': 0.7, 'W_witness': 0.6},
            manifestation_style='wholistic, balanced, harmonious',
            limitations=['May miss specific details'],
            possibilities=['Integration', 'Balance', 'Harmony']
        ),
        'holistic': RealismType(
            name='Holistic Realism',
            category='integrated',
            s_level_range=(5.0, 6.5),
            description='Reality as unified field',
            operator_signature={'Co_coherence': 0.7, 'O_openness': 0.7, 'A_aware': 0.7},
            manifestation_style='inclusive, connecting, embracing',
            limitations=['May lack boundaries'],
            possibilities=['Wholeness experience', 'Unity perception']
        ),
        'intuitive': RealismType(
            name='Intuitive Realism',
            category='integrated',
            s_level_range=(5.0, 6.5),
            description='Reality through direct knowing',
            operator_signature={'A_aware': 0.7, 'W_witness': 0.6, 'O_openness': 0.7},
            manifestation_style='direct, knowing, immediate',
            limitations=['Hard to verify'],
            possibilities=['Direct insight', 'Wisdom']
        ),
        'creative': RealismType(
            name='Creative Realism',
            category='integrated',
            s_level_range=(5.0, 6.5),
            description='Reality as creative canvas',
            operator_signature={'M_manifest': 0.7, 'I_intention': 0.6, 'O_openness': 0.7},
            manifestation_style='generative, novel, expressive',
            limitations=['May lose grounding'],
            possibilities=['Creation', 'Innovation', 'Art']
        ),

        # ============ S6-S7: WITNESS/WISDOM ============
        'witness': RealismType(
            name='Witness Realism',
            category='wisdom',
            s_level_range=(6.0, 7.5),
            description='Reality observed without identification',
            operator_signature={'W_witness': 0.8, 'A_aware': 0.8, 'At_attachment': 0.2},
            manifestation_style='observing, non-reactive, clear',
            limitations=['May seem detached'],
            possibilities=['Clear seeing', 'Equanimity', 'Freedom']
        ),
        'wisdom': RealismType(
            name='Wisdom Realism',
            category='wisdom',
            s_level_range=(6.5, 8.0),
            description='Reality through wisdom lens',
            operator_signature={'W_witness': 0.8, 'A_aware': 0.8, 'G_grace': 0.7},
            manifestation_style='wise, discerning, knowing',
            limitations=['May seem slow to act'],
            possibilities=['Deep understanding', 'Right action']
        ),
        'transcendent': RealismType(
            name='Transcendent Realism',
            category='wisdom',
            s_level_range=(6.5, 8.0),
            description='Reality beyond ordinary limits',
            operator_signature={'V_void': 0.7, 'W_witness': 0.8, 'Psi_quality': 0.8},
            manifestation_style='beyond, unlimited, free',
            limitations=['Hard to communicate'],
            possibilities=['Transcendence', 'Liberation']
        ),

        # ============ S7-S8: UNITY/ABSOLUTE ============
        'unity': RealismType(
            name='Unity Realism',
            category='absolute',
            s_level_range=(7.0, 8.0),
            description='Reality as undivided whole',
            operator_signature={'Co_coherence': 0.9, 'V_void': 0.8, 'W_witness': 0.9},
            manifestation_style='unified, non-dual, complete',
            limitations=['Functioning in duality'],
            possibilities=['Unity consciousness', 'Oneness']
        ),
        'grace': RealismType(
            name='Grace Realism',
            category='absolute',
            s_level_range=(7.0, 8.0),
            description='Reality as grace flow',
            operator_signature={'G_grace': 0.9, 'S_surrender': 0.9, 'At_attachment': 0.1},
            manifestation_style='effortless, blessed, flowing',
            limitations=['None significant'],
            possibilities=['Divine flow', 'Miraculous manifestation']
        ),
        'universal': RealismType(
            name='Universal Realism',
            category='absolute',
            s_level_range=(7.5, 8.0),
            description='Reality as universal consciousness',
            operator_signature={'Psi_quality': 0.9, 'Co_coherence': 0.9, 'W_witness': 0.9},
            manifestation_style='universal, impersonal, cosmic',
            limitations=['Ordinary function'],
            possibilities=['Cosmic consciousness', 'Universal identity']
        ),
        'absolute': RealismType(
            name='Absolute Realism',
            category='absolute',
            s_level_range=(7.5, 8.0),
            description='Reality as absolute truth',
            operator_signature={'V_void': 0.9, 'W_witness': 0.95, 'Psi_quality': 0.95},
            manifestation_style='absolute, unchanging, eternal',
            limitations=['Communication'],
            possibilities=['Absolute realization', 'Complete freedom']
        )
    }

    # Category groupings
    CATEGORIES = {
        'biological': ['dirty', 'naturalistic', 'biological', 'survival', 'scarcity', 'material', 'physical', 'sensory'],
        'seeking': ['emotional', 'romantic', 'psychological', 'relational'],
        'achievement': ['social', 'economic', 'political', 'achievement', 'professional', 'competitive', 'strategic'],
        'service': ['service', 'purposeful', 'ethical', 'systemic'],
        'integrated': ['flow', 'integrated', 'holistic', 'intuitive', 'creative'],
        'wisdom': ['witness', 'wisdom', 'transcendent'],
        'absolute': ['unity', 'grace', 'universal', 'absolute']
    }

    def calculate_realism_profile(
        self,
        operators: Dict[str, float],
        s_level: float
    ) -> RealismProfile:
        """
        Calculate which realism types are active and their weights.

        ZERO-FALLBACK: Tracks missing operators, allows partial calculations.
        """
        # Calculate weight for each realism type
        realism_weights = {}
        all_missing: Set[str] = set()

        for name, realism in self.REALISM_TYPES.items():
            weight, missing = self._calculate_realism_weight(operators, s_level, realism)
            all_missing.update(missing)
            if weight is not None and weight > 0.1:  # Only include significant activations
                realism_weights[name] = weight

        # Normalize weights
        total_weight = sum(realism_weights.values())
        if total_weight > 0:
            realism_weights = {k: v / total_weight for k, v in realism_weights.items()}

        # Get active realisms (weight > threshold)
        active = [k for k, v in realism_weights.items() if v > 0.05]

        # Find dominant
        if realism_weights:
            dominant = max(realism_weights.items(), key=lambda x: x[1])
            dominant_name = dominant[0]
            dominant_weight = dominant[1]
        else:
            # ZERO-FALLBACK: Cannot determine dominant if no weights calculable
            dominant_name = None
            dominant_weight = None
            realism_weights = {}
            active = []

        # Calculate coherence (how well realisms integrate)
        coherence = self._calculate_realism_coherence(active) if active else None

        # Determine evolution direction
        evolution_direction = self._determine_evolution_direction(s_level, dominant_name) if dominant_name else "Cannot determine - insufficient data"

        # Recommend expansions
        recommended = self._recommend_realism_expansion(s_level, active)

        return RealismProfile(
            active_realisms=active,
            dominant_realism=dominant_name,
            dominant_weight=dominant_weight,
            realism_blend=realism_weights,
            coherence=coherence,
            evolution_direction=evolution_direction,
            recommended_expansion=recommended
        )

    def _calculate_realism_weight(
        self,
        operators: Dict[str, float],
        s_level: float,
        realism: RealismType
    ) -> Tuple[Optional[float], List[str]]:
        """
        Calculate how much a specific realism type is active.

        ZERO-FALLBACK: Returns (None, missing_ops) if required operators missing.
        """
        # S-level fit
        min_s, max_s = realism.s_level_range
        if s_level < min_s - 0.5 or s_level > max_s + 0.5:
            s_fit = 0.1  # Low fit outside range
        elif min_s <= s_level <= max_s:
            s_fit = 1.0  # Perfect fit within range
        else:
            # Partial fit in transition zones
            if s_level < min_s:
                s_fit = 0.5 + 0.5 * (s_level - (min_s - 0.5)) / 0.5
            else:
                s_fit = 0.5 + 0.5 * ((max_s + 0.5) - s_level) / 0.5

        # Operator signature match - ZERO-FALLBACK
        signature_match = 0.0
        matched_ops = 0
        missing_ops = []

        for op, expected in realism.operator_signature.items():
            actual = operators.get(op)
            if actual is None:
                missing_ops.append(op)
                continue
            # Closer to expected = higher match
            match = 1 - abs(actual - expected)
            signature_match += match
            matched_ops += 1

        # If all operators missing, return None
        if matched_ops == 0:
            return None, missing_ops

        # Allow partial calculation if some operators present
        signature_match /= matched_ops

        # Combined weight
        return s_fit * signature_match, missing_ops

    def _calculate_realism_coherence(self, active_realisms: List[str]) -> float:
        """Calculate how well active realisms integrate"""
        if len(active_realisms) <= 1:
            return 1.0

        # Get categories of active realisms
        categories = set()
        for realism in active_realisms:
            for cat, members in self.CATEGORIES.items():
                if realism in members:
                    categories.add(cat)
                    break

        # More categories = potentially less coherence
        # But adjacent categories are more coherent
        category_order = ['biological', 'seeking', 'achievement', 'service', 'integrated', 'wisdom', 'absolute']

        if len(categories) == 1:
            return 1.0

        # Calculate spread
        indices = [category_order.index(c) for c in categories if c in category_order]
        if not indices:
            return 0.5

        spread = max(indices) - min(indices)

        # Coherence decreases with spread
        coherence = 1.0 - (spread / len(category_order)) * 0.7

        return max(0.2, coherence)

    def _determine_evolution_direction(
        self,
        s_level: float,
        dominant_realism: str
    ) -> str:
        """Determine natural evolution direction"""
        realism = self.REALISM_TYPES.get(dominant_realism)
        if not realism:
            return "undefined"

        _, max_s = realism.s_level_range

        if s_level >= max_s:
            # Ready to move beyond this realism
            for cat, members in self.CATEGORIES.items():
                if dominant_realism in members:
                    cat_idx = list(self.CATEGORIES.keys()).index(cat)
                    if cat_idx < len(self.CATEGORIES) - 1:
                        next_cat = list(self.CATEGORIES.keys())[cat_idx + 1]
                        return f"Evolving toward {next_cat} realisms"
            return "Approaching absolute realism"
        else:
            return f"Deepening {realism.category} realism capacity"

    def _recommend_realism_expansion(
        self,
        s_level: float,
        active_realisms: List[str]
    ) -> List[str]:
        """Recommend realisms to develop"""
        recommendations = []

        # Find current categories
        current_cats = set()
        for realism in active_realisms:
            for cat, members in self.CATEGORIES.items():
                if realism in members:
                    current_cats.add(cat)

        # Suggest next level realisms
        category_order = ['biological', 'seeking', 'achievement', 'service', 'integrated', 'wisdom', 'absolute']

        for cat in current_cats:
            idx = category_order.index(cat) if cat in category_order else 0
            if idx < len(category_order) - 1:
                next_cat = category_order[idx + 1]
                # Find a realism in next category appropriate for S-level
                for realism_name in self.CATEGORIES.get(next_cat, []):
                    realism = self.REALISM_TYPES.get(realism_name)
                    if realism and realism.s_level_range[0] <= s_level + 0.5:
                        recommendations.append(realism_name)
                        break

        return recommendations[:3]

    def get_realism_details(self, realism_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a realism type"""
        realism = self.REALISM_TYPES.get(realism_name)
        if not realism:
            return None

        return {
            'name': realism.name,
            'category': realism.category,
            's_level_range': f"S{realism.s_level_range[0]:.1f} - S{realism.s_level_range[1]:.1f}",
            'description': realism.description,
            'manifestation_style': realism.manifestation_style,
            'limitations': realism.limitations,
            'possibilities': realism.possibilities,
            'key_operators': list(realism.operator_signature.keys())
        }

    def calculate_realism_blend(
        self,
        profile: RealismProfile,
        fractal_depth: float = 1.0,
        creator_coefficient: float = 1.0
    ) -> float:
        """
        Calculate blended realism strength.

        Formula: R_blend = Σ(R_i × w_i × d_i)^C
        Where:
        - R_i = realism type weight
        - w_i = operator alignment weight
        - d_i = fractal depth contribution
        - C = creator coefficient
        """
        blend = 0.0

        for realism_name, weight in profile.realism_blend.items():
            realism = self.REALISM_TYPES.get(realism_name)
            if not realism:
                continue

            # Fractal depth contribution varies by category
            depth_factor = fractal_depth
            if realism.category in ['wisdom', 'absolute']:
                depth_factor *= 1.2  # Higher realisms benefit more from depth
            elif realism.category in ['biological']:
                depth_factor *= 0.8  # Lower realisms benefit less

            blend += weight * depth_factor

        return blend ** creator_coefficient
