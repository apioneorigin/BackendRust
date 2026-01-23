"""
Value Organizer Service for Articulation Bridge
Transforms flat backend calculations into semantic structure
"""

from typing import Dict, Any, List
from datetime import datetime

from consciousness_state import (
    ConsciousnessState, Tier1, Tier2, Tier3, Tier4, Tier5, Tier6,
    CoreOperators, SLevel, Drives,
    Distortions, Chakras, UCBComponents, Gunas, CascadeCleanliness,
    Emotions, Koshas, CirclesQuality, FiveActs, DrivesInternalization,
    CoherenceMetrics, TransformationMatrices, PatternDetection,
    DeathArchitecture, Pathways, PathwayWitnessing, PathwayCreating, PathwayEmbodying,
    PipelineFlow, BreakthroughDynamics, KarmaDynamics, GraceMechanics,
    NetworkEffects, POMDPGaps, MorphogeneticFields,
    TimelinePredictions, TransformationVectors, QuantumMechanics, FrequencyAnalysis,
    Bottleneck, LeveragePoint
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
        """
        return ConsciousnessState(
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
            targets=tier1_values.get('targets', []),
            query_pattern=tier1_values.get('query_pattern', '')
        )

    def _get_value(self, values: Dict[str, Any], *keys, default: float = 0.5) -> float:
        """Get value from dict, trying multiple key names"""
        for key in keys:
            if key in values:
                val = values[key]
                if isinstance(val, (int, float)):
                    return float(val)
        return default

    def _organize_tier1(self, values: Dict[str, Any]) -> Tier1:
        """Organize Tier 1 values (from LLM Call 1)"""
        # Extract core operators from observations
        observations = values.get('observations', [])
        obs_dict = {}
        for obs in observations:
            if isinstance(obs, dict) and 'var' in obs and 'value' in obs:
                obs_dict[obs['var']] = obs['value']

        core_operators = CoreOperators(
            P_presence=self._get_value(obs_dict, 'P', 'Presence', 'Prana', default=0.5),
            A_aware=self._get_value(obs_dict, 'A', 'Awareness', default=0.5),
            E_equanimity=self._get_value(obs_dict, 'E', 'Equanimity', 'Entropy', default=0.5),
            Psi_quality=self._get_value(obs_dict, 'Ψ', 'Psi', 'Consciousness', default=0.5),
            M_maya=self._get_value(obs_dict, 'M', 'Maya', default=0.5),
            M_manifest=self._get_value(obs_dict, 'Manifestation', default=0.5),
            W_witness=self._get_value(obs_dict, 'W', 'Witness', default=0.5),
            I_intention=self._get_value(obs_dict, 'I', 'Intention', default=0.5),
            At_attachment=self._get_value(obs_dict, 'At', 'Attachment', default=0.5),
            Se_service=self._get_value(obs_dict, 'Se', 'Seva', 'Service', default=0.5),
            Sh_shakti=self._get_value(obs_dict, 'Sh', 'Shakti', default=0.5),
            G_grace=self._get_value(obs_dict, 'G', 'Grace', default=0.5),
            S_surrender=self._get_value(obs_dict, 'Su', 'Surrender', default=0.5),
            D_dharma=self._get_value(obs_dict, 'D', 'Dharma', default=0.5),
            K_karma=self._get_value(obs_dict, 'K', 'Karma', default=0.5),
            Hf_habit=self._get_value(obs_dict, 'Hf', 'HabitForce', default=0.5),
            V_void=self._get_value(obs_dict, 'V', 'Void', default=0.5),
            T_time_past=self._get_value(obs_dict, 'T_past', default=0.33),
            T_time_present=self._get_value(obs_dict, 'T_present', default=0.34),
            T_time_future=self._get_value(obs_dict, 'T_future', default=0.33),
            Ce_celebration=self._get_value(obs_dict, 'Ce', 'Celebration', default=0.5),
            Co_coherence=self._get_value(obs_dict, 'Co', 'Coherence', default=0.5),
            R_resistance=self._get_value(obs_dict, 'R', 'Re', 'Resistance', default=0.5),
            F_fear=self._get_value(obs_dict, 'F', 'Fe', 'Fear', default=0.5),
            J_joy=self._get_value(obs_dict, 'J', 'Joy', default=0.5),
            Tr_trust=self._get_value(obs_dict, 'Tr', 'Trust', default=0.5),
            O_openness=self._get_value(obs_dict, 'O', 'Openness', default=0.5)
        )

        # Parse S-level
        s_level_str = values.get('s_level', 'S3')
        s_level_num = 3.0
        if isinstance(s_level_str, str):
            # Extract number from strings like "S3", "S4: Service", etc.
            import re
            match = re.search(r'S(\d)', s_level_str)
            if match:
                s_level_num = float(match.group(1))

        s_level = SLevel(
            current=s_level_num,
            label=get_s_level_label(s_level_num),
            transition_rate=self._get_value(values, 'dS_dt', 'evolution_rate', default=0.0)
        )

        # Parse drives
        drives = Drives(
            love_strength=self._get_value(obs_dict, 'L', 'Love', default=0.5),
            peace_strength=self._get_value(values, 'drive_peace', default=0.5),
            bliss_strength=self._get_value(values, 'drive_bliss', default=0.5),
            satisfaction_strength=self._get_value(values, 'drive_satisfaction', default=0.5),
            freedom_strength=self._get_value(values, 'drive_freedom', default=0.5)
        )

        return Tier1(
            core_operators=core_operators,
            s_level=s_level,
            drives=drives
        )

    def _organize_tier2(self, values: Dict[str, Any]) -> Tier2:
        """Organize Tier 2 values (simple derivations)"""
        v = values.get('values', values)

        distortions = Distortions(
            avarana_shakti=self._get_value(v, 'avarana', 'avarana_shakti', default=0.5),
            vikshepa_shakti=self._get_value(v, 'vikshepa', 'vikshepa_shakti', default=0.5),
            maya_vrittis=self._get_value(v, 'maya_vrittis', default=0.5),
            asmita=self._get_value(v, 'asmita', default=0.5),
            raga=self._get_value(v, 'raga', default=0.5),
            dvesha=self._get_value(v, 'dvesha', default=0.5),
            abhinivesha=self._get_value(v, 'abhinivesha', default=0.5),
            avidya_total=self._get_value(v, 'avidya_total', 'avidya', default=0.5)
        )

        chakras = Chakras(
            muladhara=self._get_value(v, 'chakra_1', 'muladhara', default=0.5),
            svadhisthana=self._get_value(v, 'chakra_2', 'svadhisthana', default=0.5),
            manipura=self._get_value(v, 'chakra_3', 'manipura', default=0.5),
            anahata=self._get_value(v, 'chakra_4', 'anahata', default=0.5),
            vishuddha=self._get_value(v, 'chakra_5', 'vishuddha', default=0.5),
            ajna=self._get_value(v, 'chakra_6', 'ajna', default=0.5),
            sahasrara=self._get_value(v, 'chakra_7', 'sahasrara', default=0.5)
        )

        ucb_components = UCBComponents(
            P_t=self._get_value(v, 'UCB_P', default=0.5),
            A_t=self._get_value(v, 'UCB_A', default=0.5),
            E_t=self._get_value(v, 'UCB_E', default=0.5),
            Psi_t=self._get_value(v, 'UCB_Psi', default=0.5),
            M_t=self._get_value(v, 'UCB_M', default=0.5),
            L_fg=self._get_value(v, 'UCB_L', default=0.5),
            G_t=self._get_value(v, 'UCB_G', default=0.5),
            S_t=self._get_value(v, 'UCB_S', default=0.5)
        )

        sattva = self._get_value(v, 'guna_sattva', 'sattva', default=0.33)
        rajas = self._get_value(v, 'guna_rajas', 'rajas', default=0.34)
        tamas = self._get_value(v, 'guna_tamas', 'tamas', default=0.33)
        gunas = Gunas(
            sattva=sattva,
            rajas=rajas,
            tamas=tamas,
            dominant=get_dominant({'sattva': sattva, 'rajas': rajas, 'tamas': tamas})
        )

        cascade_cleanliness = CascadeCleanliness(
            self=self._get_value(v, 'cascade_1', 'cascade_self', default=0.5),
            ego=self._get_value(v, 'cascade_2', 'cascade_ego', default=0.5),
            memory=self._get_value(v, 'cascade_3', 'cascade_memory', default=0.5),
            intellect=self._get_value(v, 'cascade_4', 'cascade_intellect', default=0.5),
            mind=self._get_value(v, 'cascade_5', 'cascade_mind', default=0.5),
            breath=self._get_value(v, 'cascade_6', 'cascade_breath', default=0.5),
            body=self._get_value(v, 'cascade_7', 'cascade_body', default=0.5),
            average=self._get_value(v, 'cascade_avg', default=0.5)
        )

        emotion_values = {
            'shringara': self._get_value(v, 'rasa_shringara', 'shringara', default=0.5),
            'hasya': self._get_value(v, 'rasa_hasya', 'hasya', default=0.5),
            'karuna': self._get_value(v, 'rasa_karuna', 'karuna', default=0.5),
            'raudra': self._get_value(v, 'rasa_raudra', 'raudra', default=0.5),
            'veera': self._get_value(v, 'rasa_veera', 'veera', default=0.5),
            'bhayanaka': self._get_value(v, 'rasa_bhayanaka', 'bhayanaka', default=0.5),
            'adbhuta': self._get_value(v, 'rasa_adbhuta', 'adbhuta', default=0.5),
            'shanta': self._get_value(v, 'rasa_shanta', 'shanta', default=0.5),
            'bibhatsa': self._get_value(v, 'rasa_bibhatsa', 'bibhatsa', default=0.5)
        }
        emotions = Emotions(
            **emotion_values,
            dominant=get_dominant(emotion_values)
        )

        koshas = Koshas(
            annamaya=self._get_value(v, 'kosha_anna', 'annamaya', default=0.5),
            pranamaya=self._get_value(v, 'kosha_prana', 'pranamaya', default=0.5),
            manomaya=self._get_value(v, 'kosha_mano', 'manomaya', default=0.5),
            vijnanamaya=self._get_value(v, 'kosha_vijnana', 'vijnanamaya', default=0.5),
            anandamaya=self._get_value(v, 'kosha_ananda', 'anandamaya', default=0.5)
        )

        circle_values = {
            'personal': self._get_value(v, 'circle_personal', default=0.5),
            'family': self._get_value(v, 'circle_family', default=0.5),
            'social': self._get_value(v, 'circle_social', default=0.5),
            'professional': self._get_value(v, 'circle_professional', default=0.5),
            'universal': self._get_value(v, 'circle_universal', default=0.5)
        }
        circles_quality = CirclesQuality(
            **circle_values,
            dominant=get_dominant(circle_values)
        )

        act_values = {
            'srishti_creation': self._get_value(v, 'act_srishti', default=0.5),
            'sthiti_maintenance': self._get_value(v, 'act_sthiti', default=0.5),
            'samhara_dissolution': self._get_value(v, 'act_samhara', default=0.5),
            'tirodhana_concealment': self._get_value(v, 'act_tirodhana', default=0.5),
            'anugraha_grace': self._get_value(v, 'act_anugraha', default=0.5)
        }
        five_acts = FiveActs(
            **act_values,
            balance=self._get_value(v, 'acts_balance', default=0.5),
            dominant=get_dominant(act_values)
        )

        drives_internalization = DrivesInternalization(
            love_internal_pct=self._get_value(v, 'love_internal_pct', default=50.0),
            love_external_pct=self._get_value(v, 'love_external_pct', default=50.0),
            peace_internal_pct=self._get_value(v, 'peace_internal_pct', default=50.0),
            peace_external_pct=self._get_value(v, 'peace_external_pct', default=50.0),
            bliss_internal_pct=self._get_value(v, 'bliss_internal_pct', default=50.0),
            bliss_external_pct=self._get_value(v, 'bliss_external_pct', default=50.0),
            satisfaction_internal_pct=self._get_value(v, 'satisfaction_internal_pct', default=50.0),
            satisfaction_external_pct=self._get_value(v, 'satisfaction_external_pct', default=50.0),
            freedom_internal_pct=self._get_value(v, 'freedom_internal_pct', default=50.0),
            freedom_external_pct=self._get_value(v, 'freedom_external_pct', default=50.0)
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
        v = values.get('values', values)

        coherence_metrics = CoherenceMetrics(
            fundamental=self._get_value(v, 'coherence_fundamental', default=0.5),
            specification=self._get_value(v, 'coherence_spec', 'coherence_specification', default=0.5),
            hierarchical=self._get_value(v, 'coherence_hierarchical', default=0.5),
            temporal=self._get_value(v, 'coherence_temporal', default=0.5),
            collective=self._get_value(v, 'coherence_collective', default=0.5),
            overall=self._get_value(v, 'coherence_overall', 'Coherence', default=0.5)
        )

        truth_score = self._get_value(v, 'matrix_truth_score', 'truth_matrix', default=0.5)
        love_score = self._get_value(v, 'matrix_love_score', 'love_matrix', default=0.5)
        power_score = self._get_value(v, 'matrix_power_score', 'power_matrix', default=0.5)
        freedom_score = self._get_value(v, 'matrix_freedom_score', 'freedom_matrix', default=0.5)
        creation_score = self._get_value(v, 'matrix_creation_score', 'creation_matrix', default=0.5)
        time_score = self._get_value(v, 'matrix_time_score', 'time_matrix', default=0.5)
        death_score = self._get_value(v, 'matrix_death_score', 'death_matrix', default=0.5)

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
            zero_detection=v.get('pattern_zero', False),
            bottleneck_scan=v.get('pattern_bottlenecks', []),
            inverse_pair_check=v.get('pattern_inverse_pairs', {"found": False, "pairs": []}),
            power_trinity_check=v.get('pattern_power_trinity', {"found": False, "operators": []}),
            golden_ratio_validation=v.get('pattern_golden_ratio', {"found": False, "ratios": []})
        )

        active_process = v.get('death_active', None)
        death_architecture = DeathArchitecture(
            d1_identity=self._get_value(v, 'death_d1', default=0.5),
            d2_belief=self._get_value(v, 'death_d2', default=0.5),
            d3_emotion=self._get_value(v, 'death_d3', default=0.5),
            d4_attachment=self._get_value(v, 'death_d4', default=0.5),
            d5_control=self._get_value(v, 'death_d5', default=0.5),
            d6_separation=self._get_value(v, 'death_d6', default=0.5),
            d7_ego=self._get_value(v, 'death_d7', default=0.5),
            active_process=active_process if isinstance(active_process, str) else None,
            depth=self._get_value(v, 'death_depth', default=0.0)
        )

        pathways = Pathways(
            witnessing=PathwayWitnessing(
                observation=self._get_value(v, 'pathway_witness_obs', default=0.5),
                perception=self._get_value(v, 'pathway_witness_perc', default=0.5),
                expression=self._get_value(v, 'pathway_witness_expr', default=0.5)
            ),
            creating=PathwayCreating(
                intention=self._get_value(v, 'pathway_create_intent', default=0.5),
                attention=self._get_value(v, 'pathway_create_attn', default=0.5),
                manifestation=self._get_value(v, 'pathway_create_manifest', default=0.5)
            ),
            embodying=PathwayEmbodying(
                thoughts=self._get_value(v, 'pathway_embody_thoughts', default=0.5),
                words=self._get_value(v, 'pathway_embody_words', default=0.5),
                actions=self._get_value(v, 'pathway_embody_actions', default=0.5)
            )
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
        v = values.get('values', values)

        manifestation_days = self._get_value(v, 'manifestation_time_days', default=30.0)
        pipeline_flow = PipelineFlow(
            stage_1_turiya=self._get_value(v, 'pipeline_stage1', default=0.5),
            stage_2_anandamaya=self._get_value(v, 'pipeline_stage2', default=0.5),
            stage_3_vijnanamaya=self._get_value(v, 'pipeline_stage3', default=0.5),
            stage_4_manomaya=self._get_value(v, 'pipeline_stage4', default=0.5),
            stage_5_pranamaya=self._get_value(v, 'pipeline_stage5', default=0.5),
            stage_6_annamaya=self._get_value(v, 'pipeline_stage6', default=0.5),
            stage_7_external=self._get_value(v, 'pipeline_stage7', default=0.5),
            flow_rate=self._get_value(v, 'pipeline_flow_rate', default=0.5),
            manifestation_time=get_manifestation_time_label(manifestation_days)
        )

        breakthrough_dynamics = BreakthroughDynamics(
            probability=self._get_value(v, 'breakthrough_prob', default=0.1),
            tipping_point_distance=self._get_value(v, 'breakthrough_tipping', default=0.5),
            quantum_jump_prob=self._get_value(v, 'quantum_jump_prob', default=0.05),
            operators_at_threshold=v.get('breakthrough_operators', [])
        )

        karma_dynamics = KarmaDynamics(
            sanchita_stored=self._get_value(v, 'karma_sanchita', default=0.5),
            prarabdha_active=self._get_value(v, 'karma_prarabdha', default=0.5),
            kriyamana_creating=self._get_value(v, 'karma_kriyamana', default=0.5),
            burn_rate=self._get_value(v, 'karma_burn_rate', default=0.1),
            allowance_factor=self._get_value(v, 'karma_allowance', default=0.5)
        )

        grace_mechanics = GraceMechanics(
            availability=self._get_value(v, 'grace_availability', 'Grace', default=0.5),
            effectiveness=self._get_value(v, 'grace_effectiveness', default=0.5),
            multiplication_factor=self._get_value(v, 'grace_multiplier', default=1.0),
            timing_probability=self._get_value(v, 'grace_timing_prob', default=0.5)
        )

        network_effects = NetworkEffects(
            coherence_multiplier=self._get_value(v, 'network_coherence_mult', default=1.0),
            acceleration_factor=self._get_value(v, 'network_accel', default=0.0),
            collective_breakthrough_prob=self._get_value(v, 'network_breakthrough_prob', default=0.1),
            resonance_amplification=self._get_value(v, 'network_resonance', default=0.0),
            group_mind_iq=v.get('network_group_iq', None)
        )

        pomdp_gaps = POMDPGaps(
            reality_gap=self._get_value(v, 'pomdp_reality_gap', default=0.3),
            observation_gap=self._get_value(v, 'pomdp_obs_gap', default=0.3),
            belief_gap=self._get_value(v, 'pomdp_belief_gap', default=0.3),
            severity=self._get_value(v, 'pomdp_severity', default=0.3)
        )

        morphogenetic_fields = MorphogeneticFields(
            field_strength=self._get_value(v, 'morph_field_strength', default=0.5),
            access_probability=self._get_value(v, 'morph_access_prob', default=0.5),
            information_transfer_rate=self._get_value(v, 'morph_info_transfer', default=0.5)
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
        v = values.get('values', values)

        timeline_predictions = TimelinePredictions(
            to_goal=v.get('timeline_to_goal', "unknown"),
            to_next_s_level=v.get('timeline_to_next_s', "unknown"),
            evolution_rate=self._get_value(v, 'evolution_rate', default=0.0),
            acceleration_factor=self._get_value(v, 'evolution_accel', default=1.0)
        )

        transformation_vectors = TransformationVectors(
            current_state_summary=v.get('transform_current', ""),
            target_state_summary=v.get('transform_target', ""),
            core_shift_required=v.get('transform_shift', ""),
            primary_obstacle=v.get('transform_obstacle', ""),
            primary_enabler=v.get('transform_enabler', ""),
            leverage_point=v.get('transform_leverage', ""),
            evolution_direction=v.get('transform_direction', "")
        )

        quantum_mechanics = QuantumMechanics(
            wave_function_amplitude=self._get_value(v, 'quantum_amplitude', default=0.5),
            collapse_probability=v.get('quantum_collapse_prob', {}),
            tunneling_probability=self._get_value(v, 'quantum_tunnel_prob', default=0.1),
            interference_strength=self._get_value(v, 'quantum_interference', default=0.5)
        )

        frequency_analysis = FrequencyAnalysis(
            dominant_frequency=self._get_value(v, 'freq_dominant', default=7.83),
            harmonic_content=v.get('freq_harmonics', ""),
            power_spectral_density=self._get_value(v, 'freq_psd', default=0.5),
            resonance_strength=self._get_value(v, 'freq_resonance', default=0.5),
            decoherence_time=self._get_value(v, 'freq_decoherence', default=1.0)
        )

        return Tier5(
            timeline_predictions=timeline_predictions,
            transformation_vectors=transformation_vectors,
            quantum_mechanics=quantum_mechanics,
            frequency_analysis=frequency_analysis
        )

    def _organize_tier6(self, values: Dict[str, Any]) -> Tier6:
        """Organize Tier 6 values (quantum fields)"""
        v = values.get('values', values)

        return Tier6(
            field_charge_density=self._get_value(v, 'field_charge', default=0.5),
            field_current_density=self._get_value(v, 'field_current', default=0.5),
            consciousness_curvature=self._get_value(v, 'consciousness_curvature', default=0.0)
        )
