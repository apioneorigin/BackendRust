"""
Realism Engine - 77 Reality Types
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

from logging_config import get_logger
logger = get_logger('formulas.realism')


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

    # 77 Realism Types organized by S-level clusters
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
        'materialistic': RealismType(
            name='Materialistic Realism',
            category='biological',
            s_level_range=(1.0, 2.5),
            description='Reality as physical matter only, rejecting non-physical',
            operator_signature={'M_maya': 0.7, 'At_attachment': 0.7, 'Psi_quality': 0.2},
            manifestation_style='concrete, physical-only, measurable',
            limitations=['Misses spiritual dimensions', 'Reductionist worldview'],
            possibilities=['Practical accomplishment', 'Material mastery']
        ),
        'cynical': RealismType(
            name='Cynical Realism',
            category='biological',
            s_level_range=(1.5, 3.0),
            description='Reality filtered through distrust and negative expectations',
            operator_signature={'F_fear': 0.6, 'R_resistance': 0.7, 'O_openness': 0.2},
            manifestation_style='skeptical, defensive, self-protective',
            limitations=['Cannot trust', 'Misses opportunities'],
            possibilities=['Protection from exploitation', 'Realistic assessment']
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
        'status': RealismType(
            name='Status Realism',
            category='achievement',
            s_level_range=(2.5, 4.0),
            description='Reality as hierarchy and rank',
            operator_signature={'At_attachment': 0.7, 'I_intention': 0.6, 'Co_coherence': 0.5},
            manifestation_style='hierarchical, position-aware, status-seeking',
            limitations=['Constant comparison', 'Never satisfied'],
            possibilities=['Social intelligence', 'Strategic positioning']
        ),
        'pragmatic': RealismType(
            name='Pragmatic Realism',
            category='achievement',
            s_level_range=(2.5, 4.5),
            description='Reality as what works in practice',
            operator_signature={'I_intention': 0.6, 'A_aware': 0.5, 'M_manifest': 0.6},
            manifestation_style='practical, results-focused, adaptive',
            limitations=['May miss deeper meaning', 'Short-term focus'],
            possibilities=['Effective problem-solving', 'Practical wisdom']
        ),
        'merit': RealismType(
            name='Merit Realism',
            category='achievement',
            s_level_range=(3.0, 4.5),
            description='Reality as earned through skill and effort',
            operator_signature={'I_intention': 0.7, 'Sh_shakti': 0.6, 'D_dharma': 0.5},
            manifestation_style='achievement-based, fair, earned',
            limitations=['Ignores systemic factors', 'Judgmental'],
            possibilities=['Strong work ethic', 'Self-improvement']
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
        'interpersonal': RealismType(
            name='Interpersonal Realism',
            category='service',
            s_level_range=(3.5, 5.0),
            description='Reality through one-on-one human connection',
            operator_signature={'Se_service': 0.6, 'Co_coherence': 0.6, 'O_openness': 0.6},
            manifestation_style='relational, personal, connecting',
            limitations=['May neglect larger systems', 'Boundary challenges'],
            possibilities=['Deep connection', 'Trust building']
        ),
        'community': RealismType(
            name='Community Realism',
            category='service',
            s_level_range=(3.5, 5.0),
            description='Reality as collective wellbeing and shared resources',
            operator_signature={'Se_service': 0.7, 'Co_coherence': 0.7, 'At_attachment': 0.4},
            manifestation_style='communal, collaborative, supportive',
            limitations=['Groupthink risk', 'May suppress individuality'],
            possibilities=['Mutual support', 'Collective strength']
        ),
        'cultural': RealismType(
            name='Cultural Realism',
            category='service',
            s_level_range=(3.5, 5.5),
            description='Reality as shared values and traditions',
            operator_signature={'Co_coherence': 0.7, 'D_dharma': 0.5, 'A_aware': 0.5},
            manifestation_style='traditional, values-based, identity-forming',
            limitations=['May resist change', 'In-group bias'],
            possibilities=['Cultural continuity', 'Shared meaning']
        ),
        'empathic': RealismType(
            name='Empathic Realism',
            category='service',
            s_level_range=(4.0, 5.5),
            description='Reality through feeling others emotions and perspectives',
            operator_signature={'A_aware': 0.7, 'O_openness': 0.7, 'At_attachment': 0.3},
            manifestation_style='compassionate, resonant, understanding',
            limitations=['Emotional overwhelm', 'Boundary confusion'],
            possibilities=['Deep understanding', 'Compassionate action']
        ),
        'developmental': RealismType(
            name='Developmental Realism',
            category='service',
            s_level_range=(4.0, 5.5),
            description='Reality as continuous growth and evolution',
            operator_signature={'I_intention': 0.6, 'A_aware': 0.6, 'O_openness': 0.7},
            manifestation_style='growth-oriented, learning-focused, evolving',
            limitations=['Never arrived', 'Process addiction'],
            possibilities=['Continuous improvement', 'Self-actualization']
        ),
        'therapeutic': RealismType(
            name='Therapeutic Realism',
            category='service',
            s_level_range=(4.0, 5.5),
            description='Reality as healing journey and integration process',
            operator_signature={'A_aware': 0.7, 'W_witness': 0.5, 'O_openness': 0.6},
            manifestation_style='healing-oriented, integrative, compassionate',
            limitations=['Pathology focus', 'Never fully healed'],
            possibilities=['Deep healing', 'Shadow integration']
        ),
        'educational': RealismType(
            name='Educational Realism',
            category='service',
            s_level_range=(3.5, 5.0),
            description='Reality as learning opportunity and knowledge acquisition',
            operator_signature={'A_aware': 0.6, 'I_intention': 0.6, 'O_openness': 0.7},
            manifestation_style='curious, learning-focused, knowledge-seeking',
            limitations=['Endless seeking', 'Knowledge over wisdom'],
            possibilities=['Continuous learning', 'Skill mastery']
        ),
        'transformational': RealismType(
            name='Transformational Realism',
            category='service',
            s_level_range=(4.5, 6.0),
            description='Reality as metamorphosis and identity shift',
            operator_signature={'S_surrender': 0.6, 'A_aware': 0.7, 'O_openness': 0.7},
            manifestation_style='breakthrough-focused, metamorphic, evolving',
            limitations=['Destabilizing', 'Identity confusion'],
            possibilities=['Profound transformation', 'New becoming']
        ),
        'existential': RealismType(
            name='Existential Realism',
            category='service',
            s_level_range=(4.0, 6.0),
            description='Reality as meaning-seeking and authentic living',
            operator_signature={'D_dharma': 0.6, 'A_aware': 0.7, 'W_witness': 0.5},
            manifestation_style='meaning-seeking, authentic, questioning',
            limitations=['Existential anxiety', 'Meaning crisis'],
            possibilities=['Authentic existence', 'Purpose clarity']
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
        'dharmic': RealismType(
            name='Dharmic Realism',
            category='integrated',
            s_level_range=(4.5, 6.0),
            description='Reality as aligned natural path and right action',
            operator_signature={'D_dharma': 0.8, 'A_aware': 0.6, 'S_surrender': 0.5},
            manifestation_style='aligned, purposeful, harmonious',
            limitations=['May become rigid', 'Attachment to path'],
            possibilities=['Natural alignment', 'Right livelihood']
        ),
        'spiritual': RealismType(
            name='Spiritual Realism',
            category='integrated',
            s_level_range=(5.0, 7.0),
            description='Reality as non-physical consciousness and inner truth',
            operator_signature={'Psi_quality': 0.7, 'A_aware': 0.7, 'W_witness': 0.6},
            manifestation_style='inner-focused, transcendent, sacred',
            limitations=['May reject material world'],
            possibilities=['Spiritual awakening', 'Inner peace']
        ),
        'mystical': RealismType(
            name='Mystical Realism',
            category='integrated',
            s_level_range=(5.5, 8.0),
            description='Reality as direct ineffable experience beyond rational mind',
            operator_signature={'Psi_quality': 0.8, 'V_void': 0.6, 'W_witness': 0.7},
            manifestation_style='transcendent, ineffable, visionary',
            limitations=['Hard to communicate', 'May seem irrational'],
            possibilities=['Direct knowing', 'Mystical union']
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
        'ecological': RealismType(
            name='Ecological Realism',
            category='wisdom',
            s_level_range=(5.0, 7.0),
            description='Reality as interconnected natural systems and sustainability',
            operator_signature={'Co_coherence': 0.7, 'A_aware': 0.7, 'O_openness': 0.6},
            manifestation_style='interconnected, sustainable, nature-aware',
            limitations=['Overwhelmed by complexity'],
            possibilities=['Environmental harmony', 'Systems understanding']
        ),
        'non_dual': RealismType(
            name='Non-Dual Realism',
            category='wisdom',
            s_level_range=(6.5, 8.0),
            description='Reality as unity of subject and object',
            operator_signature={'W_witness': 0.9, 'V_void': 0.7, 'M_maya': 0.2},
            manifestation_style='unified, non-separate, advaitic',
            limitations=['Functioning in duality', 'Communication'],
            possibilities=['Non-dual awareness', 'Liberation']
        ),
        'eternal': RealismType(
            name='Eternal Realism',
            category='wisdom',
            s_level_range=(6.5, 8.0),
            description='Reality as timeless unchanging truth',
            operator_signature={'W_witness': 0.8, 'V_void': 0.7, 'Psi_quality': 0.8},
            manifestation_style='timeless, unchanging, eternal',
            limitations=['May deny change', 'Difficult to relate'],
            possibilities=['Eternal perspective', 'Peace beyond time']
        ),
        'void': RealismType(
            name='Void Realism',
            category='wisdom',
            s_level_range=(6.5, 8.0),
            description='Reality as emptiness and pure potential',
            operator_signature={'V_void': 0.9, 'W_witness': 0.8, 'At_attachment': 0.1},
            manifestation_style='empty, spacious, potential-filled',
            limitations=['May seem nihilistic', 'Hard to function'],
            possibilities=['Spacious freedom', 'Creative potential']
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
        ),
        'cosmic': RealismType(
            name='Cosmic Realism',
            category='absolute',
            s_level_range=(6.5, 8.0),
            description='Reality at universal/galactic scale and perspective',
            operator_signature={'Psi_quality': 0.8, 'W_witness': 0.8, 'Co_coherence': 0.8},
            manifestation_style='vast, cosmic, universal-scale',
            limitations=['Distant from everyday', 'Impersonal'],
            possibilities=['Cosmic perspective', 'Universal identity']
        ),
        'divine': RealismType(
            name='Divine Realism',
            category='absolute',
            s_level_range=(6.5, 8.0),
            description='Reality as sacred consciousness and holy perception',
            operator_signature={'G_grace': 0.9, 'Psi_quality': 0.8, 'S_surrender': 0.7},
            manifestation_style='sacred, holy, blessed',
            limitations=['May seem disconnected'],
            possibilities=['Divine connection', 'Sacred perception']
        ),
        'universal_love': RealismType(
            name='Universal Love Realism',
            category='absolute',
            s_level_range=(6.5, 8.0),
            description='Reality as unconditional love underlying all existence',
            operator_signature={'G_grace': 0.8, 'O_openness': 0.9, 'At_attachment': 0.1},
            manifestation_style='loving, unconditional, heart-centered',
            limitations=['May seem naive'],
            possibilities=['Unconditional love', 'Heart-based living']
        ),

        # ============ CROSS-DOMAIN REALISMS ============
        'scientific': RealismType(
            name='Scientific Realism',
            category='cross_domain',
            s_level_range=(2.0, 6.0),
            description='Reality as empirical evidence and reproducible observation',
            operator_signature={'A_aware': 0.7, 'W_witness': 0.5, 'M_maya': 0.3},
            manifestation_style='empirical, data-driven, methodical',
            limitations=['May miss subjective truth', 'Reductionist'],
            possibilities=['Objective understanding', 'Reliable knowledge']
        ),
        'probabilistic': RealismType(
            name='Probabilistic Realism',
            category='cross_domain',
            s_level_range=(3.0, 6.0),
            description='Reality as uncertainty, ranges, and statistical thinking',
            operator_signature={'A_aware': 0.6, 'O_openness': 0.6, 'W_witness': 0.5},
            manifestation_style='uncertain, range-based, statistical',
            limitations=['Paralysis by analysis', 'Never certain'],
            possibilities=['Risk awareness', 'Nuanced thinking']
        ),
        'technological': RealismType(
            name='Technological Realism',
            category='cross_domain',
            s_level_range=(2.0, 5.0),
            description='Reality mediated through technology and digital systems',
            operator_signature={'I_intention': 0.6, 'M_manifest': 0.6, 'A_aware': 0.5},
            manifestation_style='tech-mediated, digital, systemic',
            limitations=['Disconnection from nature', 'Tool dependency'],
            possibilities=['Leverage technology', 'Systematic solutions']
        ),
        'game_theoretic': RealismType(
            name='Game Theoretic Realism',
            category='cross_domain',
            s_level_range=(3.0, 5.5),
            description='Reality as strategic interaction and payoff optimization',
            operator_signature={'I_intention': 0.7, 'A_aware': 0.6, 'W_witness': 0.4},
            manifestation_style='strategic, game-like, equilibrium-seeking',
            limitations=['Overly calculated', 'Misses cooperation'],
            possibilities=['Strategic clarity', 'Optimal decisions']
        ),
        'systems': RealismType(
            name='Systems Realism',
            category='cross_domain',
            s_level_range=(4.0, 6.5),
            description='Reality as feedback loops and emergent complexity',
            operator_signature={'Co_coherence': 0.7, 'A_aware': 0.7, 'O_openness': 0.6},
            manifestation_style='systemic, interconnected, emergent',
            limitations=['Overwhelm by complexity'],
            possibilities=['Systems leverage', 'Pattern recognition']
        ),
        'historical': RealismType(
            name='Historical Realism',
            category='cross_domain',
            s_level_range=(3.0, 5.5),
            description='Reality shaped by past patterns and legacy forces',
            operator_signature={'A_aware': 0.6, 'Co_coherence': 0.5, 'At_attachment': 0.5},
            manifestation_style='past-aware, pattern-seeing, contextual',
            limitations=['Trapped in past', 'Fatalistic'],
            possibilities=['Historical wisdom', 'Pattern learning']
        ),
        'futures': RealismType(
            name='Futures Realism',
            category='cross_domain',
            s_level_range=(4.0, 6.0),
            description='Reality as multiple possible futures and scenario space',
            operator_signature={'I_intention': 0.7, 'A_aware': 0.6, 'O_openness': 0.7},
            manifestation_style='future-oriented, possibility-aware, visionary',
            limitations=['Detached from present', 'Speculation'],
            possibilities=['Strategic foresight', 'Visionary planning']
        ),

        # ============ SPECIALIZED REALISMS ============
        'poetic': RealismType(
            name='Poetic Realism',
            category='specialized',
            s_level_range=(4.0, 7.0),
            description='Reality as metaphoric truth and aesthetic expression',
            operator_signature={'A_aware': 0.6, 'O_openness': 0.8, 'Psi_quality': 0.6},
            manifestation_style='metaphoric, beautiful, expressive',
            limitations=['Impractical', 'Subjective'],
            possibilities=['Beauty perception', 'Artistic truth']
        ),
        'mythic': RealismType(
            name='Mythic Realism',
            category='specialized',
            s_level_range=(4.0, 7.0),
            description='Reality as archetypal patterns and hero journey',
            operator_signature={'A_aware': 0.6, 'D_dharma': 0.6, 'Psi_quality': 0.6},
            manifestation_style='archetypal, story-based, meaningful',
            limitations=['May impose narrative', 'Romantic'],
            possibilities=['Deep meaning', 'Archetypal guidance']
        ),
        'shamanic': RealismType(
            name='Shamanic Realism',
            category='specialized',
            s_level_range=(5.0, 8.0),
            description='Reality includes spirit world and energy dimensions',
            operator_signature={'Psi_quality': 0.7, 'Sh_shakti': 0.7, 'A_aware': 0.6},
            manifestation_style='spirit-connected, energy-aware, journeying',
            limitations=['May seem irrational', 'Cultural context needed'],
            possibilities=['Spirit guidance', 'Energy perception']
        ),
        'dream': RealismType(
            name='Dream Realism',
            category='specialized',
            s_level_range=(4.0, 7.0),
            description='Reality includes dream states and symbolic truth',
            operator_signature={'A_aware': 0.6, 'Psi_quality': 0.6, 'O_openness': 0.6},
            manifestation_style='symbolic, dreamlike, unconscious-aware',
            limitations=['Interpretation challenges', 'Subjective'],
            possibilities=['Unconscious wisdom', 'Symbol reading']
        ),
        'somatic': RealismType(
            name='Somatic Realism',
            category='specialized',
            s_level_range=(3.0, 6.0),
            description='Reality as felt sense and embodied wisdom',
            operator_signature={'P_presence': 0.7, 'A_aware': 0.6, 'Sh_shakti': 0.5},
            manifestation_style='body-based, felt-sense, embodied',
            limitations=['Hard to articulate', 'Culture-resistant'],
            possibilities=['Body wisdom', 'Embodied knowing']
        ),
        'trauma': RealismType(
            name='Trauma Realism',
            category='specialized',
            s_level_range=(1.5, 5.0),
            description='Reality filtered through past wounds and healing needs',
            operator_signature={'F_fear': 0.7, 'At_attachment': 0.6, 'R_resistance': 0.6},
            manifestation_style='wound-aware, protective, healing-focused',
            limitations=['Trigger sensitivity', 'Past-focused'],
            possibilities=['Trauma wisdom', 'Healing path clarity']
        ),
        'shadow': RealismType(
            name='Shadow Realism',
            category='specialized',
            s_level_range=(4.0, 6.5),
            description='Reality includes hidden forces and unconscious drivers',
            operator_signature={'A_aware': 0.7, 'W_witness': 0.6, 'O_openness': 0.5},
            manifestation_style='depth-aware, shadow-seeing, integrative',
            limitations=['Dark focus', 'May become cynical'],
            possibilities=['Shadow integration', 'Depth understanding']
        ),
        'paradoxical': RealismType(
            name='Paradoxical Realism',
            category='specialized',
            s_level_range=(5.5, 8.0),
            description='Reality embraces both/and and transcends contradiction',
            operator_signature={'A_aware': 0.7, 'W_witness': 0.7, 'Psi_quality': 0.7},
            manifestation_style='both-and, koan-like, transcendent',
            limitations=['Confusing', 'Hard to communicate'],
            possibilities=['Paradox resolution', 'Higher integration']
        ),
        'quantum': RealismType(
            name='Quantum Realism',
            category='specialized',
            s_level_range=(5.0, 8.0),
            description='Reality as observer-dependent probability collapse',
            operator_signature={'W_witness': 0.7, 'Psi_quality': 0.7, 'A_aware': 0.6},
            manifestation_style='probabilistic, observer-influenced, superposed',
            limitations=['Misapplication risk', 'Pseudoscience adjacent'],
            possibilities=['Creative reality shaping', 'Multiple possibility awareness']
        ),
        'chaos': RealismType(
            name='Chaos Realism',
            category='specialized',
            s_level_range=(4.0, 7.0),
            description='Reality as sensitive dependence and butterfly effects',
            operator_signature={'A_aware': 0.6, 'O_openness': 0.7, 'Co_coherence': 0.5},
            manifestation_style='complexity-aware, sensitive, adaptive',
            limitations=['Unpredictability anxiety', 'Hard to plan'],
            possibilities=['Leverage small actions', 'Embrace uncertainty']
        ),
        'fractal': RealismType(
            name='Fractal Realism',
            category='specialized',
            s_level_range=(5.0, 7.5),
            description='Reality as self-similar patterns across scales',
            operator_signature={'A_aware': 0.7, 'Co_coherence': 0.7, 'W_witness': 0.6},
            manifestation_style='pattern-seeing, scale-aware, recursive',
            limitations=['Pattern imposition', 'Over-abstraction'],
            possibilities=['Scale-independent wisdom', 'Pattern recognition']
        )
    }

    # Category groupings
    # Category groupings - Updated with all 77 realism types
    CATEGORIES = {
        'biological': [
            'dirty', 'naturalistic', 'biological', 'survival', 'scarcity',
            'material', 'physical', 'sensory', 'materialistic', 'cynical'
        ],
        'seeking': ['emotional', 'romantic', 'psychological', 'relational'],
        'achievement': [
            'social', 'economic', 'political', 'achievement', 'professional',
            'competitive', 'strategic', 'status', 'pragmatic', 'merit'
        ],
        'service': [
            'service', 'purposeful', 'ethical', 'systemic', 'interpersonal',
            'community', 'cultural', 'empathic', 'developmental', 'therapeutic',
            'educational', 'transformational', 'existential'
        ],
        'integrated': [
            'flow', 'integrated', 'holistic', 'intuitive', 'creative',
            'dharmic', 'spiritual', 'mystical'
        ],
        'wisdom': [
            'witness', 'wisdom', 'transcendent', 'ecological',
            'non_dual', 'eternal', 'void'
        ],
        'absolute': ['unity', 'grace', 'universal', 'absolute', 'cosmic', 'divine', 'universal_love'],
        'cross_domain': [
            'scientific', 'probabilistic', 'technological', 'game_theoretic',
            'systems', 'historical', 'futures'
        ],
        'specialized': [
            'poetic', 'mythic', 'shamanic', 'dream', 'somatic', 'trauma',
            'shadow', 'paradoxical', 'quantum', 'chaos', 'fractal'
        ]
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
        logger.debug(f"[calculate_realism_profile] s_level={s_level:.3f}, operators={len(operators)} keys")
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
            dominant_name = "unknown"
            dominant_weight = 0.0
            realism_weights = {}
            active = []

        # Calculate coherence (how well realisms integrate)
        coherence = self._calculate_realism_coherence(active) if active else None

        # Determine evolution direction
        evolution_direction = self._determine_evolution_direction(s_level, dominant_name) if dominant_name else "Cannot determine - insufficient data"

        # Recommend expansions
        recommended = self._recommend_realism_expansion(s_level, active)

        if all_missing:
            logger.warning(f"[calculate_realism_profile] missing operators: {len(all_missing)}")
        logger.debug(
            f"[calculate_realism_profile] result: dominant={dominant_name}, "
            f"dominant_weight={dominant_weight:.3f}, active={len(active)}, "
            f"coherence={coherence if coherence is not None else 'None'}"
        )

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

    def _calculate_realism_coherence(self, active_realisms: List[str]) -> Optional[float]:
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
        category_order = ['biological', 'seeking', 'achievement', 'service', 'integrated', 'wisdom', 'absolute', 'cross_domain', 'specialized']

        if len(categories) == 1:
            return 1.0

        # Calculate spread
        indices = [category_order.index(c) for c in categories if c in category_order]
        if not indices:
            return None

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
        category_order = ['biological', 'seeking', 'achievement', 'service', 'integrated', 'wisdom', 'absolute', 'cross_domain', 'specialized']

        for cat in current_cats:
            idx = category_order.index(cat) if cat in category_order else None
            if idx is not None and idx < len(category_order) - 1:
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
        logger.debug(
            f"[calculate_realism_blend] fractal_depth={fractal_depth:.3f}, "
            f"creator_coefficient={creator_coefficient:.3f}, "
            f"blend_entries={len(profile.realism_blend)}"
        )
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

        result = blend ** creator_coefficient
        logger.debug(f"[calculate_realism_blend] result: {result:.3f}")
        return result

    def get_semantic_description(self, realism_name: str, weight: float, context: str = 'general') -> str:
        """
        Get natural language description of a realism type for articulation.

        Args:
            realism_name: The key name of the realism type
            weight: The weight/activation level (0.0-1.0)
            context: Context type ('business', 'personal', 'spiritual', 'general')

        Returns:
            Human-readable description of how this realism manifests
        """
        logger.debug(f"[get_semantic_description] realism={realism_name}, weight={weight:.3f}, context={context}")
        if realism_name not in REALISM_SEMANTIC_DESCRIPTIONS:
            logger.warning(f"[get_semantic_description] missing description for realism '{realism_name}'")
            return f"{realism_name.replace('_', ' ').title()} is active"

        desc = REALISM_SEMANTIC_DESCRIPTIONS[realism_name]

        # Select context-appropriate description
        if context in desc:
            base = desc[context]
        else:
            base = desc.get('general')

        # Intensity modifiers based on weight
        if weight >= 0.8:
            intensity = "strongly"
        elif weight >= 0.6:
            intensity = "significantly"
        elif weight >= 0.4:
            intensity = "moderately"
        else:
            intensity = "somewhat"

        result = f"{intensity} {base}"
        logger.debug(f"[get_semantic_description] result: '{result[:80]}'")
        return result


# Semantic descriptions for natural language articulation
# Each realism has context-specific descriptions for different domains
REALISM_SEMANTIC_DESCRIPTIONS = {
    # S1-S2 BIOLOGICAL
    'dirty': {
        'general': 'seeing reality through raw, unfiltered survival needs',
        'business': 'operating from basic survival instincts, focused on immediate threats',
        'personal': 'experiencing life as raw physical struggle'
    },
    'naturalistic': {
        'general': 'perceiving reality through natural cycles and organic processes',
        'business': 'understanding market rhythms and natural growth patterns',
        'personal': 'living in harmony with natural rhythms'
    },
    'biological': {
        'general': 'experiencing reality through body and instinct',
        'business': 'trusting gut reactions and physical intuition',
        'personal': 'living from embodied wisdom'
    },
    'survival': {
        'general': 'filtering everything through threat/safety assessment',
        'business': 'every decision framed as survival-critical',
        'personal': 'living in constant vigilance mode'
    },
    'scarcity': {
        'general': 'seeing resources as fundamentally limited',
        'business': 'zero-sum thinking about markets and opportunities',
        'personal': 'hoarding mindset, fear of not having enough'
    },
    'material': {
        'general': 'valuing what is tangible and measurable',
        'business': 'focusing on concrete assets and bottom-line results',
        'personal': 'defining success by possessions'
    },
    'physical': {
        'general': 'trusting sensory experience above all',
        'business': 'demanding physical proof and tangible evidence',
        'personal': 'grounded in body and sensory world'
    },
    'sensory': {
        'general': 'experiencing reality through rich sensory perception',
        'business': 'attention to aesthetic and experiential quality',
        'personal': 'living through taste, touch, sight, sound'
    },
    'materialistic': {
        'general': 'seeing only physical matter as real',
        'business': 'dismissing intangibles, focusing only on measurable assets',
        'personal': 'meaning found through acquisition and possession'
    },
    'cynical': {
        'general': 'expecting the worst from people and situations',
        'business': 'assuming hidden agendas behind every deal',
        'personal': 'protective distrust as default orientation'
    },

    # S2-S3 SEEKING
    'emotional': {
        'general': 'reality colored by emotional states',
        'business': 'decisions driven by feelings about people and situations',
        'personal': 'life experienced through emotional lens'
    },
    'romantic': {
        'general': 'idealizing reality through longing and passion',
        'business': 'vision-driven, inspired by what could be',
        'personal': 'seeking perfect love and ideal connections'
    },
    'psychological': {
        'general': 'understanding reality through mental patterns',
        'business': 'analyzing motivations and psychological dynamics',
        'personal': 'self-aware, working with inner patterns'
    },
    'relational': {
        'general': 'reality defined through relationships',
        'business': 'success measured by relationship quality',
        'personal': 'identity formed through connections'
    },

    # S3-S4 ACHIEVEMENT
    'social': {
        'general': 'reality as social structures and roles',
        'business': 'navigating organizational hierarchies',
        'personal': 'identity defined by social position'
    },
    'economic': {
        'general': 'seeing reality through exchange and value',
        'business': 'everything has a price, optimizing transactions',
        'personal': 'measuring life in terms of economic value'
    },
    'political': {
        'general': 'perceiving power dynamics and influence',
        'business': 'aware of office politics and power plays',
        'personal': 'navigating social power structures'
    },
    'achievement': {
        'general': 'reality as goals to accomplish',
        'business': 'driven by targets, metrics, and milestones',
        'personal': 'self-worth tied to accomplishments'
    },
    'professional': {
        'general': 'identity through career and expertise',
        'business': 'credentialing and competence as currency',
        'personal': 'defining self through work role'
    },
    'competitive': {
        'general': 'framing everything as competition',
        'business': 'market share battles, winning against rivals',
        'personal': 'constantly comparing and competing'
    },
    'strategic': {
        'general': 'seeing reality as chess board to navigate',
        'business': 'long-term planning and positioning',
        'personal': 'life as strategy game'
    },
    'status': {
        'general': 'reality filtered through hierarchy and rank',
        'business': 'focused on position, title, prestige',
        'personal': 'worth measured by social standing'
    },
    'pragmatic': {
        'general': 'focused on what works in practice',
        'business': 'results over theory, practical solutions',
        'personal': 'no-nonsense approach to life'
    },
    'merit': {
        'general': 'believing outcomes reflect effort and skill',
        'business': 'meritocracy mindset, earned success',
        'personal': 'taking responsibility for results'
    },

    # S4-S5 SERVICE
    'service': {
        'general': 'reality as opportunity to contribute',
        'business': 'customer service as core value',
        'personal': 'fulfillment through helping others'
    },
    'purposeful': {
        'general': 'driven by sense of purpose',
        'business': 'mission-driven organization',
        'personal': 'life organized around meaningful purpose'
    },
    'ethical': {
        'general': 'reality through moral framework',
        'business': 'ethical business practices as priority',
        'personal': 'living by principles and values'
    },
    'systemic': {
        'general': 'seeing interconnected systems everywhere',
        'business': 'understanding organizational dynamics',
        'personal': 'aware of how everything connects'
    },
    'interpersonal': {
        'general': 'reality through one-on-one connection',
        'business': 'building individual relationships',
        'personal': 'depth in personal connections'
    },
    'community': {
        'general': 'reality as collective wellbeing',
        'business': 'community-building and shared resources',
        'personal': 'belonging to something larger'
    },
    'cultural': {
        'general': 'reality shaped by shared values and traditions',
        'business': 'organizational culture as key asset',
        'personal': 'identity through cultural participation'
    },
    'empathic': {
        'general': 'feeling others emotions and perspectives',
        'business': 'deep customer and employee understanding',
        'personal': 'living with compassionate awareness'
    },
    'developmental': {
        'general': 'seeing everything as growth opportunity',
        'business': 'continuous improvement mindset',
        'personal': 'life as learning journey'
    },
    'therapeutic': {
        'general': 'reality as healing journey',
        'business': 'organizational healing and culture repair',
        'personal': 'committed to inner work and integration'
    },
    'educational': {
        'general': 'reality as learning opportunity',
        'business': 'learning organization, knowledge management',
        'personal': 'curious, always studying'
    },
    'transformational': {
        'general': 'reality as metamorphosis and change',
        'business': 'leading organizational transformation',
        'personal': 'embracing identity shifts'
    },
    'existential': {
        'general': 'seeking authentic meaning in existence',
        'business': 'questioning purpose and authenticity',
        'personal': 'confronting life\'s big questions'
    },

    # S5-S6 INTEGRATED
    'flow': {
        'general': 'reality as effortless flowing process',
        'business': 'operating in flow states, effortless performance',
        'personal': 'living in the zone'
    },
    'integrated': {
        'general': 'reality as unified whole',
        'business': 'whole-systems approach, integration',
        'personal': 'living from wholeness'
    },
    'holistic': {
        'general': 'seeing the whole in every part',
        'business': 'holistic business approach',
        'personal': 'mind-body-spirit integration'
    },
    'intuitive': {
        'general': 'reality through direct knowing',
        'business': 'trusting intuitive business decisions',
        'personal': 'guided by inner knowing'
    },
    'creative': {
        'general': 'reality as creative canvas',
        'business': 'innovation and creative problem-solving',
        'personal': 'life as artistic expression'
    },
    'dharmic': {
        'general': 'living in alignment with natural path',
        'business': 'right livelihood, aligned business',
        'personal': 'following life purpose'
    },
    'spiritual': {
        'general': 'perceiving non-physical dimensions',
        'business': 'spiritual values in business',
        'personal': 'inner life as primary reality'
    },
    'mystical': {
        'general': 'experiencing reality beyond rational mind',
        'business': 'visionary leadership, inspired guidance',
        'personal': 'direct mystical experience'
    },

    # S6-S7 WISDOM
    'witness': {
        'general': 'observing reality without identification',
        'business': 'detached awareness of business dynamics',
        'personal': 'pure awareness, not caught in drama'
    },
    'wisdom': {
        'general': 'reality through wisdom lens',
        'business': 'wise leadership and decision-making',
        'personal': 'living from accumulated wisdom'
    },
    'transcendent': {
        'general': 'reality beyond ordinary limits',
        'business': 'transcending conventional business thinking',
        'personal': 'touching dimensions beyond ordinary'
    },
    'ecological': {
        'general': 'seeing reality as interconnected ecosystem',
        'business': 'sustainable, environmentally-conscious business',
        'personal': 'living in harmony with nature'
    },
    'non_dual': {
        'general': 'experiencing unity of subject and object',
        'business': 'dissolving us/them boundaries',
        'personal': 'living from non-separation'
    },
    'eternal': {
        'general': 'perceiving timeless unchanging truth',
        'business': 'building for eternity, timeless values',
        'personal': 'resting in what never changes'
    },
    'void': {
        'general': 'knowing emptiness as creative potential',
        'business': 'comfort with uncertainty and emptiness',
        'personal': 'spacious freedom beyond form'
    },

    # S7-S8 ABSOLUTE
    'unity': {
        'general': 'reality as undivided consciousness',
        'business': 'seeing oneness in all stakeholders',
        'personal': 'living from unity consciousness'
    },
    'grace': {
        'general': 'reality as divine grace flowing',
        'business': 'business as vessel for grace',
        'personal': 'living in gratitude and grace'
    },
    'universal': {
        'general': 'reality as universal consciousness',
        'business': 'global perspective, universal values',
        'personal': 'identity as universal self'
    },
    'absolute': {
        'general': 'touching absolute truth',
        'business': 'alignment with absolute principles',
        'personal': 'resting in the absolute'
    },
    'cosmic': {
        'general': 'reality at galactic/universal scale',
        'business': 'cosmic perspective on earthly affairs',
        'personal': 'awareness of cosmic context'
    },
    'divine': {
        'general': 'perceiving sacredness in everything',
        'business': 'business as sacred activity',
        'personal': 'seeing God in all'
    },
    'universal_love': {
        'general': 'reality as unconditional love',
        'business': 'love as business foundation',
        'personal': 'loving without conditions'
    },

    # CROSS-DOMAIN
    'scientific': {
        'general': 'relying on empirical evidence',
        'business': 'data-driven decision making',
        'personal': 'scientific approach to life'
    },
    'probabilistic': {
        'general': 'thinking in probabilities and ranges',
        'business': 'risk assessment and scenario planning',
        'personal': 'comfortable with uncertainty'
    },
    'technological': {
        'general': 'reality mediated through technology',
        'business': 'tech-first approach to solutions',
        'personal': 'digital native worldview'
    },
    'game_theoretic': {
        'general': 'seeing reality as strategic game',
        'business': 'game theory in negotiations',
        'personal': 'strategic interaction awareness'
    },
    'systems': {
        'general': 'perceiving feedback loops and emergence',
        'business': 'systems thinking in organizations',
        'personal': 'seeing how everything connects'
    },
    'historical': {
        'general': 'reality shaped by past patterns',
        'business': 'learning from business history',
        'personal': 'aware of historical forces'
    },
    'futures': {
        'general': 'seeing multiple possible futures',
        'business': 'scenario planning and foresight',
        'personal': 'future-oriented thinking'
    },

    # SPECIALIZED
    'poetic': {
        'general': 'perceiving metaphoric truth and beauty',
        'business': 'storytelling and narrative leadership',
        'personal': 'life as poetry'
    },
    'mythic': {
        'general': 'living archetypal patterns',
        'business': 'brand mythology and meaning',
        'personal': 'hero\'s journey awareness'
    },
    'shamanic': {
        'general': 'perceiving spirit world and energy',
        'business': 'energy awareness in organizations',
        'personal': 'spirit-connected living'
    },
    'dream': {
        'general': 'honoring dream reality and symbols',
        'business': 'vision and dream-inspired innovation',
        'personal': 'working with dreams'
    },
    'somatic': {
        'general': 'trusting body wisdom and felt sense',
        'business': 'embodied leadership',
        'personal': 'living from body knowing'
    },
    'trauma': {
        'general': 'reality filtered through past wounds',
        'business': 'trauma-informed organizational practices',
        'personal': 'healing-focused living'
    },
    'shadow': {
        'general': 'aware of hidden forces and projections',
        'business': 'shadow work in organizations',
        'personal': 'integrating rejected parts'
    },
    'paradoxical': {
        'general': 'embracing both/and over either/or',
        'business': 'holding paradox in leadership',
        'personal': 'comfort with contradiction'
    },
    'quantum': {
        'general': 'reality as observer-influenced probability',
        'business': 'quantum leadership principles',
        'personal': 'creating through observation'
    },
    'chaos': {
        'general': 'aware of sensitive dependence and emergence',
        'business': 'thriving in chaos and complexity',
        'personal': 'embracing unpredictability'
    },
    'fractal': {
        'general': 'seeing self-similar patterns across scales',
        'business': 'fractal organization design',
        'personal': 'pattern recognition mastery'
    }
}
