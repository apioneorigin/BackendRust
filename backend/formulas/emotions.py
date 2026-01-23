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

from typing import Dict, Any, List, Tuple, Optional, Set
from dataclasses import dataclass, field
import math


@dataclass
class EmotionState:
    """A single emotion's state"""
    name: str
    sanskrit: str
    intensity: Optional[float]  # 0.0-1.0 or None if cannot calculate
    valence: str      # positive, negative, neutral
    components: Dict[str, Optional[float]]
    description: str
    missing_operators: List[str] = field(default_factory=list)


@dataclass
class EmotionalProfile:
    """Complete emotional profile"""
    rasas: Dict[str, EmotionState]
    secondary_emotions: Dict[str, EmotionState]
    dominant_rasa: Optional[str]
    emotional_coherence: Optional[float]
    guna_influence: Dict[str, Optional[float]]
    missing_operators: Set[str] = field(default_factory=set)
    calculable_rasas: int = 0


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
        """
        Analyze complete emotional profile from operators.

        ZERO-FALLBACK: Tracks missing operators and handles None intensities.
        """
        all_missing: Set[str] = set()

        # Calculate all rasas
        rasas = {}
        calculable_rasas = 0
        for rasa_name, rasa_def in self.RASAS.items():
            rasa = self._calculate_emotion(
                rasa_name,
                rasa_def,
                operators
            )
            rasas[rasa_name] = rasa
            all_missing.update(rasa.missing_operators)
            if rasa.intensity is not None:
                calculable_rasas += 1

        # Calculate secondary emotions
        secondary = {}
        for emotion_name, emotion_def in self.SECONDARY_EMOTIONS.items():
            emotion = self._calculate_emotion(
                emotion_name,
                emotion_def,
                operators,
                is_rasa=False
            )
            secondary[emotion_name] = emotion
            all_missing.update(emotion.missing_operators)

        # Find dominant rasa - ZERO-FALLBACK: only from calculable rasas
        calculable_rasa_items = [(k, v) for k, v in rasas.items() if v.intensity is not None]
        if calculable_rasa_items:
            dominant = max(calculable_rasa_items, key=lambda x: x[1].intensity)
            dominant_rasa = dominant[0]
        else:
            dominant_rasa = None

        # Calculate emotional coherence
        coherence = self._calculate_coherence(rasas, secondary)

        # Calculate guna influence on emotions
        guna_influence = self._calculate_guna_influence(operators)

        return EmotionalProfile(
            rasas=rasas,
            secondary_emotions=secondary,
            dominant_rasa=dominant_rasa,
            emotional_coherence=coherence,
            guna_influence=guna_influence,
            missing_operators=all_missing,
            calculable_rasas=calculable_rasas
        )

    def _calculate_emotion(
        self,
        name: str,
        definition: Dict[str, Any],
        operators: Dict[str, float],
        is_rasa: bool = True
    ) -> EmotionState:
        """
        Calculate a single emotion's intensity.

        ZERO-FALLBACK: Returns None intensity if required operators are missing.
        """
        op_weights = definition.get('operators', {})
        missing_ops = []
        components = {}

        total_weight = 0.0
        weighted_sum = 0.0
        has_all_required = True

        for op_name, weight in op_weights.items():
            # ZERO-FALLBACK: Check if operator exists
            if op_name == 'Av_aversion' and op_name not in operators:
                # Aversion can be derived from fear + resistance if both present
                f_val = operators.get('F_fear')
                r_val = operators.get('R_resistance')
                if f_val is not None and r_val is not None:
                    value = f_val * 0.7 + r_val * 0.3
                else:
                    missing_ops.append(op_name)
                    has_all_required = False
                    value = None
            elif op_name not in operators or operators.get(op_name) is None:
                missing_ops.append(op_name)
                has_all_required = False
                value = None
            else:
                value = operators.get(op_name)

            abs_weight = abs(weight)

            if value is not None:
                # Negative weights invert contribution
                if weight < 0:
                    contribution = (1.0 - value) * abs_weight
                else:
                    contribution = value * abs_weight

                weighted_sum += contribution
                total_weight += abs_weight
                components[op_name] = contribution / abs_weight if abs_weight > 0 else None
            else:
                components[op_name] = None

        # ZERO-FALLBACK: Only calculate intensity if all operators present
        if has_all_required and total_weight > 0:
            intensity = weighted_sum / total_weight
            description = self._get_emotion_description(name, intensity, is_rasa)
        else:
            intensity = None
            description = f"Cannot calculate - missing: {', '.join(missing_ops)}"

        return EmotionState(
            name=name,
            sanskrit=definition.get('sanskrit', name.title()),
            intensity=intensity,
            valence=definition.get('valence', 'neutral'),
            components=components,
            description=description,
            missing_operators=missing_ops
        )

    def _calculate_coherence(
        self,
        rasas: Dict[str, EmotionState],
        secondary: Dict[str, EmotionState]
    ) -> Optional[float]:
        """
        Calculate emotional coherence.
        High coherence = emotions aligned, low internal conflict.

        ZERO-FALLBACK: Returns None if insufficient data to calculate conflicts.
        """
        # Check for conflicting emotions
        conflicts = 0.0
        conflict_pairs_checked = 0

        # Joy vs Fear conflict
        if 'hasya' in rasas and 'bhayanaka' in rasas:
            h_int = rasas['hasya'].intensity
            b_int = rasas['bhayanaka'].intensity
            if h_int is not None and b_int is not None:
                conflicts += h_int * b_int
                conflict_pairs_checked += 1

        # Peace vs Anger conflict
        if 'shanta' in rasas and 'raudra' in rasas:
            s_int = rasas['shanta'].intensity
            r_int = rasas['raudra'].intensity
            if s_int is not None and r_int is not None:
                conflicts += s_int * r_int
                conflict_pairs_checked += 1

        # Love vs Disgust conflict
        if 'shringara' in rasas and 'bibhatsa' in rasas:
            sh_int = rasas['shringara'].intensity
            bi_int = rasas['bibhatsa'].intensity
            if sh_int is not None and bi_int is not None:
                conflicts += sh_int * bi_int
                conflict_pairs_checked += 1

        # Hope vs Despair conflict
        if 'hope' in secondary and 'despair' in secondary:
            hp_int = secondary['hope'].intensity
            dp_int = secondary['despair'].intensity
            if hp_int is not None and dp_int is not None:
                conflicts += hp_int * dp_int
                conflict_pairs_checked += 1

        # ZERO-FALLBACK: Return None if no conflict pairs could be checked
        if conflict_pairs_checked == 0:
            return None

        # Coherence is inverse of conflicts
        coherence = max(0.0, 1.0 - conflicts)

        return coherence

    def _calculate_guna_influence(self, operators: Dict[str, float]) -> Dict[str, Optional[float]]:
        """
        Calculate how gunas influence emotional state.

        ZERO-FALLBACK: Returns None for each guna if required operators are missing.
        """
        # Required operators for each guna
        sattva_ops = ['E_equanimity', 'A_aware', 'W_witness', 'Co_coherence']
        rajas_ops = ['I_intention', 'At_attachment', 'Sh_shakti', 'R_resistance']
        tamas_ops = ['F_fear', 'Hf_habit', 'M_maya', 'A_aware']

        def calc_guna(op_list: List[str], weights: List[float]) -> Optional[float]:
            total = 0.0
            for op, w in zip(op_list, weights):
                val = operators.get(op)
                if val is None:
                    return None
                total += val * w
            return total

        sattva = calc_guna(sattva_ops, [0.3, 0.3, 0.2, 0.2])
        rajas = calc_guna(rajas_ops, [0.3, 0.3, 0.2, 0.2])

        # Tamas has a special calculation with inverted A_aware
        tamas_base_ops = ['F_fear', 'Hf_habit', 'M_maya']
        tamas_weights = [0.3, 0.3, 0.2]
        tamas_base = calc_guna(tamas_base_ops, tamas_weights)
        a_val = operators.get('A_aware')

        if tamas_base is not None and a_val is not None:
            tamas = tamas_base + (1.0 - a_val) * 0.2
        else:
            tamas = None

        # Normalize only if all gunas are calculable
        if sattva is not None and rajas is not None and tamas is not None:
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
        intensity: Optional[float],
        is_rasa: bool
    ) -> str:
        """
        Generate description based on emotion and intensity.

        ZERO-FALLBACK: Returns appropriate message if intensity is None.
        """
        if intensity is None:
            return f"Cannot assess {name} - insufficient data"

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
        """
        Generate recommendations based on emotional profile.

        ZERO-FALLBACK: Handles None values gracefully.
        """
        recommendations = []

        # Check for negative dominant states
        if profile.dominant_rasa:
            dominant = profile.rasas.get(profile.dominant_rasa)
            if dominant and dominant.intensity is not None:
                if dominant.valence == 'negative' and dominant.intensity > 0.6:
                    if profile.dominant_rasa == 'bhayanaka':
                        recommendations.append("Practice grounding and safety-building exercises")
                    elif profile.dominant_rasa == 'raudra':
                        recommendations.append("Channel energy through physical activity or creative expression")
                    elif profile.dominant_rasa == 'bibhatsa':
                        recommendations.append("Examine what you're rejecting - it may hold wisdom")

        # Check coherence - ZERO-FALLBACK: only if calculable
        if profile.emotional_coherence is not None and profile.emotional_coherence < 0.5:
            recommendations.append("Internal conflict detected - integration practices recommended")

        # Check guna balance - ZERO-FALLBACK: only if calculable
        tamas_val = profile.guna_influence.get('tamas')
        rajas_val = profile.guna_influence.get('rajas')

        if tamas_val is not None and tamas_val > 0.5:
            recommendations.append("Increase activity and engagement to reduce tamasic influence")
        if rajas_val is not None and rajas_val > 0.5:
            recommendations.append("Balance activity with stillness practices")

        # Positive reinforcement - ZERO-FALLBACK: check intensity exists
        shanta = profile.rasas.get('shanta')
        if shanta and shanta.intensity is not None and shanta.intensity > 0.6:
            recommendations.append("Peace is well-established - maintain through regular practice")

        # Add recommendation if insufficient data
        if profile.missing_operators:
            recommendations.append(f"Note: {len(profile.missing_operators)} operators missing for complete analysis")

        return recommendations

    def calculate_emotional_evolution(
        self,
        current: EmotionalProfile,
        target_rasa: str,
        s_level: float
    ) -> Dict[str, Any]:
        """
        Calculate path from current emotional state to target rasa.

        ZERO-FALLBACK: Returns error if insufficient data for calculation.

        Returns operator changes needed to shift emotional dominant.
        """
        if target_rasa not in self.RASAS:
            return {'error': f'Unknown target rasa: {target_rasa}'}

        current_dominant = current.dominant_rasa
        if current_dominant is None:
            return {'error': 'Cannot determine current dominant rasa - insufficient operator data'}

        target_def = self.RASAS[target_rasa]
        current_rasa = current.rasas.get(current_dominant)
        if not current_rasa:
            return {'error': f'Current dominant rasa {current_dominant} not found'}

        # Calculate which operators need to change - ZERO-FALLBACK
        required_changes = {}
        missing_for_analysis = []

        for op_name, target_weight in target_def['operators'].items():
            current_contribution = current_rasa.components.get(op_name)

            if current_contribution is None:
                missing_for_analysis.append(op_name)
                continue

            if target_weight > 0:
                # Need higher value
                if current_contribution < 0.6:
                    required_changes[op_name] = f"Increase (current: {current_contribution:.0%})"
            else:
                # Need lower value
                if current_contribution > 0.4:
                    required_changes[op_name] = f"Decrease (current: {current_contribution:.0%})"

        result = {
            'current_dominant': current_dominant,
            'target_rasa': target_rasa,
            'required_changes': required_changes,
            's_level_factor': f"S{s_level:.0f} - {'accelerated' if s_level > 5 else 'gradual'} emotional evolution"
        }

        if missing_for_analysis:
            result['missing_operators'] = missing_for_analysis
            result['note'] = 'Some operators missing - analysis may be incomplete'

        return result
