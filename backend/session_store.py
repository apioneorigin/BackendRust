"""
Session Store - Zero-Fallback Session Persistence Layer

Manages session state including:
- Confirmed operator values (from user answers)
- Inferred operator values (from LLM analysis)
- Missing operator tracking
- Historical context from previous interactions

ZERO-FALLBACK MODE: No default values. Only stores explicitly provided or inferred values.
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid

from formulas import CANONICAL_OPERATOR_NAMES
from logging_config import session_store_logger as logger


class OperatorSource(Enum):
    """Source of an operator value"""
    USER_CONFIRMED = "user_confirmed"      # User directly answered a question
    LLM_INFERRED = "llm_inferred"          # LLM extracted from user text
    FORMULA_DERIVED = "formula_derived"     # Calculated from other operators
    HISTORICAL = "historical"               # From previous session


@dataclass
class OperatorValue:
    """A single operator value with metadata"""
    operator_name: str
    canonical_name: str  # Standardized name (e.g., 'K' for karma)
    value: float  # 0.0-1.0
    confidence: float  # 0.0-1.0
    source: OperatorSource
    timestamp: datetime
    evidence: Optional[str] = None  # Supporting text/reasoning
    question_id: Optional[str] = None  # If from a question answer


@dataclass
class SessionContext:
    """Context from the current session"""
    original_query: str
    query_timestamp: datetime
    interaction_count: int = 0
    topics_discussed: List[str] = field(default_factory=list)
    user_responses: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SessionState:
    """Complete session state"""
    session_id: str
    created_at: datetime
    last_updated: datetime
    context: SessionContext
    operators: Dict[str, OperatorValue]  # canonical_name -> OperatorValue
    missing_operators: Set[str]  # Operators needed but not yet provided
    pending_questions: List[Dict[str, Any]]  # Questions waiting for answers
    answered_questions: List[Dict[str, Any]]  # Questions already answered
    inference_history: List[Dict[str, Any]]  # Previous inference runs


class SessionStore:
    """
    Manages session state for zero-fallback operation.

    Key responsibilities:
    - Store and retrieve operator values with metadata
    - Track which operators are missing
    - Maintain session context across interactions
    - Support confidence-weighted operator updates
    """

    # Canonical operator mappings (various names -> canonical)
    CANONICAL_NAMES = {
        # Core operators
        'Ψ': 'Psi', 'Psi': 'Psi', 'Psi_quality': 'Psi', 'psi': 'Psi',
        'K': 'K', 'K_karma': 'K', 'karma': 'K',
        'M': 'M', 'M_maya': 'M', 'maya': 'M',
        'G': 'G', 'G_grace': 'G', 'grace': 'G',
        'W': 'W', 'W_witness': 'W', 'witness': 'W',
        'A': 'A', 'A_aware': 'A', 'aware': 'A', 'awareness': 'A',
        'P': 'P', 'P_presence': 'P', 'presence': 'P',
        'E': 'E', 'E_equanimity': 'E', 'equanimity': 'E',
        'V': 'V', 'V_void': 'V', 'void': 'V',
        'L': 'L', 'L_love': 'L', 'love': 'L',
        'R': 'R', 'R_resistance': 'R', 'resistance': 'R',
        'At': 'At', 'At_attachment': 'At', 'attachment': 'At',
        'Av': 'Av', 'Av_aversion': 'Av', 'aversion': 'Av',
        'Se': 'Se', 'Se_service': 'Se', 'service': 'Se',
        'Ce': 'Ce', 'Ce_cleaning': 'Ce', 'celebration': 'Ce', 'cleaning': 'Ce',
        'Su': 'Su', 'Su_suffering': 'Su', 'suffering': 'Su',
        'As': 'As', 'As_aspiration': 'As', 'aspiration': 'As',
        'Fe': 'Fe', 'Fe_faith': 'Fe', 'faith': 'Fe',
        'De': 'De', 'De_devotion': 'De', 'devotion': 'De',
        'Re': 'Re', 'Re_receptivity': 'Re', 'receptivity': 'Re',
        'Hf': 'Hf', 'Hf_habit': 'Hf', 'habit': 'Hf',
        'Sa': 'Sa', 'Sa_samskara': 'Sa', 'samskara': 'Sa',
        'Bu': 'Bu', 'Bu_buddhi': 'Bu', 'buddhi': 'Bu',
        'Ma': 'Ma', 'Ma_manas': 'Ma', 'manas': 'Ma',
        'Ch': 'Ch', 'Ch_chitta': 'Ch', 'chitta': 'Ch',
        # Extended operators
        'I': 'I', 'I_intention': 'I', 'intention': 'I',
        'S': 'S', 'S_surrender': 'S', 'surrender': 'S',
        'F': 'F', 'F_fear': 'F', 'fear': 'F',
        'D': 'D', 'D_dharma': 'D', 'dharma': 'D',
        'Sh': 'Sh', 'Sh_shakti': 'Sh', 'shakti': 'Sh',
        'Tr': 'Tr', 'Tr_trust': 'Tr', 'trust': 'Tr',
        'O': 'O', 'O_openness': 'O', 'openness': 'O',
        'Co': 'Co', 'Co_coherence': 'Co', 'coherence': 'Co',
        'J': 'J', 'J_joy': 'J', 'joy': 'J',
        'M_manifest': 'M_manifest', 'manifest': 'M_manifest',
        'T_time_present': 'T_time', 'time': 'T_time',
    }

    # Use centralized canonical operator names
    CORE_OPERATORS = CANONICAL_OPERATOR_NAMES

    def __init__(self):
        """Initialize the session store."""
        self.sessions: Dict[str, SessionState] = {}
        self.session_timeout = timedelta(hours=24)

    def create_session(self, query: str) -> SessionState:
        """
        Create a new session for a query.

        Args:
            query: The user's original query

        Returns:
            New SessionState with empty operator state
        """
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()
        logger.info(f"[SESSION] Creating new session {session_id[:8]}... for query: '{query[:60]}...'")

        context = SessionContext(
            original_query=query,
            query_timestamp=now,
            interaction_count=1
        )

        session = SessionState(
            session_id=session_id,
            created_at=now,
            last_updated=now,
            context=context,
            operators={},
            missing_operators=self.CORE_OPERATORS.copy(),
            pending_questions=[],
            answered_questions=[],
            inference_history=[]
        )

        self.sessions[session_id] = session
        logger.debug(f"[SESSION] Session {session_id[:8]} created with {len(self.CORE_OPERATORS)} missing operators")
        return session

    def get_session(self, session_id: str) -> Optional[SessionState]:
        """
        Retrieve a session by ID.

        Args:
            session_id: The session identifier

        Returns:
            SessionState if found and not expired, None otherwise
        """
        session = self.sessions.get(session_id)
        if session is None:
            logger.debug(f"[SESSION] Session {session_id[:8]} not found")
            return None

        # Check if session has expired
        if datetime.utcnow() - session.last_updated > self.session_timeout:
            logger.info(f"[SESSION] Session {session_id[:8]} expired, removing")
            del self.sessions[session_id]
            return None

        return session

    def get_canonical_name(self, operator_name: str) -> str:
        """
        Get the canonical name for an operator.

        Args:
            operator_name: Any variant of the operator name

        Returns:
            Canonical operator name
        """
        return self.CANONICAL_NAMES.get(operator_name, operator_name)

    def set_operator(
        self,
        session_id: str,
        operator_name: str,
        value: float,
        confidence: float,
        source: OperatorSource,
        evidence: Optional[str] = None,
        question_id: Optional[str] = None
    ) -> bool:
        """
        Set an operator value in the session.

        Confidence-weighted update: Only updates if new confidence >= existing.

        Args:
            session_id: Session identifier
            operator_name: Operator name (any variant)
            value: Operator value (0.0-1.0)
            confidence: Confidence in this value (0.0-1.0)
            source: Where this value came from
            evidence: Supporting text/reasoning
            question_id: If from a question answer

        Returns:
            True if value was set, False if rejected due to lower confidence
        """
        session = self.get_session(session_id)
        if session is None:
            return False

        canonical = self.get_canonical_name(operator_name)

        # Check existing value
        existing = session.operators.get(canonical)
        if existing is not None:
            # User-confirmed values take precedence
            if existing.source == OperatorSource.USER_CONFIRMED and source != OperatorSource.USER_CONFIRMED:
                return False
            # Otherwise, only update if confidence is higher or equal
            if existing.confidence > confidence:
                return False

        # Create and store the operator value
        op_value = OperatorValue(
            operator_name=operator_name,
            canonical_name=canonical,
            value=value,
            confidence=confidence,
            source=source,
            timestamp=datetime.utcnow(),
            evidence=evidence,
            question_id=question_id
        )

        session.operators[canonical] = op_value
        session.missing_operators.discard(canonical)
        session.last_updated = datetime.utcnow()

        logger.debug(f"[SESSION] Set {canonical}={value:.3f} conf={confidence:.2f} src={source.value} remaining_missing={len(session.missing_operators)}")
        return True

    def set_operators_batch(
        self,
        session_id: str,
        operators: Dict[str, float],
        confidence: float,
        source: OperatorSource,
        evidence: Optional[str] = None
    ) -> Tuple[int, int]:
        """
        Set multiple operator values at once.

        Args:
            session_id: Session identifier
            operators: Dict of operator_name -> value
            confidence: Confidence for all values
            source: Source for all values
            evidence: Optional evidence string

        Returns:
            Tuple of (successful_count, rejected_count)
        """
        successful = 0
        rejected = 0

        for op_name, value in operators.items():
            if self.set_operator(session_id, op_name, value, confidence, source, evidence):
                successful += 1
            else:
                rejected += 1

        logger.info(f"[SESSION] Batch set: {successful} accepted, {rejected} rejected (src={source.value})")
        return successful, rejected

    def get_operator(self, session_id: str, operator_name: str) -> Optional[OperatorValue]:
        """
        Get an operator value from the session.

        Args:
            session_id: Session identifier
            operator_name: Operator name (any variant)

        Returns:
            OperatorValue if found, None otherwise
        """
        session = self.get_session(session_id)
        if session is None:
            return None

        canonical = self.get_canonical_name(operator_name)
        return session.operators.get(canonical)

    def get_all_operators(self, session_id: str) -> Dict[str, float]:
        """
        Get all operator values as a simple dict for calculations.

        Args:
            session_id: Session identifier

        Returns:
            Dict of canonical_name -> value for all stored operators
        """
        session = self.get_session(session_id)
        if session is None:
            return {}

        return {
            op.canonical_name: op.value
            for op in session.operators.values()
        }

    def get_operators_with_metadata(self, session_id: str) -> Dict[str, OperatorValue]:
        """
        Get all operators with full metadata.

        Args:
            session_id: Session identifier

        Returns:
            Dict of canonical_name -> OperatorValue
        """
        session = self.get_session(session_id)
        if session is None:
            return {}

        return session.operators.copy()

    def get_missing_operators(self, session_id: str) -> Set[str]:
        """
        Get the set of operators that are still missing.

        Args:
            session_id: Session identifier

        Returns:
            Set of canonical operator names that haven't been provided
        """
        session = self.get_session(session_id)
        if session is None:
            return self.CORE_OPERATORS.copy()

        return session.missing_operators.copy()

    def get_operator_coverage(self, session_id: str) -> Dict[str, Any]:
        """
        Get statistics about operator coverage.

        Args:
            session_id: Session identifier

        Returns:
            Dict with coverage statistics
        """
        session = self.get_session(session_id)
        if session is None:
            return {
                'total_core': len(self.CORE_OPERATORS),
                'populated': 0,
                'missing': len(self.CORE_OPERATORS),
                'coverage_percent': 0.0,
                'missing_operators': list(self.CORE_OPERATORS)
            }

        populated = len(session.operators)
        missing = len(session.missing_operators)
        total = len(self.CORE_OPERATORS)

        # Breakdown by source
        by_source = {}
        for op in session.operators.values():
            source_name = op.source.value
            by_source[source_name] = by_source.get(source_name, 0) + 1

        # Average confidence
        if session.operators:
            avg_confidence = sum(op.confidence for op in session.operators.values()) / len(session.operators)
        else:
            avg_confidence = 0.0

        return {
            'total_core': total,
            'populated': populated,
            'missing': missing,
            'coverage_percent': (populated / total) * 100 if total > 0 else 0.0,
            'missing_operators': list(session.missing_operators),
            'by_source': by_source,
            'average_confidence': avg_confidence
        }

    def add_question(self, session_id: str, question: Dict[str, Any]) -> bool:
        """
        Add a pending question to the session.

        Args:
            session_id: Session identifier
            question: Question data including target operators

        Returns:
            True if added successfully
        """
        session = self.get_session(session_id)
        if session is None:
            return False

        session.pending_questions.append(question)
        session.last_updated = datetime.utcnow()
        return True

    def record_answer(
        self,
        session_id: str,
        question_id: str,
        answer: Dict[str, Any],
        operator_values: Dict[str, float]
    ) -> bool:
        """
        Record an answer to a question and update operators.

        Args:
            session_id: Session identifier
            question_id: ID of the question being answered
            answer: The user's answer data
            operator_values: Operator values derived from the answer

        Returns:
            True if recorded successfully
        """
        session = self.get_session(session_id)
        if session is None:
            return False

        # Find and move the question from pending to answered
        for i, q in enumerate(session.pending_questions):
            if q.get('id') == question_id:
                q['answer'] = answer
                q['answered_at'] = datetime.utcnow().isoformat()
                session.answered_questions.append(q)
                session.pending_questions.pop(i)
                break

        # Update operators from answer
        for op_name, value in operator_values.items():
            self.set_operator(
                session_id=session_id,
                operator_name=op_name,
                value=value,
                confidence=0.9,  # User-confirmed answers have high confidence
                source=OperatorSource.USER_CONFIRMED,
                question_id=question_id
            )

        # Record user response for context
        session.context.user_responses.append({
            'question_id': question_id,
            'answer': answer,
            'timestamp': datetime.utcnow().isoformat()
        })
        session.context.interaction_count += 1
        session.last_updated = datetime.utcnow()

        return True

    def record_inference(
        self,
        session_id: str,
        inference_result: Dict[str, Any]
    ) -> bool:
        """
        Record an inference run result.

        Args:
            session_id: Session identifier
            inference_result: Results from inference engine

        Returns:
            True if recorded successfully
        """
        session = self.get_session(session_id)
        if session is None:
            return False

        session.inference_history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'result': inference_result,
            'operator_count': len(session.operators),
            'missing_count': len(session.missing_operators)
        })
        session.last_updated = datetime.utcnow()

        return True

    def export_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Export session state as JSON-serializable dict.

        Args:
            session_id: Session identifier

        Returns:
            Dict representation of session state
        """
        session = self.get_session(session_id)
        if session is None:
            return None

        return {
            'session_id': session.session_id,
            'created_at': session.created_at.isoformat(),
            'last_updated': session.last_updated.isoformat(),
            'context': {
                'original_query': session.context.original_query,
                'query_timestamp': session.context.query_timestamp.isoformat(),
                'interaction_count': session.context.interaction_count,
                'topics_discussed': session.context.topics_discussed,
                'user_responses': session.context.user_responses
            },
            'operators': {
                name: {
                    'operator_name': op.operator_name,
                    'canonical_name': op.canonical_name,
                    'value': op.value,
                    'confidence': op.confidence,
                    'source': op.source.value,
                    'timestamp': op.timestamp.isoformat(),
                    'evidence': op.evidence,
                    'question_id': op.question_id
                }
                for name, op in session.operators.items()
            },
            'missing_operators': list(session.missing_operators),
            'pending_questions': session.pending_questions,
            'answered_questions': session.answered_questions,
            'inference_history': session.inference_history
        }

    def cleanup_expired_sessions(self) -> int:
        """
        Remove expired sessions.

        Returns:
            Number of sessions removed
        """
        now = datetime.utcnow()
        expired = [
            sid for sid, session in self.sessions.items()
            if now - session.last_updated > self.session_timeout
        ]

        for sid in expired:
            del self.sessions[sid]

        if expired:
            logger.info(f"[SESSION] Cleaned up {len(expired)} expired sessions")
        return len(expired)


# Global session store instance
session_store = SessionStore()
