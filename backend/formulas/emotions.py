"""
Emotion Component Formulas
20+ emotions with component breakdowns and 9 Rasas

Rasas (aesthetic emotions):
1. Shringara - Love/beauty/romance
2. Hasya - Joy/humor/laughter
3. Karuna - Compassion/sadness
4. Raudra - Anger/fury
5. Veera - Courage/heroism
6. Bhayanaka - Fear/terror
7. Adbhuta - Wonder/amazement
8. Shanta - Peace/tranquility
9. Bibhatsa - Disgust/aversion

Each emotion is derived from operator combinations.
"""

from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
import math


@dataclass
class EmotionState:
    """A single emotion's state"""
    name: str
    sanskrit: str
    intensity: float  # 0.0-1.0
    valence: str      # positive, negative, neutral
    components: Dict[str, float]
    description: str


@dataclass
class EmotionalProfile:
    """Complete emotional profile"""
    rasas: Dict[str, EmotionState]
    secondary_emotions: Dict[str, EmotionState]
    dominant_rasa: str
    emotional_coherence: float
    guna_influence: Dict[str, float]


class EmotionAnalyzer:
    """
    Analyze emotional states from consciousness operators.
    Calculates 9 rasas and 20+ secondary emotions.
    """

    # Rasa definitions with operator weights
    RASAS = {
        'shringara': {
            'sanskrit': 'Shringara',
            'english': 'Love/Beauty',
            'valence': 'positive',
            'operators': {
                'L_love': 1.0,
                'O_openness': 0.7,
                'G_grace': 0.5,
                'At_attachment': 0.3,  # Some attachment creates longing
                'P_presence': 0.4
            }
        },
        'hasya': {
            'sanskrit': 'Hasya',
            'english': 'Joy/Humor',
            'valence': 'positive',
            'operators': {
                'J_joy': 1.0,
                'Ce_celebration': 0.8,
                'O_openness': 0.6,
                'P_presence': 0.5,
                'F_fear': -0.4  # Fear diminishes joy
            }
        },
        'karuna': {
            'sanskrit': 'Karuna',
            'english': 'Compassion',
            'valence': 'neutral',
            'operators': {
                'Se_service': 0.9,
                'A_aware': 0.7,
                'O_openness': 0.6,
                'At_attachment': -0.3,  # Detached compassion is purer
                'W_witness': 0.4
            }
        },
        'raudra': {
            'sanskrit': 'Raudra',
            'english': 'Anger/Fury',
            'valence': 'negative',
            'operators': {
                'R_resistance': 0.8,
                'I_intention': 0.6,  # Frustrated intention
                'At_attachment': 0.5,
                'S_surrender': -0.7,  # Opposite of surrender
                'F_fear': 0.3
            }
        },
        'veera': {
            'sanskrit': 'Veera',
            'english': 'Courage',
            'valence': 'positive',
            'operators': {
                'I_intention': 0.9,
                'Sh_shakti': 0.8,
                'F_fear': -0.6,  # Courage transcends fear
                'D_dharma': 0.5,
                'Tr_trust': 0.4
            }
        },
        'bhayanaka': {
            'sanskrit': 'Bhayanaka',
            'english': 'Fear/Terror',
            'valence': 'negative',
            'operators': {
                'F_fear': 1.0,
                'M_maya': 0.6,
                'At_attachment': 0.5,
                'Tr_trust': -0.6,
                'G_grace': -0.4
            }
        },
        'adbhuta': {
            'sanskrit': 'Adbhuta',
            'english': 'Wonder/Amazement',
            'valence': 'positive',
            'operators': {
                'O_openness': 0.9,
                'A_aware': 0.7,
                'P_presence': 0.6,
                'Hf_habit': -0.5,  # Novelty vs habit
                'W_witness': 0.4
            }
        },
        'shanta': {
            'sanskrit': 'Shanta',
            'english': 'Peace/Tranquility',
            'valence': 'positive',
            'operators': {
                'E_equanimity': 1.0,
                'S_surrender': 0.8,
                'P_presence': 0.7,
                'R_resistance': -0.6,
                'Co_coherence': 0.5
            }
        },
        'bibhatsa': {
            'sanskrit': 'Bibhatsa',
            'english': 'Disgust/Aversion',
            'valence': 'negative',
            'operators': {
                'Av_aversion': 0.9 if 'Av_aversion' else 0.0,
                'R_resistance': 0.7,
                'O_openness': -0.6,
                'F_fear': 0.3,
                'M_maya': 0.4
            }
        }
    }

    # Secondary emotions derived from operator combinations
    SECONDARY_EMOTIONS = {
        'gratitude': {
            'operators': {'G_grace': 0.8, 'O_openness': 0.6, 'A_aware': 0.5},
            'valence': 'positive'
        },
        'hope': {
            'operators': {'I_intention': 0.7, 'Tr_trust': 0.6, 'F_fear': -0.3},
            'valence': 'positive'
        },
        'despair': {
            'operators': {'F_fear': 0.6, 'Tr_trust': -0.7, 'G_grace': -0.5},
            'valence': 'negative'
        },
        'pride': {
            'operators': {'At_attachment': 0.7, 'I_intention': 0.5, 'S_surrender': -0.4},
            'valence': 'neutral'
        },
        'shame': {
            'operators': {'F_fear': 0.5, 'At_attachment': 0.6, 'Se_service': -0.3},
            'valence': 'negative'
        },
        'guilt': {
            'operators': {'K_karma': 0.7, 'A_aware': 0.5, 'D_dharma': -0.4},
            'valence': 'negative'
        },
        'jealousy': {
            'operators': {'At_attachment': 0.8, 'F_fear': 0.5, 'O_openness': -0.5},
            'valence': 'negative'
        },
        'envy': {
            'operators': {'At_attachment': 0.7, 'R_resistance': 0.5, 'Se_service': -0.4},
            'valence': 'negative'
        },
        'contentment': {
            'operators': {'E_equanimity': 0.7, 'P_presence': 0.6, 'At_attachment': -0.3},
            'valence': 'positive'
        },
        'longing': {
            'operators': {'At_attachment': 0.8, 'I_intention': 0.5, 'P_presence': -0.4},
            'valence': 'neutral'
        },
        'serenity': {
            'operators': {'E_equanimity': 0.8, 'Co_coherence': 0.6, 'R_resistance': -0.5},
            'valence': 'positive'
        },
        'anxiety': {
            'operators': {'F_fear': 0.7, 'P_presence': -0.5, 'Tr_trust': -0.4},
            'valence': 'negative'
        },
        'grief': {
            'operators': {'At_attachment': 0.6, 'V_void': 0.5, 'Ce_celebration': -0.4},
            'valence': 'negative'
        },
        'relief': {
            'operators': {'F_fear': -0.6, 'S_surrender': 0.5, 'E_equanimity': 0.4},
            'valence': 'positive'
        },
        'frustration': {
            'operators': {'R_resistance': 0.7, 'I_intention': 0.5, 'S_surrender': -0.5},
            'valence': 'negative'
        },
        'enthusiasm': {
            'operators': {'I_intention': 0.8, 'Sh_shakti': 0.6, 'J_joy': 0.5},
            'valence': 'positive'
        },
        'apathy': {
            'operators': {'I_intention': -0.6, 'Sh_shakti': -0.5, 'P_presence': -0.4},
            'valence': 'negative'
        },
        'awe': {
            'operators': {'O_openness': 0.8, 'W_witness': 0.6, 'At_attachment': -0.3},
            'valence': 'positive'
        },
        'reverence': {
            'operators': {'S_surrender': 0.7, 'A_aware': 0.6, 'G_grace': 0.5},
            'valence': 'positive'
        },
        'boredom': {
            'operators': {'P_presence': -0.6, 'O_openness': -0.4, 'Hf_habit': 0.5},
            'valence': 'negative'
        }
    }

    def analyze(self, operators: Dict[str, float]) -> EmotionalProfile:
        """Analyze complete emotional profile from operators"""
        # Calculate all rasas
        rasas = {}
        for rasa_name, rasa_def in self.RASAS.items():
            rasas[rasa_name] = self._calculate_emotion(
                rasa_name,
                rasa_def,
                operators
            )

        # Calculate secondary emotions
        secondary = {}
        for emotion_name, emotion_def in self.SECONDARY_EMOTIONS.items():
            secondary[emotion_name] = self._calculate_emotion(
                emotion_name,
                emotion_def,
                operators,
                is_rasa=False
            )

        # Find dominant rasa
        dominant = max(rasas.items(), key=lambda x: x[1].intensity)
        dominant_rasa = dominant[0]

        # Calculate emotional coherence
        coherence = self._calculate_coherence(rasas, secondary)

        # Calculate guna influence on emotions
        guna_influence = self._calculate_guna_influence(operators)

        return EmotionalProfile(
            rasas=rasas,
            secondary_emotions=secondary,
            dominant_rasa=dominant_rasa,
            emotional_coherence=coherence,
            guna_influence=guna_influence
        )

    def _calculate_emotion(
        self,
        name: str,
        definition: Dict[str, Any],
        operators: Dict[str, float],
        is_rasa: bool = True
    ) -> EmotionState:
        """Calculate a single emotion's intensity"""
        op_weights = definition.get('operators', {})

        total_weight = 0.0
        weighted_sum = 0.0
        components = {}

        for op_name, weight in op_weights.items():
            # Handle aversion specially
            if op_name == 'Av_aversion' and op_name not in operators:
                value = operators.get('F_fear', 0.5) * 0.7 + operators.get('R_resistance', 0.5) * 0.3
            else:
                value = operators.get(op_name, 0.5)

            abs_weight = abs(weight)

            # Negative weights invert contribution
            if weight < 0:
                contribution = (1.0 - value) * abs_weight
            else:
                contribution = value * abs_weight

            weighted_sum += contribution
            total_weight += abs_weight
            components[op_name] = contribution / abs_weight if abs_weight > 0 else 0.5

        intensity = weighted_sum / total_weight if total_weight > 0 else 0.5

        # Get description based on intensity
        description = self._get_emotion_description(name, intensity, is_rasa)

        return EmotionState(
            name=name,
            sanskrit=definition.get('sanskrit', name.title()),
            intensity=intensity,
            valence=definition.get('valence', 'neutral'),
            components=components,
            description=description
        )

    def _calculate_coherence(
        self,
        rasas: Dict[str, EmotionState],
        secondary: Dict[str, EmotionState]
    ) -> float:
        """
        Calculate emotional coherence.
        High coherence = emotions aligned, low internal conflict.
        """
        # Check for conflicting emotions
        conflicts = 0.0

        # Joy vs Fear conflict
        if 'hasya' in rasas and 'bhayanaka' in rasas:
            conflicts += rasas['hasya'].intensity * rasas['bhayanaka'].intensity

        # Peace vs Anger conflict
        if 'shanta' in rasas and 'raudra' in rasas:
            conflicts += rasas['shanta'].intensity * rasas['raudra'].intensity

        # Love vs Disgust conflict
        if 'shringara' in rasas and 'bibhatsa' in rasas:
            conflicts += rasas['shringara'].intensity * rasas['bibhatsa'].intensity

        # Hope vs Despair conflict
        if 'hope' in secondary and 'despair' in secondary:
            conflicts += secondary['hope'].intensity * secondary['despair'].intensity

        # Coherence is inverse of conflicts
        coherence = max(0.0, 1.0 - conflicts)

        return coherence

    def _calculate_guna_influence(self, operators: Dict[str, float]) -> Dict[str, float]:
        """Calculate how gunas influence emotional state"""
        # Approximate guna from operators
        sattva = (
            operators.get('E_equanimity', 0.5) * 0.3 +
            operators.get('A_aware', 0.5) * 0.3 +
            operators.get('W_witness', 0.5) * 0.2 +
            operators.get('Co_coherence', 0.5) * 0.2
        )

        rajas = (
            operators.get('I_intention', 0.5) * 0.3 +
            operators.get('At_attachment', 0.5) * 0.3 +
            operators.get('Sh_shakti', 0.5) * 0.2 +
            operators.get('R_resistance', 0.5) * 0.2
        )

        tamas = (
            operators.get('F_fear', 0.5) * 0.3 +
            operators.get('Hf_habit', 0.5) * 0.3 +
            operators.get('M_maya', 0.5) * 0.2 +
            (1.0 - operators.get('A_aware', 0.5)) * 0.2
        )

        # Normalize
        total = sattva + rajas + tamas
        if total > 0:
            sattva /= total
            rajas /= total
            tamas /= total

        return {
            'sattva': sattva,
            'rajas': rajas,
            'tamas': tamas
        }

    def _get_emotion_description(
        self,
        name: str,
        intensity: float,
        is_rasa: bool
    ) -> str:
        """Generate description based on emotion and intensity"""
        pct = intensity * 100

        if pct < 30:
            level = "minimal"
        elif pct < 50:
            level = "moderate"
        elif pct < 70:
            level = "significant"
        else:
            level = "strong"

        if is_rasa:
            return f"{level.title()} {name} ({pct:.0f}%)"
        else:
            return f"{level.title()} {name}"

    def get_emotional_recommendations(
        self,
        profile: EmotionalProfile
    ) -> List[str]:
        """Generate recommendations based on emotional profile"""
        recommendations = []

        # Check for negative dominant states
        dominant = profile.rasas.get(profile.dominant_rasa)
        if dominant and dominant.valence == 'negative' and dominant.intensity > 0.6:
            if profile.dominant_rasa == 'bhayanaka':
                recommendations.append("Practice grounding and safety-building exercises")
            elif profile.dominant_rasa == 'raudra':
                recommendations.append("Channel energy through physical activity or creative expression")
            elif profile.dominant_rasa == 'bibhatsa':
                recommendations.append("Examine what you're rejecting - it may hold wisdom")

        # Check coherence
        if profile.emotional_coherence < 0.5:
            recommendations.append("Internal conflict detected - integration practices recommended")

        # Check guna balance
        if profile.guna_influence.get('tamas', 0) > 0.5:
            recommendations.append("Increase activity and engagement to reduce tamasic influence")
        if profile.guna_influence.get('rajas', 0) > 0.5:
            recommendations.append("Balance activity with stillness practices")

        # Positive reinforcement
        if profile.rasas.get('shanta', EmotionState('', '', 0, '', {}, '')).intensity > 0.6:
            recommendations.append("Peace is well-established - maintain through regular practice")

        return recommendations

    def calculate_emotional_evolution(
        self,
        current: EmotionalProfile,
        target_rasa: str,
        s_level: float
    ) -> Dict[str, Any]:
        """
        Calculate path from current emotional state to target rasa.

        Returns operator changes needed to shift emotional dominant.
        """
        if target_rasa not in self.RASAS:
            return {'error': f'Unknown target rasa: {target_rasa}'}

        current_dominant = current.dominant_rasa
        target_def = self.RASAS[target_rasa]

        # Calculate which operators need to change
        required_changes = {}
        for op_name, target_weight in target_def['operators'].items():
            current_contribution = current.rasas[current_dominant].components.get(op_name, 0.5)

            if target_weight > 0:
                # Need higher value
                if current_contribution < 0.6:
                    required_changes[op_name] = f"Increase (current: {current_contribution:.0%})"
            else:
                # Need lower value
                if current_contribution > 0.4:
                    required_changes[op_name] = f"Decrease (current: {current_contribution:.0%})"

        # Estimate timeline based on S-level
        base_weeks = 4 + (8 - s_level)  # Higher S-level = faster change

        return {
            'current_dominant': current_dominant,
            'target_rasa': target_rasa,
            'required_changes': required_changes,
            'estimated_weeks': base_weeks,
            's_level_factor': f"S{s_level:.0f} - {'accelerated' if s_level > 5 else 'gradual'} emotional evolution"
        }
