"""
Transformation Matrix Detection
7 matrices × 4 states = 28 detection formulas

Each matrix represents a dimension of consciousness transformation:
- Truth: Illusion → Confusion → Clarity → Truth
- Love: Separation → Connection → Unity → Oneness
- Power: Victim → Responsibility → Mastery → Service
- Freedom: Bondage → Choice → Liberation → Transcendence
- Creation: Destruction → Maintenance → Creation → Source
- Time: Past/Future → Present → Eternal → Beyond
- Death: Clinging → Acceptance → Surrender → Rebirth
"""

from typing import Dict, Tuple, Any, Optional, List, Set
from dataclasses import dataclass, field


@dataclass
class MatrixPosition:
    """A position on a transformation matrix"""
    matrix: str
    position: str
    score: Optional[float]  # 0.0-1.0 or None if cannot calculate
    stage: Optional[int]  # 1-4 or None
    description: str
    missing_operators: List[str] = field(default_factory=list)


class MatrixDetector:
    """
    Detect positions on 7 transformation matrices.
    Uses operator values to calculate matrix positions.
    """

    # Matrix definitions: (stages, detection weights)
    MATRICES = {
        'truth': {
            'stages': ['illusion', 'confusion', 'clarity', 'truth'],
            'operators': {
                'M_maya': -1.0,      # High maya = lower truth
                'W_witness': 1.0,    # High witness = higher truth
                'A_aware': 0.8,      # Awareness supports truth
                'Psi_quality': 0.6,  # Consciousness quality
                'V_void': 0.4       # Void experience reveals truth
            },
            'thresholds': [0.25, 0.5, 0.75]  # Stage boundaries
        },
        'love': {
            'stages': ['separation', 'connection', 'unity', 'oneness'],
            'operators': {
                'At_attachment': -0.5,  # Attachment creates separation
                'Se_service': 1.0,      # Service enables unity
                'G_grace': 0.8,         # Grace opens heart
                'Co_coherence': 0.6,    # Coherence with others
                'O_openness': 0.7       # Openness to connection
            },
            'thresholds': [0.25, 0.5, 0.75]
        },
        'power': {
            'stages': ['victim', 'responsibility', 'mastery', 'service'],
            'operators': {
                'R_resistance': -0.8,   # Resistance = victim
                'I_intention': 0.9,     # Intention = power
                'D_dharma': 0.7,        # Dharma alignment
                'Sh_shakti': 0.8,       # Energy available
                'S_surrender': 0.5      # Surrender paradoxically increases power
            },
            'thresholds': [0.25, 0.5, 0.75]
        },
        'freedom': {
            'stages': ['bondage', 'choice', 'liberation', 'transcendence'],
            'operators': {
                'At_attachment': -1.0,  # Attachment = bondage
                'K_karma': -0.6,        # Karma limits freedom
                'S_surrender': 0.8,     # Surrender enables freedom
                'V_void': 0.7,          # Emptiness is freedom
                'G_grace': 0.6          # Grace liberates
            },
            'thresholds': [0.25, 0.5, 0.75]
        },
        'creation': {
            'stages': ['destruction', 'maintenance', 'creation', 'source'],
            'operators': {
                'I_intention': 0.9,     # Intention drives creation
                'M_manifest': 0.8,      # Manifestation power
                'Sh_shakti': 0.7,       # Energy for creation
                'Co_coherence': 0.6,    # Coherence sustains
                'Psi_quality': 0.5      # Consciousness quality
            },
            'thresholds': [0.25, 0.5, 0.75]
        },
        'time': {
            'stages': ['past_future', 'present', 'eternal', 'beyond'],
            'operators': {
                'P_presence': 1.0,      # Presence = present
                'T_time_present': 0.8,  # Time orientation
                'A_aware': 0.6,         # Awareness of now
                'W_witness': 0.7,       # Witness transcends time
                'V_void': 0.5           # Void is timeless
            },
            'thresholds': [0.25, 0.5, 0.75]
        },
        'death': {
            'stages': ['clinging', 'acceptance', 'surrender', 'rebirth'],
            'operators': {
                'At_attachment': -1.0,  # Attachment = clinging
                'S_surrender': 1.0,     # Surrender enables death
                'V_void': 0.8,          # Void tolerance
                'F_fear': -0.7,         # Fear blocks death
                'G_grace': 0.6          # Grace supports rebirth
            },
            'thresholds': [0.25, 0.5, 0.75]
        }
    }

    def detect_all(self, operators: Dict[str, float]) -> Dict[str, MatrixPosition]:
        """Detect positions on all 7 transformation matrices"""
        positions = {}
        for matrix_name in self.MATRICES:
            positions[matrix_name] = self.detect_matrix(matrix_name, operators)
        return positions

    def detect_matrix(self, matrix_name: str, operators: Dict[str, float]) -> MatrixPosition:
        """
        Detect position on a single matrix.

        ZERO-FALLBACK: Returns None score/stage if required operators are missing.
        """
        if matrix_name not in self.MATRICES:
            return MatrixPosition(
                matrix=matrix_name,
                position='unknown',
                score=None,
                stage=None,
                description=f"Unknown matrix: {matrix_name}",
                missing_operators=['unknown_matrix']
            )

        matrix_def = self.MATRICES[matrix_name]
        score, missing_ops = self._calculate_score(operators, matrix_def['operators'])

        # ZERO-FALLBACK: Handle missing operators
        if score is None:
            return MatrixPosition(
                matrix=matrix_name,
                position='indeterminate',
                score=None,
                stage=None,
                description=f"Cannot calculate - missing: {', '.join(missing_ops)}",
                missing_operators=missing_ops
            )

        stage = self._score_to_stage(score, matrix_def['thresholds'])
        position = matrix_def['stages'][stage - 1]

        return MatrixPosition(
            matrix=matrix_name,
            position=position,
            score=score,
            stage=stage,
            description=self._get_description(matrix_name, position, score),
            missing_operators=[]
        )

    def _calculate_score(
        self,
        operators: Dict[str, float],
        weights: Dict[str, float]
    ) -> Tuple[Optional[float], List[str]]:
        """
        Calculate weighted score from operators.

        ZERO-FALLBACK: Returns (None, missing_ops) if required operators are missing.
        """
        total_weight = 0.0
        weighted_sum = 0.0
        missing_ops = []

        for op_name, weight in weights.items():
            value = operators.get(op_name)

            # ZERO-FALLBACK: Track missing operators
            if value is None:
                missing_ops.append(op_name)
                continue

            abs_weight = abs(weight)

            # Negative weights invert the value
            if weight < 0:
                value = 1.0 - value

            weighted_sum += value * abs_weight
            total_weight += abs_weight

        # ZERO-FALLBACK: Return None if any required operators missing
        if missing_ops:
            return None, missing_ops

        if total_weight == 0:
            return None, ['no_weights_defined']

        return max(0.0, min(1.0, weighted_sum / total_weight)), []

    def _score_to_stage(self, score: float, thresholds: list) -> int:
        """Convert score to stage number (1-4)"""
        for i, threshold in enumerate(thresholds):
            if score < threshold:
                return i + 1
        return 4

    def _get_description(self, matrix: str, position: str, score: float) -> str:
        """Generate human-readable description"""
        descriptions = {
            'truth': {
                'illusion': "Operating under significant illusions about reality",
                'confusion': "Partial clarity but still significant blind spots",
                'clarity': "Clear perception of most situations",
                'truth': "Direct perception of reality as it is"
            },
            'love': {
                'separation': "Experiencing fundamental disconnection from others",
                'connection': "Forming meaningful connections",
                'unity': "Deep sense of connection with others",
                'oneness': "Experience of non-separation"
            },
            'power': {
                'victim': "Feeling powerless over circumstances",
                'responsibility': "Taking ownership of outcomes",
                'mastery': "Skillful navigation of situations",
                'service': "Power expressed through service to others"
            },
            'freedom': {
                'bondage': "Bound by attachments and limiting patterns",
                'choice': "Aware of choices available",
                'liberation': "Free from most limiting patterns",
                'transcendence': "Beyond the bondage-freedom duality"
            },
            'creation': {
                'destruction': "Energy primarily dissolving existing forms",
                'maintenance': "Energy sustaining current structures",
                'creation': "Actively manifesting new forms",
                'source': "Connected to the source of all creation"
            },
            'time': {
                'past_future': "Attention primarily in past or future",
                'present': "Grounded in present moment",
                'eternal': "Experiencing timelessness",
                'beyond': "Transcending the time dimension entirely"
            },
            'death': {
                'clinging': "Holding tightly to current identity/forms",
                'acceptance': "Beginning to accept necessary endings",
                'surrender': "Actively releasing what needs to die",
                'rebirth': "Experiencing renewal through letting go"
            }
        }

        base_desc = descriptions.get(matrix, {}).get(position, f"{matrix} at {position}")
        return f"{base_desc} ({score:.0%})"

    def get_transformation_vector(
        self,
        current: Dict[str, MatrixPosition],
        target_stages: Dict[str, int]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate what needs to shift to move from current to target positions.
        Returns required operator changes for each matrix.
        """
        vectors = {}

        for matrix_name, target_stage in target_stages.items():
            if matrix_name not in current:
                continue

            current_pos = current[matrix_name]
            if current_pos.stage >= target_stage:
                vectors[matrix_name] = {
                    'shift_required': False,
                    'message': f"Already at or beyond target stage"
                }
                continue

            stage_diff = target_stage - current_pos.stage
            matrix_def = self.MATRICES[matrix_name]

            # Determine which operators need to change
            required_changes = {}
            for op_name, weight in matrix_def['operators'].items():
                if weight > 0:
                    required_changes[op_name] = f"Increase by ~{stage_diff * 15}%"
                else:
                    required_changes[op_name] = f"Decrease by ~{stage_diff * 15}%"

            vectors[matrix_name] = {
                'shift_required': True,
                'current_stage': current_pos.stage,
                'target_stage': target_stage,
                'stage_gap': stage_diff,
                'current_position': current_pos.position,
                'target_position': matrix_def['stages'][target_stage - 1],
                'operator_changes': required_changes
            }

        return vectors

    def detect_matrix_coherence(
        self,
        positions: Dict[str, MatrixPosition]
    ) -> Dict[str, Any]:
        """
        Check if matrix positions are coherent with each other.
        Incoherent positions indicate internal conflict.

        ZERO-FALLBACK: Only considers positions with calculable stages.
        """
        # ZERO-FALLBACK: Filter to positions with calculable stages
        stages = [pos.stage for pos in positions.values() if pos.stage is not None]
        if not stages:
            return {
                'coherent': None,
                'variance': None,
                'conflicts': [],
                'note': 'Cannot assess coherence - insufficient operator data'
            }

        avg_stage = sum(stages) / len(stages)
        variance = sum((s - avg_stage) ** 2 for s in stages) / len(stages)

        conflicts = []

        # Check specific conflict patterns - ZERO-FALLBACK: check for None
        power_pos = positions.get('power')
        creation_pos = positions.get('creation')
        if power_pos and power_pos.stage is not None and creation_pos and creation_pos.stage is not None:
            if power_pos.stage <= 1 and creation_pos.stage >= 3:
                conflicts.append("Victim stance conflicts with creator role")

        truth_pos = positions.get('truth')
        love_pos = positions.get('love')
        if truth_pos and truth_pos.stage is not None and love_pos and love_pos.stage is not None:
            if truth_pos.stage <= 1 and love_pos.stage >= 3:
                conflicts.append("Illusion-based love may not be sustainable")

        freedom_pos = positions.get('freedom')
        death_pos = positions.get('death')
        if freedom_pos and freedom_pos.stage is not None and death_pos and death_pos.stage is not None:
            if freedom_pos.stage <= 1 and death_pos.stage >= 3:
                conflicts.append("Cannot surrender while in bondage consciousness")

        return {
            'coherent': variance < 1.0 and len(conflicts) == 0,
            'variance': variance,
            'average_stage': avg_stage,
            'conflicts': conflicts,
            'calculable_matrices': len(stages)
        }
