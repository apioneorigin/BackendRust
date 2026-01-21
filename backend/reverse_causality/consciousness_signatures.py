"""
Consciousness Signatures Library
Pre-computed templates mapping common goals to required consciousness configurations

Each signature specifies:
- Required operator values (minimums)
- Required matrix positions (transformation matrices)
- S-level requirements
- Key death processes that may be needed
- Grace dependency level
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import json
from pathlib import Path


@dataclass
class MatrixRequirement:
    """Required position on a transformation matrix"""
    matrix: str  # truth, love, power, freedom, creation, time, death
    minimum_stage: int  # 1-4
    description: str


@dataclass
class DeathRequirement:
    """Required death process for transformation"""
    death_type: str  # D1-D7
    intensity: float  # 0-1 how complete the death needs to be
    description: str


@dataclass
class ConsciousnessSignature:
    """Complete consciousness signature for a goal"""
    id: str
    name: str
    category: str  # wealth, relationships, health, spiritual, career, creative
    description: str

    # Operator requirements (minimum values)
    operator_minimums: Dict[str, float]

    # Operator ceilings (maximum values for blockers)
    operator_maximums: Dict[str, float]

    # Matrix requirements
    matrix_requirements: List[MatrixRequirement]

    # S-level requirement
    min_s_level: float
    optimal_s_level: float

    # Death requirements
    death_requirements: List[DeathRequirement]

    # Grace dependency (0 = effort-based, 1 = grace-required)
    grace_dependency: float

    # Time characteristics
    typical_timeline: str  # "days", "weeks", "months", "years"
    timeline_flexibility: float  # 0-1 how much timeline can compress

    # Related signatures (for progressive goals)
    prerequisite_signatures: List[str]
    enables_signatures: List[str]

    # Keywords for matching
    keywords: List[str]


class ConsciousnessSignatureLibrary:
    """
    Library of consciousness signatures for common transformation goals.
    """

    def __init__(self):
        """Initialize with built-in signatures"""
        self.signatures: Dict[str, ConsciousnessSignature] = {}
        self._load_builtin_signatures()

    def _load_builtin_signatures(self):
        """Load all built-in signatures"""

        # ============================================
        # WEALTH & ABUNDANCE SIGNATURES
        # ============================================

        self.signatures['wealth_foundation'] = ConsciousnessSignature(
            id='wealth_foundation',
            name='Wealth Foundation',
            category='wealth',
            description='Establish the consciousness base for sustainable wealth creation',
            operator_minimums={
                'I_intention': 0.7,
                'D_dharma': 0.6,
                'Se_service': 0.5,
                'Co_coherence': 0.6,
                'Tr_trust': 0.6
            },
            operator_maximums={
                'At_attachment': 0.4,
                'F_fear': 0.4,
                'M_maya': 0.5
            },
            matrix_requirements=[
                MatrixRequirement('power', 2, 'Move from victim to actor'),
                MatrixRequirement('truth', 2, 'See reality clearly')
            ],
            min_s_level=3.0,
            optimal_s_level=4.5,
            death_requirements=[
                DeathRequirement('D2', 0.5, 'Release limiting beliefs about money')
            ],
            grace_dependency=0.3,
            typical_timeline='months',
            timeline_flexibility=0.4,
            prerequisite_signatures=[],
            enables_signatures=['wealth_growth', 'wealth_mastery'],
            keywords=['money', 'income', 'financial', 'prosperity', 'abundance', 'wealth']
        )

        self.signatures['wealth_growth'] = ConsciousnessSignature(
            id='wealth_growth',
            name='Wealth Growth',
            category='wealth',
            description='Expand wealth through aligned action and value creation',
            operator_minimums={
                'I_intention': 0.75,
                'D_dharma': 0.7,
                'Se_service': 0.65,
                'Co_coherence': 0.7,
                'Sh_shakti': 0.6,
                'O_openness': 0.6
            },
            operator_maximums={
                'At_attachment': 0.35,
                'F_fear': 0.35,
                'R_resistance': 0.4
            },
            matrix_requirements=[
                MatrixRequirement('power', 3, 'Achieve co-creator stage'),
                MatrixRequirement('creation', 2, 'Move to active creation')
            ],
            min_s_level=4.0,
            optimal_s_level=5.0,
            death_requirements=[
                DeathRequirement('D2', 0.7, 'Deep release of scarcity beliefs'),
                DeathRequirement('D4', 0.5, 'Release attachment to specific outcomes')
            ],
            grace_dependency=0.4,
            typical_timeline='months',
            timeline_flexibility=0.5,
            prerequisite_signatures=['wealth_foundation'],
            enables_signatures=['wealth_mastery'],
            keywords=['growth', 'expansion', 'scale', 'business', 'investment', 'revenue']
        )

        self.signatures['wealth_mastery'] = ConsciousnessSignature(
            id='wealth_mastery',
            name='Wealth Mastery',
            category='wealth',
            description='Achieve effortless abundance through consciousness alignment',
            operator_minimums={
                'I_intention': 0.8,
                'D_dharma': 0.8,
                'Se_service': 0.75,
                'G_grace': 0.7,
                'S_surrender': 0.65,
                'Co_coherence': 0.8
            },
            operator_maximums={
                'At_attachment': 0.25,
                'F_fear': 0.25,
                'M_maya': 0.3
            },
            matrix_requirements=[
                MatrixRequirement('power', 4, 'Achieve mastery stage'),
                MatrixRequirement('freedom', 3, 'Inner freedom from outcomes')
            ],
            min_s_level=5.0,
            optimal_s_level=6.0,
            death_requirements=[
                DeathRequirement('D2', 0.9, 'Complete release of money beliefs'),
                DeathRequirement('D4', 0.7, 'Non-attachment to wealth itself'),
                DeathRequirement('D5', 0.5, 'Release need to control outcomes')
            ],
            grace_dependency=0.6,
            typical_timeline='years',
            timeline_flexibility=0.3,
            prerequisite_signatures=['wealth_growth'],
            enables_signatures=[],
            keywords=['mastery', 'effortless', 'flow', 'legacy', 'impact']
        )

        # ============================================
        # RELATIONSHIP SIGNATURES
        # ============================================

        self.signatures['relationship_healing'] = ConsciousnessSignature(
            id='relationship_healing',
            name='Relationship Healing',
            category='relationships',
            description='Heal relationship patterns and open to authentic connection',
            operator_minimums={
                'O_openness': 0.6,
                'Tr_trust': 0.55,
                'A_aware': 0.6,
                'E_equanimity': 0.5
            },
            operator_maximums={
                'F_fear': 0.45,
                'At_attachment': 0.5,
                'R_resistance': 0.45
            },
            matrix_requirements=[
                MatrixRequirement('love', 2, 'Move toward acceptance'),
                MatrixRequirement('truth', 2, 'See self and other clearly')
            ],
            min_s_level=3.0,
            optimal_s_level=4.0,
            death_requirements=[
                DeathRequirement('D3', 0.6, 'Release painful emotional patterns'),
                DeathRequirement('D2', 0.5, 'Release beliefs about relationships')
            ],
            grace_dependency=0.4,
            typical_timeline='months',
            timeline_flexibility=0.4,
            prerequisite_signatures=[],
            enables_signatures=['relationship_deepening', 'soulmate_attraction'],
            keywords=['relationship', 'healing', 'connection', 'intimacy', 'partner', 'love']
        )

        self.signatures['relationship_deepening'] = ConsciousnessSignature(
            id='relationship_deepening',
            name='Relationship Deepening',
            category='relationships',
            description='Deepen existing relationship into profound connection',
            operator_minimums={
                'O_openness': 0.75,
                'Tr_trust': 0.7,
                'Se_service': 0.65,
                'P_presence': 0.7,
                'E_equanimity': 0.6
            },
            operator_maximums={
                'F_fear': 0.35,
                'At_attachment': 0.4,
                'R_resistance': 0.35
            },
            matrix_requirements=[
                MatrixRequirement('love', 3, 'Unconditional love stage'),
                MatrixRequirement('truth', 3, 'Deep honesty and transparency')
            ],
            min_s_level=4.0,
            optimal_s_level=5.0,
            death_requirements=[
                DeathRequirement('D3', 0.7, 'Release protective emotional walls'),
                DeathRequirement('D4', 0.6, 'Release attachment to how partner should be')
            ],
            grace_dependency=0.5,
            typical_timeline='months',
            timeline_flexibility=0.5,
            prerequisite_signatures=['relationship_healing'],
            enables_signatures=['relationship_unity'],
            keywords=['deep', 'intimate', 'profound', 'marriage', 'partnership']
        )

        self.signatures['soulmate_attraction'] = ConsciousnessSignature(
            id='soulmate_attraction',
            name='Soulmate Attraction',
            category='relationships',
            description='Attract a deeply compatible partner through resonance',
            operator_minimums={
                'O_openness': 0.7,
                'Rs_resonance': 0.65,
                'D_dharma': 0.6,
                'J_joy': 0.6,
                'Co_coherence': 0.65
            },
            operator_maximums={
                'F_fear': 0.4,
                'At_attachment': 0.45,
                'M_maya': 0.45
            },
            matrix_requirements=[
                MatrixRequirement('love', 2, 'Open heart space'),
                MatrixRequirement('creation', 2, 'Active creation mode')
            ],
            min_s_level=3.5,
            optimal_s_level=4.5,
            death_requirements=[
                DeathRequirement('D2', 0.6, 'Release beliefs about being unlovable'),
                DeathRequirement('D4', 0.5, 'Release attachment to specific person type')
            ],
            grace_dependency=0.6,
            typical_timeline='months',
            timeline_flexibility=0.6,
            prerequisite_signatures=['relationship_healing'],
            enables_signatures=['relationship_deepening'],
            keywords=['soulmate', 'attract', 'partner', 'dating', 'love', 'romance']
        )

        # ============================================
        # CAREER & PURPOSE SIGNATURES
        # ============================================

        self.signatures['career_clarity'] = ConsciousnessSignature(
            id='career_clarity',
            name='Career Clarity',
            category='career',
            description='Discover authentic career direction aligned with dharma',
            operator_minimums={
                'D_dharma': 0.65,
                'A_aware': 0.6,
                'W_witness': 0.55,
                'I_intention': 0.6
            },
            operator_maximums={
                'M_maya': 0.45,
                'F_fear': 0.45,
                'Hf_habit': 0.5
            },
            matrix_requirements=[
                MatrixRequirement('truth', 2, 'See through illusions about self'),
                MatrixRequirement('freedom', 2, 'Freedom from others expectations')
            ],
            min_s_level=3.5,
            optimal_s_level=4.5,
            death_requirements=[
                DeathRequirement('D1', 0.5, 'Release outdated identity'),
                DeathRequirement('D2', 0.5, 'Release beliefs about what you should do')
            ],
            grace_dependency=0.4,
            typical_timeline='weeks',
            timeline_flexibility=0.5,
            prerequisite_signatures=[],
            enables_signatures=['career_transition', 'leadership_emergence'],
            keywords=['career', 'purpose', 'calling', 'direction', 'job', 'work']
        )

        self.signatures['career_transition'] = ConsciousnessSignature(
            id='career_transition',
            name='Career Transition',
            category='career',
            description='Successfully navigate major career change',
            operator_minimums={
                'I_intention': 0.7,
                'D_dharma': 0.65,
                'Tr_trust': 0.6,
                'V_void': 0.5,
                'Sh_shakti': 0.6
            },
            operator_maximums={
                'F_fear': 0.4,
                'At_attachment': 0.45,
                'R_resistance': 0.4
            },
            matrix_requirements=[
                MatrixRequirement('death', 2, 'Acceptance of endings'),
                MatrixRequirement('creation', 2, 'Active creation of new')
            ],
            min_s_level=3.5,
            optimal_s_level=4.5,
            death_requirements=[
                DeathRequirement('D1', 0.7, 'Release old professional identity'),
                DeathRequirement('D4', 0.5, 'Release attachment to status/security')
            ],
            grace_dependency=0.5,
            typical_timeline='months',
            timeline_flexibility=0.4,
            prerequisite_signatures=['career_clarity'],
            enables_signatures=['leadership_emergence'],
            keywords=['transition', 'change', 'new', 'pivot', 'switch', 'career']
        )

        self.signatures['leadership_emergence'] = ConsciousnessSignature(
            id='leadership_emergence',
            name='Leadership Emergence',
            category='career',
            description='Step into authentic leadership presence',
            operator_minimums={
                'I_intention': 0.75,
                'W_witness': 0.65,
                'Se_service': 0.7,
                'Co_coherence': 0.7,
                'P_presence': 0.65
            },
            operator_maximums={
                'F_fear': 0.35,
                'At_attachment': 0.4,
                'M_maya': 0.4
            },
            matrix_requirements=[
                MatrixRequirement('power', 3, 'Co-creator leadership'),
                MatrixRequirement('truth', 3, 'Authentic expression')
            ],
            min_s_level=4.5,
            optimal_s_level=5.5,
            death_requirements=[
                DeathRequirement('D1', 0.6, 'Release limited self-image'),
                DeathRequirement('D5', 0.5, 'Release need to control others')
            ],
            grace_dependency=0.5,
            typical_timeline='months',
            timeline_flexibility=0.4,
            prerequisite_signatures=['career_clarity'],
            enables_signatures=[],
            keywords=['leadership', 'leader', 'influence', 'vision', 'team', 'CEO']
        )

        # ============================================
        # SPIRITUAL SIGNATURES
        # ============================================

        self.signatures['awakening_initiation'] = ConsciousnessSignature(
            id='awakening_initiation',
            name='Awakening Initiation',
            category='spiritual',
            description='Begin the conscious awakening journey',
            operator_minimums={
                'A_aware': 0.6,
                'W_witness': 0.5,
                'P_presence': 0.55,
                'O_openness': 0.6
            },
            operator_maximums={
                'M_maya': 0.5,
                'At_attachment': 0.5,
                'Hf_habit': 0.5
            },
            matrix_requirements=[
                MatrixRequirement('truth', 2, 'Beginning to see through illusion')
            ],
            min_s_level=3.0,
            optimal_s_level=4.0,
            death_requirements=[
                DeathRequirement('D2', 0.4, 'Question core beliefs')
            ],
            grace_dependency=0.5,
            typical_timeline='months',
            timeline_flexibility=0.5,
            prerequisite_signatures=[],
            enables_signatures=['awakening_deepening', 'witness_stabilization'],
            keywords=['awakening', 'spiritual', 'consciousness', 'awareness', 'enlightenment']
        )

        self.signatures['witness_stabilization'] = ConsciousnessSignature(
            id='witness_stabilization',
            name='Witness Stabilization',
            category='spiritual',
            description='Stabilize witness consciousness as default state',
            operator_minimums={
                'W_witness': 0.75,
                'A_aware': 0.7,
                'P_presence': 0.7,
                'E_equanimity': 0.65
            },
            operator_maximums={
                'At_attachment': 0.35,
                'R_resistance': 0.35,
                'M_maya': 0.4
            },
            matrix_requirements=[
                MatrixRequirement('truth', 3, 'Clear seeing'),
                MatrixRequirement('freedom', 3, 'Inner freedom established')
            ],
            min_s_level=5.0,
            optimal_s_level=6.0,
            death_requirements=[
                DeathRequirement('D1', 0.7, 'Substantial identity dissolution'),
                DeathRequirement('D6', 0.5, 'Beginning of separation dissolution')
            ],
            grace_dependency=0.6,
            typical_timeline='years',
            timeline_flexibility=0.3,
            prerequisite_signatures=['awakening_initiation'],
            enables_signatures=['unity_realization'],
            keywords=['witness', 'observer', 'presence', 'awareness', 'meditation']
        )

        self.signatures['unity_realization'] = ConsciousnessSignature(
            id='unity_realization',
            name='Unity Realization',
            category='spiritual',
            description='Direct realization of non-dual unity consciousness',
            operator_minimums={
                'W_witness': 0.85,
                'A_aware': 0.85,
                'G_grace': 0.8,
                'S_surrender': 0.8,
                'V_void': 0.75,
                'Co_coherence': 0.85
            },
            operator_maximums={
                'At_attachment': 0.2,
                'M_maya': 0.25,
                'R_resistance': 0.2
            },
            matrix_requirements=[
                MatrixRequirement('truth', 4, 'Complete clarity'),
                MatrixRequirement('love', 4, 'Universal love'),
                MatrixRequirement('freedom', 4, 'Absolute freedom')
            ],
            min_s_level=7.0,
            optimal_s_level=8.0,
            death_requirements=[
                DeathRequirement('D6', 0.9, 'Complete dissolution of separation'),
                DeathRequirement('D7', 0.8, 'Ego death')
            ],
            grace_dependency=0.9,
            typical_timeline='years',
            timeline_flexibility=0.2,
            prerequisite_signatures=['witness_stabilization'],
            enables_signatures=[],
            keywords=['unity', 'non-dual', 'enlightenment', 'liberation', 'moksha', 'samadhi']
        )

        # ============================================
        # HEALTH & VITALITY SIGNATURES
        # ============================================

        self.signatures['health_restoration'] = ConsciousnessSignature(
            id='health_restoration',
            name='Health Restoration',
            category='health',
            description='Restore physical health through consciousness alignment',
            operator_minimums={
                'P_presence': 0.6,
                'J_joy': 0.55,
                'Sh_shakti': 0.6,
                'A_aware': 0.55
            },
            operator_maximums={
                'F_fear': 0.45,
                'R_resistance': 0.45,
                'Hf_habit': 0.5
            },
            matrix_requirements=[
                MatrixRequirement('truth', 2, 'Honest about health patterns')
            ],
            min_s_level=3.0,
            optimal_s_level=4.0,
            death_requirements=[
                DeathRequirement('D2', 0.5, 'Release beliefs about illness'),
                DeathRequirement('D3', 0.5, 'Release emotional holding in body')
            ],
            grace_dependency=0.4,
            typical_timeline='months',
            timeline_flexibility=0.4,
            prerequisite_signatures=[],
            enables_signatures=['vitality_optimization'],
            keywords=['health', 'healing', 'recovery', 'illness', 'body', 'wellness']
        )

        self.signatures['vitality_optimization'] = ConsciousnessSignature(
            id='vitality_optimization',
            name='Vitality Optimization',
            category='health',
            description='Optimize energy and vitality for peak performance',
            operator_minimums={
                'Sh_shakti': 0.75,
                'J_joy': 0.7,
                'P_presence': 0.7,
                'Co_coherence': 0.65
            },
            operator_maximums={
                'F_fear': 0.35,
                'R_resistance': 0.35,
                'Hf_habit': 0.4
            },
            matrix_requirements=[
                MatrixRequirement('power', 3, 'Energy mastery'),
                MatrixRequirement('creation', 3, 'Creative energy flow')
            ],
            min_s_level=4.0,
            optimal_s_level=5.0,
            death_requirements=[
                DeathRequirement('D2', 0.6, 'Release limiting beliefs about aging'),
                DeathRequirement('D4', 0.5, 'Release attachment to comfort')
            ],
            grace_dependency=0.4,
            typical_timeline='months',
            timeline_flexibility=0.5,
            prerequisite_signatures=['health_restoration'],
            enables_signatures=[],
            keywords=['vitality', 'energy', 'performance', 'peak', 'strength', 'stamina']
        )

        # ============================================
        # CREATIVE SIGNATURES
        # ============================================

        self.signatures['creative_unblocking'] = ConsciousnessSignature(
            id='creative_unblocking',
            name='Creative Unblocking',
            category='creative',
            description='Remove blocks to creative expression',
            operator_minimums={
                'O_openness': 0.65,
                'J_joy': 0.6,
                'V_void': 0.5,
                'P_presence': 0.55
            },
            operator_maximums={
                'F_fear': 0.4,
                'R_resistance': 0.4,
                'Hf_habit': 0.45
            },
            matrix_requirements=[
                MatrixRequirement('creation', 2, 'Active creation begins'),
                MatrixRequirement('freedom', 2, 'Freedom from judgment')
            ],
            min_s_level=3.5,
            optimal_s_level=4.5,
            death_requirements=[
                DeathRequirement('D2', 0.5, 'Release beliefs about creative ability'),
                DeathRequirement('D3', 0.4, 'Release fear of judgment')
            ],
            grace_dependency=0.4,
            typical_timeline='weeks',
            timeline_flexibility=0.5,
            prerequisite_signatures=[],
            enables_signatures=['creative_flow', 'creative_mastery'],
            keywords=['creative', 'block', 'art', 'writing', 'expression', 'creativity']
        )

        self.signatures['creative_flow'] = ConsciousnessSignature(
            id='creative_flow',
            name='Creative Flow',
            category='creative',
            description='Access sustained creative flow states',
            operator_minimums={
                'O_openness': 0.75,
                'J_joy': 0.7,
                'V_void': 0.65,
                'P_presence': 0.7,
                'Sh_shakti': 0.65
            },
            operator_maximums={
                'F_fear': 0.3,
                'R_resistance': 0.3,
                'At_attachment': 0.35
            },
            matrix_requirements=[
                MatrixRequirement('creation', 3, 'Effortless creation'),
                MatrixRequirement('freedom', 3, 'Creative freedom')
            ],
            min_s_level=4.5,
            optimal_s_level=5.5,
            death_requirements=[
                DeathRequirement('D1', 0.5, 'Release identity as non-creative'),
                DeathRequirement('D4', 0.6, 'Release attachment to outcomes')
            ],
            grace_dependency=0.5,
            typical_timeline='months',
            timeline_flexibility=0.5,
            prerequisite_signatures=['creative_unblocking'],
            enables_signatures=['creative_mastery'],
            keywords=['flow', 'inspiration', 'muse', 'channel', 'genius', 'creative']
        )

    def get_signature(self, signature_id: str) -> Optional[ConsciousnessSignature]:
        """Get a signature by ID"""
        return self.signatures.get(signature_id)

    def find_signatures_for_goal(
        self,
        goal_text: str,
        current_s_level: float = 3.0
    ) -> List[ConsciousnessSignature]:
        """
        Find matching signatures for a goal description.

        Args:
            goal_text: Natural language goal description
            current_s_level: Current S-level for filtering achievable signatures

        Returns:
            List of matching signatures, sorted by relevance
        """
        goal_lower = goal_text.lower()
        matches = []

        for sig in self.signatures.values():
            # Calculate keyword match score
            keyword_matches = sum(
                1 for kw in sig.keywords
                if kw in goal_lower
            )

            if keyword_matches > 0:
                # Check S-level accessibility
                s_level_gap = sig.min_s_level - current_s_level
                accessible = s_level_gap <= 1.5  # Can reach 1.5 levels up

                # Calculate relevance score
                relevance = keyword_matches * 10
                if accessible:
                    relevance += 20
                if s_level_gap <= 0:
                    relevance += 10

                matches.append((sig, relevance))

        # Sort by relevance
        matches.sort(key=lambda x: -x[1])

        return [sig for sig, _ in matches]

    def find_signatures_by_category(self, category: str) -> List[ConsciousnessSignature]:
        """Get all signatures in a category"""
        return [
            sig for sig in self.signatures.values()
            if sig.category == category
        ]

    def get_prerequisite_chain(
        self,
        target_signature_id: str
    ) -> List[ConsciousnessSignature]:
        """
        Get the full chain of prerequisites for a signature.
        """
        target = self.signatures.get(target_signature_id)
        if not target:
            return []

        chain = []
        visited = set()

        def collect_prereqs(sig_id: str):
            if sig_id in visited:
                return
            visited.add(sig_id)

            sig = self.signatures.get(sig_id)
            if sig:
                for prereq_id in sig.prerequisite_signatures:
                    collect_prereqs(prereq_id)
                chain.append(sig)

        collect_prereqs(target_signature_id)
        return chain

    def get_all_categories(self) -> List[str]:
        """Get list of all signature categories"""
        categories = set(sig.category for sig in self.signatures.values())
        return sorted(list(categories))

    def get_all_signature_ids(self) -> List[str]:
        """Get list of all signature IDs"""
        return list(self.signatures.keys())

    def export_to_json(self, filepath: str):
        """Export all signatures to JSON file"""
        export_data = {}

        for sig_id, sig in self.signatures.items():
            export_data[sig_id] = {
                'id': sig.id,
                'name': sig.name,
                'category': sig.category,
                'description': sig.description,
                'operator_minimums': sig.operator_minimums,
                'operator_maximums': sig.operator_maximums,
                'matrix_requirements': [
                    {'matrix': mr.matrix, 'minimum_stage': mr.minimum_stage, 'description': mr.description}
                    for mr in sig.matrix_requirements
                ],
                'min_s_level': sig.min_s_level,
                'optimal_s_level': sig.optimal_s_level,
                'death_requirements': [
                    {'death_type': dr.death_type, 'intensity': dr.intensity, 'description': dr.description}
                    for dr in sig.death_requirements
                ],
                'grace_dependency': sig.grace_dependency,
                'typical_timeline': sig.typical_timeline,
                'timeline_flexibility': sig.timeline_flexibility,
                'prerequisite_signatures': sig.prerequisite_signatures,
                'enables_signatures': sig.enables_signatures,
                'keywords': sig.keywords
            }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
