"""
Value Organizer Service for Articulation Bridge
Transforms flat backend calculations into semantic structure
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from logging_config import articulation_logger as logger

from consciousness_state import (
    ConsciousnessState, Tier1, Tier2, Tier3, Tier4, Tier5, Tier6,
    CoreOperators, SLevel, Drives,
    Distortions, Chakras, UCBComponents, Gunas, CascadeCleanliness,
    Emotions, Koshas, CirclesQuality, FiveActs, DrivesInternalization,
    CoherenceMetrics, TransformationMatrices, PatternDetection,
    DeathArchitecture, Pathways, PathwayWitnessing, PathwayCreating, PathwayEmbodying,
    PipelineFlow, BreakthroughDynamics, KarmaDynamics, GraceMechanics,
    NetworkEffects, POMDPGaps, MorphogeneticFields,
    TimelinePredictions, TransformationVectors, QuantumMetricsSnapshot, FrequencyAnalysis,
    Bottleneck, LeveragePoint,
    # Unity Principle dataclasses
    UnitySeparationMetrics, DualPathway, PathwayMetrics, GoalContext
)
from nomenclature import (
    get_s_level_label, get_matrix_position, get_manifestation_time_label, get_dominant
)


class ValueOrganizer:
    """
    Organize 450+ flat backend values into semantic categories.
    Input: Raw calculation results from backend
    Output: Structured ConsciousnessState object
    """

    def organize(
        self,
        raw_values: Dict[str, Any],
        tier1_values: Dict[str, Any],
        user_id: str = "",
        session_id: str = ""
    ) -> ConsciousnessState:
        """
        Transform flat backend output into organized consciousness state.

        PURE ARCHITECTURE: Pass context from Call 1 to guide Call 2 value selection.
        UNITY PRINCIPLE: Extract unity metrics and dual pathways for Jeevatma-Paramatma analysis.
        """
        values_count = len(raw_values.get('values')) if isinstance(raw_values, dict) and 'values' in raw_values else len(raw_values)
        logger.info(f"[VALUE_ORGANIZER] Organizing {values_count} computed values into consciousness state")
        logger.debug(f"[VALUE_ORGANIZER] Tier1 keys: {len(tier1_values)} | Targets: {len(tier1_values.get('targets'))}")

        # Split raw values into calculated vs non-calculated (two buckets)
        calculated_values, non_calc_question, non_calc_context = self._split_calculated_values(raw_values)

        # Extract LLM Call 1's missing operator priority (if provided)
        missing_operator_priority = tier1_values.get('missing_operator_priority')

        state = ConsciousnessState(
            timestamp=datetime.now().isoformat(),
            user_id=user_id,
            session_id=session_id,
            tier1=self._organize_tier1(tier1_values),
            tier2=self._organize_tier2(raw_values),
            tier3=self._organize_tier3(raw_values),
            tier4=self._organize_tier4(raw_values),
            tier5=self._organize_tier5(raw_values),
            tier6=self._organize_tier6(raw_values),
            bottlenecks=[],  # Will be populated by BottleneckDetector
            leverage_points=[],  # Will be populated by LeverageIdentifier
            # PURE ARCHITECTURE: Pass Call 1 context to guide Call 2 value selection
            targets=tier1_values.get('targets'),
            query_pattern=tier1_values.get('query_pattern'),
            # UNITY PRINCIPLE: Extract unity metrics and dual pathways
            unity_metrics=self._extract_unity_metrics(raw_values),
            dual_pathways=self._extract_dual_pathways(raw_values),
            goal_context=self._extract_goal_context(tier1_values),
            # ZERO-DEFAULT ARCHITECTURE: Split calculated vs non-calculated (two buckets)
            calculated_values=calculated_values,
            non_calculated_question_addressable=non_calc_question,
            non_calculated_context_addressable=non_calc_context,
            missing_operator_priority=missing_operator_priority
        )

        logger.info(
            f"[VALUE_ORGANIZER] Organization complete: "
            f"S-level={state.tier1.s_level.current} "
            f"calculated={len(calculated_values)} "
            f"question_addressable={len(non_calc_question)} "
            f"context_addressable={len(non_calc_context)} "
            f"missing_operator_priority={len(missing_operator_priority)} "
            f"unity_metrics={'present' if state.unity_metrics else 'None'} "
            f"dual_pathways={'present' if state.dual_pathways else 'None'} "
            f"goal_context={'present' if state.goal_context else 'None'}"
        )

        return state

    def _split_calculated_values(
        self,
        raw_values: Dict[str, Any]
    ) -> tuple:
        """
        Split raw inference values into calculated vs non-calculated buckets.

        ZERO-DEFAULT ARCHITECTURE:
        - calculated: {key: value} — metrics successfully computed
        - question_addressable: [key] — blocked by missing Tier 0 operators;
          a constellation question can fill these, enabling calculation next cycle
        - context_addressable: [key] — blocked by upstream calculation failure;
          not fixable by asking a question, explain in response context

        Bucketing logic:
        - If skipped_modules exists in metadata, any value belonging to a skipped
          module is question_addressable (the module was skipped because required
          operators were missing — those operators are what questions target).
        - Other None values are context_addressable (the module ran but a
          sub-calculation produced None, or summary metrics couldn't be derived).

        Returns:
            Tuple of (calculated_values dict, question_addressable list, context_addressable list)
        """
        values = raw_values.get('values') if isinstance(raw_values, dict) else raw_values
        if not isinstance(values, dict):
            return {}, [], []

        metadata = raw_values.get('metadata', {}) if isinstance(raw_values, dict) else {}
        skipped_modules = set(metadata.get('skipped_modules', []))

        # Build prefix→skipped lookup from skipped module names
        # Module names in inference map to value prefixes in _flatten_profile
        module_to_prefix = {
            "operators": "op", "drives": "drives", "matrices": "matrices",
            "pathways": "pathways", "cascade": "cascade", "emotions": "emotion",
            "death": "death", "collective": "collective", "circles": "circles",
            "kosha": "kosha", "osafc": "osafc", "distortions": "distortion",
            "panchakritya": "panchakritya", "advanced_math": "advmath",
            "hierarchical": "hierarchical", "platform": "platform",
            "multi_reality": "multi_reality", "timeline": "timeline",
            # s_level-dependent modules that also produce summary/additional values
            "dynamics": "grace,karma,transformation", "network": "network",
            "quantum": "quantum", "realism": "realism", "unity": "unity",
        }
        skipped_prefixes = set()
        for mod in skipped_modules:
            prefixes = module_to_prefix.get(mod, mod)
            for p in prefixes.split(","):
                skipped_prefixes.add(p.strip())

        calculated = {}
        question_addressable = []
        context_addressable = []

        for key, value in values.items():
            if value is not None:
                calculated[key] = value
                continue

            # Determine which bucket: does this key belong to a skipped module?
            key_prefix = key.split('_')[0] if '_' in key else key
            if key_prefix in skipped_prefixes:
                question_addressable.append(key)
            else:
                context_addressable.append(key)

        logger.debug(
            f"[_split_calculated_values] total={len(values)} "
            f"calculated={len(calculated)} "
            f"question_addressable={len(question_addressable)} "
            f"context_addressable={len(context_addressable)} "
            f"skipped_prefixes={skipped_prefixes}"
        )
        return calculated, question_addressable, context_addressable

    def _get_value(self, values: Dict[str, Any], *keys, default: Optional[float] = None) -> Optional[float]:
        """Get value from dict, trying multiple key names. Returns None if not found (ZERO-FALLBACK)."""
        for key in keys:
            if key in values:
                val = values[key]
                if isinstance(val, (int, float)):
                    return float(val)
        return default

    def _organize_tier1(self, values: Dict[str, Any]) -> Tier1:
        """Organize Tier 1 values (from LLM Call 1)"""
        logger.debug("[_organize_tier1] entry")
        # Extract core operators from observations
        observations = values.get('observations')
        obs_dict = {}
        for obs in observations:
            if isinstance(obs, dict) and 'var' in obs and 'value' in obs:
                obs_dict[obs['var']] = obs['value']

        logger.debug(f"[_organize_tier1] observations={len(observations)} extracted_operators={len(obs_dict)}")

        core_operators = CoreOperators(
            P_presence=self._get_value(obs_dict, 'P', 'Presence', 'Prana', default=None),
            A_aware=self._get_value(obs_dict, 'A', 'Awareness', default=None),
            E_equanimity=self._get_value(obs_dict, 'E', 'Equanimity', 'Entropy', default=None),
            Psi_quality=self._get_value(obs_dict, 'Ψ', 'Psi', 'Consciousness', default=None),
            M_maya=self._get_value(obs_dict, 'M', 'Maya', default=None),
            M_manifest=self._get_value(obs_dict, 'Manifestation', default=None),
            W_witness=self._get_value(obs_dict, 'W', 'Witness', default=None),
            I_intention=self._get_value(obs_dict, 'I', 'Intention', default=None),
            At_attachment=self._get_value(obs_dict, 'At', 'Attachment', default=None),
            Se_service=self._get_value(obs_dict, 'Se', 'Seva', 'Service', default=None),
            Sh_shakti=self._get_value(obs_dict, 'Sh', 'Shakti', default=None),
            G_grace=self._get_value(obs_dict, 'G', 'Grace', default=None),
            S_surrender=self._get_value(obs_dict, 'Su', 'Surrender', default=None),
            D_dharma=self._get_value(obs_dict, 'D', 'Dharma', default=None),
            K_karma=self._get_value(obs_dict, 'K', 'Karma', default=None),
            Hf_habit=self._get_value(obs_dict, 'Hf', 'HabitForce', default=None),
            V_void=self._get_value(obs_dict, 'V', 'Void', default=None),
            T_time_past=self._get_value(obs_dict, 'T_past', default=None),
            T_time_present=self._get_value(obs_dict, 'T_present', default=None),
            T_time_future=self._get_value(obs_dict, 'T_future', default=None),
            Ce_cleaning=self._get_value(obs_dict, 'Ce', 'Celebration', default=None),
            Co_coherence=self._get_value(obs_dict, 'Co', 'Coherence', default=None),
            R_resistance=self._get_value(obs_dict, 'R', 'Re', 'Resistance', default=None),
            F_fear=self._get_value(obs_dict, 'F', 'Fe', 'Fear', default=None),
            J_joy=self._get_value(obs_dict, 'J', 'Joy', default=None),
            Tr_trust=self._get_value(obs_dict, 'Tr', 'Trust', default=None),
            O_openness=self._get_value(obs_dict, 'O', 'Openness', default=None)
        )

        # Parse S-level — ZERO-FALLBACK: None if not provided
        s_level_str = values.get('s_level')
        s_level_num = None
        if isinstance(s_level_str, str):
            # Extract number from strings like "S3", "S4: Service", etc.
            import re
            match = re.search(r'S(\d)', s_level_str)
            if match:
                s_level_num = float(match.group(1))
        elif isinstance(s_level_str, (int, float)):
            s_level_num = float(s_level_str)

        s_level = SLevel(
            current=s_level_num,
            label=get_s_level_label(s_level_num),
            transition_rate=self._get_value(values, 'dS_dt', 'evolution_rate', default=None)
        )

        # Parse drives
        drives = Drives(
            love_strength=self._get_value(obs_dict, 'L', 'Love', default=None),
            peace_strength=self._get_value(values, 'drive_peace', default=None),
            bliss_strength=self._get_value(values, 'drive_bliss', default=None),
            satisfaction_strength=self._get_value(values, 'drive_satisfaction', default=None),
            freedom_strength=self._get_value(values, 'drive_freedom', default=None)
        )

        # Log operator population stats
        op_vals = [
            core_operators.P_presence, core_operators.A_aware, core_operators.E_equanimity,
            core_operators.M_maya, core_operators.W_witness, core_operators.I_intention,
            core_operators.At_attachment, core_operators.Se_service, core_operators.G_grace,
            core_operators.S_surrender, core_operators.D_dharma, core_operators.K_karma,
            core_operators.Hf_habit, core_operators.Co_coherence, core_operators.R_resistance,
            core_operators.F_fear,
        ]
        populated = sum(1 for v in op_vals if v is not None)
        none_count = len(op_vals) - populated
        logger.debug(
            f"[_organize_tier1] result: operators_populated={populated} "
            f"operators_none={none_count} s_level={s_level.current}"
        )

        return Tier1(
            core_operators=core_operators,
            s_level=s_level,
            drives=drives
        )

    def _organize_tier2(self, values: Dict[str, Any]) -> Tier2:
        """Organize Tier 2 values (simple derivations)"""
        logger.debug("[_organize_tier2] entry")
        v = values.get('values')

        distortions = Distortions(
            avarana_shakti=self._get_value(v, 'avarana', 'avarana_shakti', default=None),
            vikshepa_shakti=self._get_value(v, 'vikshepa', 'vikshepa_shakti', default=None),
            maya_vrittis=self._get_value(v, 'maya_vrittis', default=None),
            asmita=self._get_value(v, 'asmita', default=None),
            raga=self._get_value(v, 'raga', default=None),
            dvesha=self._get_value(v, 'dvesha', default=None),
            abhinivesha=self._get_value(v, 'abhinivesha', default=None),
            avidya_total=self._get_value(v, 'avidya_total', 'avidya', default=None)
        )

        chakras = Chakras(
            muladhara=self._get_value(v, 'chakra_1', 'muladhara', default=None),
            svadhisthana=self._get_value(v, 'chakra_2', 'svadhisthana', default=None),
            manipura=self._get_value(v, 'chakra_3', 'manipura', default=None),
            anahata=self._get_value(v, 'chakra_4', 'anahata', default=None),
            vishuddha=self._get_value(v, 'chakra_5', 'vishuddha', default=None),
            ajna=self._get_value(v, 'chakra_6', 'ajna', default=None),
            sahasrara=self._get_value(v, 'chakra_7', 'sahasrara', default=None)
        )

        ucb_components = UCBComponents(
            P_t=self._get_value(v, 'UCB_P', default=None),
            A_t=self._get_value(v, 'UCB_A', default=None),
            E_t=self._get_value(v, 'UCB_E', default=None),
            Psi_t=self._get_value(v, 'UCB_Psi', default=None),
            M_t=self._get_value(v, 'UCB_M', default=None),
            L_fg=self._get_value(v, 'UCB_L', default=None),
            G_t=self._get_value(v, 'UCB_G', default=None),
            S_t=self._get_value(v, 'UCB_S', default=None)
        )

        sattva = self._get_value(v, 'guna_sattva', 'sattva', default=None)
        rajas = self._get_value(v, 'guna_rajas', 'rajas', default=None)
        tamas = self._get_value(v, 'guna_tamas', 'tamas', default=None)
        gunas = Gunas(
            sattva=sattva,
            rajas=rajas,
            tamas=tamas,
            dominant=get_dominant({'sattva': sattva, 'rajas': rajas, 'tamas': tamas})
        )

        cascade_cleanliness = CascadeCleanliness(
            self_level=self._get_value(v, 'cascade_1', 'cascade_self', default=None),
            ego=self._get_value(v, 'cascade_2', 'cascade_ego', default=None),
            memory=self._get_value(v, 'cascade_3', 'cascade_memory', default=None),
            intellect=self._get_value(v, 'cascade_4', 'cascade_intellect', default=None),
            mind=self._get_value(v, 'cascade_5', 'cascade_mind', default=None),
            breath=self._get_value(v, 'cascade_6', 'cascade_breath', default=None),
            body=self._get_value(v, 'cascade_7', 'cascade_body', default=None),
            average=self._get_value(v, 'cascade_avg', default=None)
        )

        emotion_values = {
            'shringara': self._get_value(v, 'rasa_shringara', 'shringara', default=None),
            'hasya': self._get_value(v, 'rasa_hasya', 'hasya', default=None),
            'karuna': self._get_value(v, 'rasa_karuna', 'karuna', default=None),
            'raudra': self._get_value(v, 'rasa_raudra', 'raudra', default=None),
            'veera': self._get_value(v, 'rasa_veera', 'veera', default=None),
            'bhayanaka': self._get_value(v, 'rasa_bhayanaka', 'bhayanaka', default=None),
            'adbhuta': self._get_value(v, 'rasa_adbhuta', 'adbhuta', default=None),
            'shanta': self._get_value(v, 'rasa_shanta', 'shanta', default=None),
            'bibhatsa': self._get_value(v, 'rasa_bibhatsa', 'bibhatsa', default=None)
        }
        emotions = Emotions(
            **emotion_values,
            dominant=get_dominant(emotion_values)
        )

        koshas = Koshas(
            annamaya=self._get_value(v, 'kosha_anna', 'annamaya', default=None),
            pranamaya=self._get_value(v, 'kosha_prana', 'pranamaya', default=None),
            manomaya=self._get_value(v, 'kosha_mano', 'manomaya', default=None),
            vijnanamaya=self._get_value(v, 'kosha_vijnana', 'vijnanamaya', default=None),
            anandamaya=self._get_value(v, 'kosha_ananda', 'anandamaya', default=None)
        )

        circle_values = {
            'personal': self._get_value(v, 'circle_personal', default=None),
            'family': self._get_value(v, 'circle_family', default=None),
            'social': self._get_value(v, 'circle_social', default=None),
            'professional': self._get_value(v, 'circle_professional', default=None),
            'universal': self._get_value(v, 'circle_universal', default=None)
        }
        circles_quality = CirclesQuality(
            **circle_values,
            dominant=get_dominant(circle_values)
        )

        act_values = {
            'srishti_creation': self._get_value(v, 'act_srishti', default=None),
            'sthiti_maintenance': self._get_value(v, 'act_sthiti', default=None),
            'samhara_dissolution': self._get_value(v, 'act_samhara', default=None),
            'tirodhana_concealment': self._get_value(v, 'act_tirodhana', default=None),
            'anugraha_grace': self._get_value(v, 'act_anugraha', default=None)
        }
        five_acts = FiveActs(
            **act_values,
            balance=self._get_value(v, 'acts_balance', default=None),
            dominant=get_dominant(act_values)
        )

        drives_internalization = DrivesInternalization(
            love_internal_pct=self._get_value(v, 'love_internal_pct', default=None),
            love_external_pct=self._get_value(v, 'love_external_pct', default=None),
            peace_internal_pct=self._get_value(v, 'peace_internal_pct', default=None),
            peace_external_pct=self._get_value(v, 'peace_external_pct', default=None),
            bliss_internal_pct=self._get_value(v, 'bliss_internal_pct', default=None),
            bliss_external_pct=self._get_value(v, 'bliss_external_pct', default=None),
            satisfaction_internal_pct=self._get_value(v, 'satisfaction_internal_pct', default=None),
            satisfaction_external_pct=self._get_value(v, 'satisfaction_external_pct', default=None),
            freedom_internal_pct=self._get_value(v, 'freedom_internal_pct', default=None),
            freedom_external_pct=self._get_value(v, 'freedom_external_pct', default=None)
        )

        logger.debug(
            f"[_organize_tier2] result: gunas_dominant={gunas.dominant} "
            f"emotions_dominant={emotions.dominant} circles_dominant={circles_quality.dominant} "
            f"five_acts_dominant={five_acts.dominant}"
        )

        return Tier2(
            distortions=distortions,
            chakras=chakras,
            ucb_components=ucb_components,
            gunas=gunas,
            cascade_cleanliness=cascade_cleanliness,
            emotions=emotions,
            koshas=koshas,
            circles_quality=circles_quality,
            five_acts=five_acts,
            drives_internalization=drives_internalization
        )

    def _organize_tier3(self, values: Dict[str, Any]) -> Tier3:
        """Organize Tier 3 values (complex combinations)"""
        logger.debug("[_organize_tier3] entry")
        v = values.get('values')

        coherence_metrics = CoherenceMetrics(
            fundamental=self._get_value(v, 'coherence_fundamental', default=None),
            specification=self._get_value(v, 'coherence_spec', 'coherence_specification', default=None),
            hierarchical=self._get_value(v, 'coherence_hierarchical', default=None),
            temporal=self._get_value(v, 'coherence_temporal', default=None),
            collective=self._get_value(v, 'coherence_collective', default=None),
            overall=self._get_value(v, 'coherence_overall', 'Coherence', default=None)
        )

        truth_score = self._get_value(v, 'matrix_truth_score', 'truth_matrix', default=None)
        love_score = self._get_value(v, 'matrix_love_score', 'love_matrix', default=None)
        power_score = self._get_value(v, 'matrix_power_score', 'power_matrix', default=None)
        freedom_score = self._get_value(v, 'matrix_freedom_score', 'freedom_matrix', default=None)
        creation_score = self._get_value(v, 'matrix_creation_score', 'creation_matrix', default=None)
        time_score = self._get_value(v, 'matrix_time_score', 'time_matrix', default=None)
        death_score = self._get_value(v, 'matrix_death_score', 'death_matrix', default=None)

        transformation_matrices = TransformationMatrices(
            truth_position=get_matrix_position('truth', truth_score),
            truth_score=truth_score,
            love_position=get_matrix_position('love', love_score),
            love_score=love_score,
            power_position=get_matrix_position('power', power_score),
            power_score=power_score,
            freedom_position=get_matrix_position('freedom', freedom_score),
            freedom_score=freedom_score,
            creation_position=get_matrix_position('creation', creation_score),
            creation_score=creation_score,
            time_position=get_matrix_position('time', time_score),
            time_score=time_score,
            death_position=get_matrix_position('death', death_score),
            death_score=death_score
        )

        pattern_detection = PatternDetection(
            zero_detection=v.get('pattern_zero'),
            bottleneck_scan=v.get('pattern_bottlenecks'),
            inverse_pair_check=v.get('pattern_inverse_pairs'),
            power_trinity_check=v.get('pattern_power_trinity'),
            golden_ratio_validation=v.get('pattern_golden_ratio')
        )

        active_process = v.get('death_active')
        death_architecture = DeathArchitecture(
            d1_identity=self._get_value(v, 'death_d1', default=None),
            d2_belief=self._get_value(v, 'death_d2', default=None),
            d3_emotion=self._get_value(v, 'death_d3', default=None),
            d4_attachment=self._get_value(v, 'death_d4', default=None),
            d5_control=self._get_value(v, 'death_d5', default=None),
            d6_separation=self._get_value(v, 'death_d6', default=None),
            d7_ego=self._get_value(v, 'death_d7', default=None),
            active_process=active_process if isinstance(active_process, str) else None,
            depth=self._get_value(v, 'death_depth', default=None)
        )

        pathways = Pathways(
            witnessing=PathwayWitnessing(
                observation=self._get_value(v, 'pathway_witness_obs', default=None),
                perception=self._get_value(v, 'pathway_witness_perc', default=None),
                expression=self._get_value(v, 'pathway_witness_expr', default=None)
            ),
            creating=PathwayCreating(
                intention=self._get_value(v, 'pathway_create_intent', default=None),
                attention=self._get_value(v, 'pathway_create_attn', default=None),
                manifestation=self._get_value(v, 'pathway_create_manifest', default=None)
            ),
            embodying=PathwayEmbodying(
                thoughts=self._get_value(v, 'pathway_embody_thoughts', default=None),
                words=self._get_value(v, 'pathway_embody_words', default=None),
                actions=self._get_value(v, 'pathway_embody_actions', default=None)
            )
        )

        matrix_scores = [truth_score, love_score, power_score, freedom_score, creation_score, time_score, death_score]
        matrices_present = sum(1 for s in matrix_scores if s is not None)
        logger.debug(
            f"[_organize_tier3] result: matrices_present={matrices_present}/7 "
            f"coherence_overall={coherence_metrics.overall} "
            f"death_active={death_architecture.active_process} "
            f"death_depth={death_architecture.depth}"
        )

        return Tier3(
            coherence_metrics=coherence_metrics,
            transformation_matrices=transformation_matrices,
            pattern_detection=pattern_detection,
            death_architecture=death_architecture,
            pathways=pathways
        )

    def _organize_tier4(self, values: Dict[str, Any]) -> Tier4:
        """Organize Tier 4 values (network & dynamics)"""
        logger.debug("[_organize_tier4] entry")
        v = values.get('values')

        manifestation_days = self._get_value(v, 'manifestation_time_days', default=None)
        pipeline_flow = PipelineFlow(
            stage_1_turiya=self._get_value(v, 'pipeline_stage1', default=None),
            stage_2_anandamaya=self._get_value(v, 'pipeline_stage2', default=None),
            stage_3_vijnanamaya=self._get_value(v, 'pipeline_stage3', default=None),
            stage_4_manomaya=self._get_value(v, 'pipeline_stage4', default=None),
            stage_5_pranamaya=self._get_value(v, 'pipeline_stage5', default=None),
            stage_6_annamaya=self._get_value(v, 'pipeline_stage6', default=None),
            stage_7_external=self._get_value(v, 'pipeline_stage7', default=None),
            flow_rate=self._get_value(v, 'pipeline_flow_rate', default=None),
            manifestation_time=get_manifestation_time_label(manifestation_days)
        )

        breakthrough_dynamics = BreakthroughDynamics(
            probability=self._get_value(v, 'breakthrough_prob', default=None),
            tipping_point_distance=self._get_value(v, 'breakthrough_tipping', default=None),
            quantum_jump_prob=self._get_value(v, 'quantum_jump_prob', default=None),
            operators_at_threshold=v.get('breakthrough_operators')
        )

        karma_dynamics = KarmaDynamics(
            sanchita_stored=self._get_value(v, 'karma_sanchita', default=None),
            prarabdha_active=self._get_value(v, 'karma_prarabdha', default=None),
            kriyamana_creating=self._get_value(v, 'karma_kriyamana', default=None),
            burn_rate=self._get_value(v, 'karma_burn_rate', default=None),
            allowance_factor=self._get_value(v, 'karma_allowance', default=None)
        )

        grace_mechanics = GraceMechanics(
            availability=self._get_value(v, 'grace_availability', 'Grace', default=None),
            effectiveness=self._get_value(v, 'grace_effectiveness', default=None),
            multiplication_factor=self._get_value(v, 'grace_multiplier', default=None),
            timing_probability=self._get_value(v, 'grace_timing_prob', default=None)
        )

        network_effects = NetworkEffects(
            coherence_multiplier=self._get_value(v, 'network_coherence_mult', default=None),
            acceleration_factor=self._get_value(v, 'network_accel', default=None),
            collective_breakthrough_prob=self._get_value(v, 'network_breakthrough_prob', default=None),
            resonance_amplification=self._get_value(v, 'network_resonance', default=None),
            group_mind_iq=v.get('network_group_iq')
        )

        pomdp_gaps = POMDPGaps(
            reality_gap=self._get_value(v, 'pomdp_reality_gap', default=None),
            observation_gap=self._get_value(v, 'pomdp_obs_gap', default=None),
            belief_gap=self._get_value(v, 'pomdp_belief_gap', default=None),
            severity=self._get_value(v, 'pomdp_severity', default=None)
        )

        morphogenetic_fields = MorphogeneticFields(
            field_strength=self._get_value(v, 'morph_field_strength', default=None),
            access_probability=self._get_value(v, 'morph_access_prob', default=None),
            information_transfer_rate=self._get_value(v, 'morph_info_transfer', default=None)
        )

        logger.debug(
            f"[_organize_tier4] result: breakthrough_prob={breakthrough_dynamics.probability} "
            f"grace_avail={grace_mechanics.availability} "
            f"grace_effect={grace_mechanics.effectiveness} "
            f"pomdp_severity={pomdp_gaps.severity} "
            f"pipeline_flow_rate={pipeline_flow.flow_rate}"
        )

        return Tier4(
            pipeline_flow=pipeline_flow,
            breakthrough_dynamics=breakthrough_dynamics,
            karma_dynamics=karma_dynamics,
            grace_mechanics=grace_mechanics,
            network_effects=network_effects,
            pomdp_gaps=pomdp_gaps,
            morphogenetic_fields=morphogenetic_fields
        )

    def _organize_tier5(self, values: Dict[str, Any]) -> Tier5:
        """Organize Tier 5 values (predictions & advanced)"""
        logger.debug("[_organize_tier5] entry")
        v = values.get('values')

        timeline_predictions = TimelinePredictions(
            to_goal=v.get('timeline_to_goal'),
            to_next_s_level=v.get('timeline_to_next_s'),
            evolution_rate=self._get_value(v, 'evolution_rate', default=None),
            acceleration_factor=self._get_value(v, 'evolution_accel', default=None)
        )

        transformation_vectors = TransformationVectors(
            current_state_summary=v.get('transform_current'),
            target_state_summary=v.get('transform_target'),
            core_shift_required=v.get('transform_shift'),
            primary_obstacle=v.get('transform_obstacle'),
            primary_enabler=v.get('transform_enabler'),
            leverage_point=v.get('transform_leverage'),
            evolution_direction=v.get('transform_direction')
        )

        quantum_mechanics = QuantumMetricsSnapshot(
            wave_function_amplitude=self._get_value(v, 'quantum_amplitude', default=None),
            collapse_probability=v.get('quantum_collapse_prob'),
            tunneling_probability=self._get_value(v, 'quantum_tunnel_prob', default=None),
            interference_strength=self._get_value(v, 'quantum_interference', default=None)
        )

        frequency_analysis = FrequencyAnalysis(
            dominant_frequency=self._get_value(v, 'freq_dominant', default=None),
            harmonic_content=v.get('freq_harmonics'),
            power_spectral_density=self._get_value(v, 'freq_psd', default=None),
            resonance_strength=self._get_value(v, 'freq_resonance', default=None),
            decoherence_time=self._get_value(v, 'freq_decoherence', default=None)
        )

        logger.debug(
            f"[_organize_tier5] result: timeline_to_goal={timeline_predictions.to_goal} "
            f"evolution_rate={timeline_predictions.evolution_rate} "
            f"current_state={'present' if transformation_vectors.current_state_summary else 'empty'} "
            f"target_state={'present' if transformation_vectors.target_state_summary else 'empty'}"
        )

        return Tier5(
            timeline_predictions=timeline_predictions,
            transformation_vectors=transformation_vectors,
            quantum_mechanics=quantum_mechanics,
            frequency_analysis=frequency_analysis
        )

    def _organize_tier6(self, values: Dict[str, Any]) -> Tier6:
        """Organize Tier 6 values (quantum fields)"""
        logger.debug("[_organize_tier6] entry")
        v = values.get('values')

        field_charge = self._get_value(v, 'field_charge', default=None)
        field_current = self._get_value(v, 'field_current', default=None)
        curvature = self._get_value(v, 'consciousness_curvature', default=None)

        logger.debug(
            f"[_organize_tier6] result: field_charge={field_charge} "
            f"field_current={field_current} curvature={curvature}"
        )

        return Tier6(
            field_charge_density=field_charge,
            field_current_density=field_current,
            consciousness_curvature=curvature
        )

    def _extract_unity_metrics(self, values: Dict[str, Any]) -> UnitySeparationMetrics:
        """
        Extract Unity Principle metrics from calculated values.

        UNITY PRINCIPLE: Jeevatma-Paramatma dynamics
        - separation_distance: Current distance from Source (exponentially decays with S-level)
        - distortion_field: How much Maya distorts perception
        - percolation_quality: How well grace/prana flows through
        - unity_vector: Net direction toward unity (-1 to +1)
        """
        logger.debug("[_extract_unity_metrics] entry")
        v = values.get('values')

        metrics = UnitySeparationMetrics(
            separation_distance=self._get_value(v, 'unity_separation_distance', default=None),
            distortion_field=self._get_value(v, 'unity_distortion_field', default=None),
            percolation_quality=self._get_value(v, 'unity_percolation_quality', default=None),
            unity_vector=self._get_value(v, 'unity_vector', default=None),
            net_direction=v.get('unity_net_direction')
        )

        none_fields = [
            name for name, val in [
                ('separation_distance', metrics.separation_distance),
                ('distortion_field', metrics.distortion_field),
                ('percolation_quality', metrics.percolation_quality),
                ('unity_vector', metrics.unity_vector),
            ] if val is None
        ]
        if none_fields:
            logger.warning(f"[_extract_unity_metrics] missing: {none_fields}")

        logger.debug(
            f"[_extract_unity_metrics] result: sep_dist={metrics.separation_distance} "
            f"distortion={metrics.distortion_field} percolation={metrics.percolation_quality} "
            f"vector={metrics.unity_vector} direction={metrics.net_direction}"
        )
        return metrics

    def _extract_dual_pathways(self, values: Dict[str, Any]) -> DualPathway:
        """
        Extract dual pathway analysis from calculated values.

        DUAL PATHWAY REALITY: Every goal can be pursued through:
        - Separation pathway: Effort-based, initially faster but decays
        - Unity pathway: Grace-aligned, initially slower but compounds

        The crossover point shows when unity pathway overtakes separation.
        """
        logger.debug("[_extract_dual_pathways] entry")
        v = values.get('values')

        # Build separation pathway metrics
        separation_pathway = PathwayMetrics(
            initial_success_probability=self._get_value(v, 'pathway_separation_initial_success', default=None),
            sustainability_probability=self._get_value(v, 'pathway_separation_sustainability', default=None),
            fulfillment_quality=self._get_value(v, 'pathway_separation_fulfillment', default=None),
            decay_rate=self._get_value(v, 'pathway_separation_decay_rate', default=None),
            compound_rate=0.0,  # Separation doesn't compound
            time_to_goal_months=self._get_value(v, 'pathway_separation_time_months', default=None),
            effort_required=self._get_value(v, 'pathway_separation_effort', default=None),
            grace_utilization=0.0  # Separation doesn't use grace
        )

        # Build unity pathway metrics
        unity_pathway = PathwayMetrics(
            initial_success_probability=self._get_value(v, 'pathway_unity_initial_success', default=None),
            sustainability_probability=self._get_value(v, 'pathway_unity_sustainability', default=None),
            fulfillment_quality=self._get_value(v, 'pathway_unity_fulfillment', default=None),
            decay_rate=0.0,  # Unity doesn't decay
            compound_rate=self._get_value(v, 'pathway_unity_compound_rate', default=None),
            time_to_goal_months=self._get_value(v, 'pathway_unity_time_months', default=None),
            effort_required=self._get_value(v, 'pathway_unity_effort', default=None),
            grace_utilization=self._get_value(v, 'pathway_unity_grace_util', default=None)
        )

        dp = DualPathway(
            separation_pathway=separation_pathway,
            unity_pathway=unity_pathway,
            crossover_point_months=self._get_value(v, 'pathway_crossover_months', default=None),
            recommended_pathway=v.get('pathway_recommendation'),
            optimal_blend_ratio=self._get_value(v, 'pathway_blend_ratio', default=None)
        )

        sep_has_data = separation_pathway.initial_success_probability is not None
        uni_has_data = unity_pathway.initial_success_probability is not None
        if not sep_has_data and not uni_has_data:
            logger.warning("[_extract_dual_pathways] missing: no pathway probability data found")

        logger.debug(
            f"[_extract_dual_pathways] result: recommended={dp.recommended_pathway} "
            f"crossover={dp.crossover_point_months} blend_ratio={dp.optimal_blend_ratio} "
            f"sep_data={'present' if sep_has_data else 'None'} "
            f"uni_data={'present' if uni_has_data else 'None'}"
        )
        return dp

    def _extract_goal_context(self, tier1_values: Dict[str, Any]) -> GoalContext:
        """
        Extract goal context from Call 1 analysis.

        GOAL CONTEXT: Determines which constellation patterns apply
        - category: achievement, relationship, peace, or transformation
        - explicit_goal: What the user stated
        - implicit_goal: What the consciousness state reveals
        """
        logger.debug("[_extract_goal_context] entry")
        goal_data = tier1_values.get('goal_context')
        if not goal_data:
            logger.warning("[_extract_goal_context] missing: no goal_context in tier1_values")

        gc = GoalContext(
            category=goal_data.get('category'),
            explicit_goal=goal_data.get('explicit_goal'),
            implicit_goal=goal_data.get('implicit_goal'),
            why_category=goal_data.get('why_category'),
            death_architecture_required=goal_data.get('death_architecture_required'),
            s_level_requirement=goal_data.get('s_level_requirement')
        )
        logger.debug(
            f"[VALUE_ORGANIZER] Goal context extracted: category={gc.category} "
            f"why={gc.why_category} s_req={gc.s_level_requirement} "
            f"explicit='{gc.explicit_goal[:50]}...'"
        )
        return gc
