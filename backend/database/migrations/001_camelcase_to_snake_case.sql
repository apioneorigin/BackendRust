-- Migration: Rename all columns from camelCase to snake_case
-- Run this against your PostgreSQL database

BEGIN;

-- ============================================
-- chat_conversations
-- ============================================
ALTER TABLE chat_conversations RENAME COLUMN "userId" TO user_id;
ALTER TABLE chat_conversations RENAME COLUMN "organizationId" TO organization_id;
ALTER TABLE chat_conversations RENAME COLUMN "sessionId" TO session_id;
ALTER TABLE chat_conversations RENAME COLUMN "isActive" TO is_active;
ALTER TABLE chat_conversations RENAME COLUMN "totalInputTokens" TO total_input_tokens;
ALTER TABLE chat_conversations RENAME COLUMN "totalOutputTokens" TO total_output_tokens;
ALTER TABLE chat_conversations RENAME COLUMN "totalTokens" TO total_tokens;
ALTER TABLE chat_conversations RENAME COLUMN "currentPhase" TO current_phase;
ALTER TABLE chat_conversations RENAME COLUMN "questionAnswers" TO question_answers;
ALTER TABLE chat_conversations RENAME COLUMN "matrixData" TO matrix_data;
ALTER TABLE chat_conversations RENAME COLUMN "generatedPaths" TO generated_paths;
ALTER TABLE chat_conversations RENAME COLUMN "generatedDocuments" TO generated_documents;
ALTER TABLE chat_conversations RENAME COLUMN "createdAt" TO created_at;
ALTER TABLE chat_conversations RENAME COLUMN "updatedAt" TO updated_at;

-- ============================================
-- chat_messages
-- ============================================
ALTER TABLE chat_messages RENAME COLUMN "conversationId" TO conversation_id;
ALTER TABLE chat_messages RENAME COLUMN "cosData" TO cos_data;
ALTER TABLE chat_messages RENAME COLUMN "inputTokens" TO input_tokens;
ALTER TABLE chat_messages RENAME COLUMN "outputTokens" TO output_tokens;
ALTER TABLE chat_messages RENAME COLUMN "totalTokens" TO total_tokens;
ALTER TABLE chat_messages RENAME COLUMN "importanceScore" TO importance_score;
ALTER TABLE chat_messages RENAME COLUMN "isSummarized" TO is_summarized;
ALTER TABLE chat_messages RENAME COLUMN "summaryId" TO summary_id;
ALTER TABLE chat_messages RENAME COLUMN "engagementFlags" TO engagement_flags;
ALTER TABLE chat_messages RENAME COLUMN "createdAt" TO created_at;

-- ============================================
-- chat_summaries
-- ============================================
ALTER TABLE chat_summaries RENAME COLUMN "conversationId" TO conversation_id;
ALTER TABLE chat_summaries RENAME COLUMN "summaryText" TO summary_text;
ALTER TABLE chat_summaries RENAME COLUMN "startMessageId" TO start_message_id;
ALTER TABLE chat_summaries RENAME COLUMN "endMessageId" TO end_message_id;
ALTER TABLE chat_summaries RENAME COLUMN "messageCount" TO message_count;
ALTER TABLE chat_summaries RENAME COLUMN "inputTokens" TO input_tokens;
ALTER TABLE chat_summaries RENAME COLUMN "outputTokens" TO output_tokens;
ALTER TABLE chat_summaries RENAME COLUMN "savedTokens" TO saved_tokens;
ALTER TABLE chat_summaries RENAME COLUMN "summaryPhase" TO summary_phase;
ALTER TABLE chat_summaries RENAME COLUMN "createdAt" TO created_at;

-- ============================================
-- organizations
-- ============================================
ALTER TABLE organizations RENAME COLUMN "subscriptionTier" TO subscription_tier;
ALTER TABLE organizations RENAME COLUMN "subscriptionStatus" TO subscription_status;
ALTER TABLE organizations RENAME COLUMN "stripeCustomerId" TO stripe_customer_id;
ALTER TABLE organizations RENAME COLUMN "stripeSubscriptionId" TO stripe_subscription_id;
ALTER TABLE organizations RENAME COLUMN "stripePriceId" TO stripe_price_id;
ALTER TABLE organizations RENAME COLUMN "trialEndsAt" TO trial_ends_at;
ALTER TABLE organizations RENAME COLUMN "subscriptionEndsAt" TO subscription_ends_at;
ALTER TABLE organizations RENAME COLUMN "billingCycle" TO billing_cycle;
ALTER TABLE organizations RENAME COLUMN "billingPeriodStart" TO billing_period_start;
ALTER TABLE organizations RENAME COLUMN "maxUsers" TO max_users;
ALTER TABLE organizations RENAME COLUMN "maxSessions" TO max_sessions;
ALTER TABLE organizations RENAME COLUMN "maxCreditsPerMonth" TO max_credits_per_month;
ALTER TABLE organizations RENAME COLUMN "usedSessions" TO used_sessions;
ALTER TABLE organizations RENAME COLUMN "usedCredits" TO used_credits;
ALTER TABLE organizations RENAME COLUMN "usageResetAt" TO usage_reset_at;
ALTER TABLE organizations RENAME COLUMN "enabledFeatures" TO enabled_features;
ALTER TABLE organizations RENAME COLUMN "createdAt" TO created_at;
ALTER TABLE organizations RENAME COLUMN "updatedAt" TO updated_at;
ALTER TABLE organizations RENAME COLUMN "deletedAt" TO deleted_at;

-- ============================================
-- users
-- ============================================
ALTER TABLE users RENAME COLUMN "organizationId" TO organization_id;
ALTER TABLE users RENAME COLUMN "passwordHash" TO password_hash;
ALTER TABLE users RENAME COLUMN "creditsEnabled" TO credits_enabled;
ALTER TABLE users RENAME COLUMN "creditQuota" TO credit_quota;
ALTER TABLE users RENAME COLUMN "trialCreditsReceived" TO trial_credits_received;
ALTER TABLE users RENAME COLUMN "trialActivatedAt" TO trial_activated_at;
ALTER TABLE users RENAME COLUMN "createdAt" TO created_at;
ALTER TABLE users RENAME COLUMN "updatedAt" TO updated_at;
ALTER TABLE users RENAME COLUMN "lastLoginAt" TO last_login_at;

-- ============================================
-- user_sessions
-- ============================================
ALTER TABLE user_sessions RENAME COLUMN "userId" TO user_id;
ALTER TABLE user_sessions RENAME COLUMN "expiresAt" TO expires_at;
ALTER TABLE user_sessions RENAME COLUMN "ipAddress" TO ip_address;
ALTER TABLE user_sessions RENAME COLUMN "userAgent" TO user_agent;
ALTER TABLE user_sessions RENAME COLUMN "createdAt" TO created_at;
ALTER TABLE user_sessions RENAME COLUMN "lastActiveAt" TO last_active_at;

-- ============================================
-- invitations
-- ============================================
ALTER TABLE invitations RENAME COLUMN "organizationId" TO organization_id;
ALTER TABLE invitations RENAME COLUMN "invitedBy" TO invited_by;
ALTER TABLE invitations RENAME COLUMN "expiresAt" TO expires_at;
ALTER TABLE invitations RENAME COLUMN "acceptedAt" TO accepted_at;
ALTER TABLE invitations RENAME COLUMN "createdAt" TO created_at;

-- ============================================
-- user_patterns
-- ============================================
ALTER TABLE user_patterns RENAME COLUMN "userId" TO user_id;
ALTER TABLE user_patterns RENAME COLUMN "decisionSpeed" TO decision_speed;
ALTER TABLE user_patterns RENAME COLUMN "riskTolerance" TO risk_tolerance;
ALTER TABLE user_patterns RENAME COLUMN "detailOrientation" TO detail_orientation;
ALTER TABLE user_patterns RENAME COLUMN "sessionCount" TO session_count;
ALTER TABLE user_patterns RENAME COLUMN "totalInteractions" TO total_interactions;
ALTER TABLE user_patterns RENAME COLUMN "createdAt" TO created_at;
ALTER TABLE user_patterns RENAME COLUMN "updatedAt" TO updated_at;

-- ============================================
-- user_interactions
-- ============================================
ALTER TABLE user_interactions RENAME COLUMN "userId" TO user_id;
ALTER TABLE user_interactions RENAME COLUMN "sessionId" TO session_id;
ALTER TABLE user_interactions RENAME COLUMN "interactionData" TO interaction_data;

-- ============================================
-- sessions
-- ============================================
ALTER TABLE sessions RENAME COLUMN "organizationId" TO organization_id;
ALTER TABLE sessions RENAME COLUMN "userId" TO user_id;
ALTER TABLE sessions RENAME COLUMN "currentScreen" TO current_screen;
ALTER TABLE sessions RENAME COLUMN "discoverData" TO discover_data;
ALTER TABLE sessions RENAME COLUMN "stage1Data" TO stage1_data;
ALTER TABLE sessions RENAME COLUMN "stage2Data" TO stage2_data;
ALTER TABLE sessions RENAME COLUMN "stage3Data" TO stage3_data;
ALTER TABLE sessions RENAME COLUMN "dashboardData" TO dashboard_data;
ALTER TABLE sessions RENAME COLUMN "decodeData" TO decode_data;
ALTER TABLE sessions RENAME COLUMN "designData" TO design_data;
ALTER TABLE sessions RENAME COLUMN "goalText" TO goal_text;
ALTER TABLE sessions RENAME COLUMN "goalData" TO goal_data;
ALTER TABLE sessions RENAME COLUMN "goalExtractedAt" TO goal_extracted_at;
ALTER TABLE sessions RENAME COLUMN "law3DiscardRate" TO law3_discard_rate;
ALTER TABLE sessions RENAME COLUMN "law3DiscardedCount" TO law3_discarded_count;
ALTER TABLE sessions RENAME COLUMN "law3ProcessedCount" TO law3_processed_count;
ALTER TABLE sessions RENAME COLUMN "draftGoalText" TO draft_goal_text;
ALTER TABLE sessions RENAME COLUMN "workflowContext" TO workflow_context;
ALTER TABLE sessions RENAME COLUMN "isRestartFlow" TO is_restart_flow;
ALTER TABLE sessions RENAME COLUMN "isNewGoalFlow" TO is_new_goal_flow;
ALTER TABLE sessions RENAME COLUMN "profileSnapshot" TO profile_snapshot;
ALTER TABLE sessions RENAME COLUMN "predictedChallenges" TO predicted_challenges;
ALTER TABLE sessions RENAME COLUMN "actualChallenges" TO actual_challenges;
ALTER TABLE sessions RENAME COLUMN "predictionAccuracy" TO prediction_accuracy;
ALTER TABLE sessions RENAME COLUMN "lastConversationId" TO last_conversation_id;
ALTER TABLE sessions RENAME COLUMN "createdAt" TO created_at;
ALTER TABLE sessions RENAME COLUMN "updatedAt" TO updated_at;
ALTER TABLE sessions RENAME COLUMN "lastAccessedAt" TO last_accessed_at;
ALTER TABLE sessions RENAME COLUMN "lastAccessedBy" TO last_accessed_by;
ALTER TABLE sessions RENAME COLUMN "completedAt" TO completed_at;

-- ============================================
-- interactions
-- ============================================
ALTER TABLE interactions RENAME COLUMN "sessionId" TO session_id;
ALTER TABLE interactions RENAME COLUMN "questionNumber" TO question_number;
ALTER TABLE interactions RENAME COLUMN "userMessage" TO user_message;
ALTER TABLE interactions RENAME COLUMN "assistantResponse" TO assistant_response;
ALTER TABLE interactions RENAME COLUMN "tokensUsed" TO tokens_used;
ALTER TABLE interactions RENAME COLUMN "createdAt" TO created_at;

-- ============================================
-- insights
-- ============================================
ALTER TABLE insights RENAME COLUMN "sessionId" TO session_id;
ALTER TABLE insights RENAME COLUMN "createdAt" TO created_at;

-- ============================================
-- insight_generations
-- ============================================
ALTER TABLE insight_generations RENAME COLUMN "organizationId" TO organization_id;
ALTER TABLE insight_generations RENAME COLUMN "sessionId" TO session_id;
ALTER TABLE insight_generations RENAME COLUMN "userId" TO user_id;
ALTER TABLE insight_generations RENAME COLUMN "goalText" TO goal_text;
ALTER TABLE insight_generations RENAME COLUMN "totalGenerated" TO total_generated;
ALTER TABLE insight_generations RENAME COLUMN "averageGoalContribution" TO average_goal_contribution;
ALTER TABLE insight_generations RENAME COLUMN "createdAt" TO created_at;

-- ============================================
-- audit_logs
-- ============================================
ALTER TABLE audit_logs RENAME COLUMN "sessionId" TO session_id;
ALTER TABLE audit_logs RENAME COLUMN "statusCode" TO status_code;
ALTER TABLE audit_logs RENAME COLUMN "errorMessage" TO error_message;
ALTER TABLE audit_logs RENAME COLUMN "ipAddress" TO ip_address;
ALTER TABLE audit_logs RENAME COLUMN "userAgent" TO user_agent;
ALTER TABLE audit_logs RENAME COLUMN "tokensUsed" TO tokens_used;
ALTER TABLE audit_logs RENAME COLUMN "requestBody" TO request_body;
ALTER TABLE audit_logs RENAME COLUMN "requestHeaders" TO request_headers;
ALTER TABLE audit_logs RENAME COLUMN "responseBody" TO response_body;
ALTER TABLE audit_logs RENAME COLUMN "createdAt" TO created_at;

-- ============================================
-- operator_calculations
-- ============================================
ALTER TABLE operator_calculations RENAME COLUMN "organizationId" TO organization_id;
ALTER TABLE operator_calculations RENAME COLUMN "sessionId" TO session_id;
ALTER TABLE operator_calculations RENAME COLUMN "userId" TO user_id;
ALTER TABLE operator_calculations RENAME COLUMN "sophisticationLevel" TO sophistication_level;
ALTER TABLE operator_calculations RENAME COLUMN "derivedMetrics" TO derived_metrics;
ALTER TABLE operator_calculations RENAME COLUMN "createdAt" TO created_at;

-- ============================================
-- matrix_populations
-- ============================================
ALTER TABLE matrix_populations RENAME COLUMN "organizationId" TO organization_id;
ALTER TABLE matrix_populations RENAME COLUMN "sessionId" TO session_id;
ALTER TABLE matrix_populations RENAME COLUMN "userId" TO user_id;
ALTER TABLE matrix_populations RENAME COLUMN "structuralCoherence" TO structural_coherence;
ALTER TABLE matrix_populations RENAME COLUMN "createdAt" TO created_at;

-- ============================================
-- usage_records
-- ============================================
ALTER TABLE usage_records RENAME COLUMN "organizationId" TO organization_id;
ALTER TABLE usage_records RENAME COLUMN "userId" TO user_id;
ALTER TABLE usage_records RENAME COLUMN "sessionId" TO session_id;
ALTER TABLE usage_records RENAME COLUMN "usageType" TO usage_type;
ALTER TABLE usage_records RENAME COLUMN "usageMetadata" TO usage_metadata;
ALTER TABLE usage_records RENAME COLUMN "createdAt" TO created_at;

-- ============================================
-- claude_api_logs
-- ============================================
ALTER TABLE claude_api_logs RENAME COLUMN "taskType" TO task_type;
ALTER TABLE claude_api_logs RENAME COLUMN "goalId" TO goal_id;
ALTER TABLE claude_api_logs RENAME COLUMN "userId" TO user_id;
ALTER TABLE claude_api_logs RENAME COLUMN "sessionId" TO session_id;
ALTER TABLE claude_api_logs RENAME COLUMN "organizationId" TO organization_id;
ALTER TABLE claude_api_logs RENAME COLUMN "promptTokens" TO prompt_tokens;
ALTER TABLE claude_api_logs RENAME COLUMN "completionTokens" TO completion_tokens;
ALTER TABLE claude_api_logs RENAME COLUMN "totalTokens" TO total_tokens;
ALTER TABLE claude_api_logs RENAME COLUMN "estimatedCost" TO estimated_cost;
ALTER TABLE claude_api_logs RENAME COLUMN "durationMs" TO duration_ms;
ALTER TABLE claude_api_logs RENAME COLUMN "errorMessage" TO error_message;
ALTER TABLE claude_api_logs RENAME COLUMN "frameworkVersion" TO framework_version;
ALTER TABLE claude_api_logs RENAME COLUMN "frameworkFiles" TO framework_files;
ALTER TABLE claude_api_logs RENAME COLUMN "coherenceScore" TO coherence_score;
ALTER TABLE claude_api_logs RENAME COLUMN "responseQuality" TO response_quality;
ALTER TABLE claude_api_logs RENAME COLUMN "hasErrors" TO has_errors;
ALTER TABLE claude_api_logs RENAME COLUMN "frameworkCompliance" TO framework_compliance;
ALTER TABLE claude_api_logs RENAME COLUMN "requestBody" TO request_body;
ALTER TABLE claude_api_logs RENAME COLUMN "responseBody" TO response_body;
ALTER TABLE claude_api_logs RENAME COLUMN "createdAt" TO created_at;

-- ============================================
-- ai_assist_messages
-- ============================================
ALTER TABLE ai_assist_messages RENAME COLUMN "sessionId" TO session_id;
ALTER TABLE ai_assist_messages RENAME COLUMN "messageType" TO message_type;
ALTER TABLE ai_assist_messages RENAME COLUMN "wasHelpful" TO was_helpful;

-- ============================================
-- oof_cos_analytics
-- ============================================
ALTER TABLE oof_cos_analytics RENAME COLUMN "userId" TO user_id;
ALTER TABLE oof_cos_analytics RENAME COLUMN "sessionId" TO session_id;
ALTER TABLE oof_cos_analytics RENAME COLUMN "organizationId" TO organization_id;
ALTER TABLE oof_cos_analytics RENAME COLUMN "cognitiveMode" TO cognitive_mode;
ALTER TABLE oof_cos_analytics RENAME COLUMN "confusionBeforeClarity" TO confusion_before_clarity;
ALTER TABLE oof_cos_analytics RENAME COLUMN "coreSevenActivated" TO core_seven_activated;
ALTER TABLE oof_cos_analytics RENAME COLUMN "coreSevenComplete" TO core_seven_complete;
ALTER TABLE oof_cos_analytics RENAME COLUMN "operatorCoverage" TO operator_coverage;
ALTER TABLE oof_cos_analytics RENAME COLUMN "dominantOperator" TO dominant_operator;
ALTER TABLE oof_cos_analytics RENAME COLUMN "estimatedSLevel" TO estimated_s_level;
ALTER TABLE oof_cos_analytics RENAME COLUMN "discoveryFeel" TO discovery_feel;
ALTER TABLE oof_cos_analytics RENAME COLUMN "frameworkFeel" TO framework_feel;
ALTER TABLE oof_cos_analytics RENAME COLUMN "concealmentVerified" TO concealment_verified;
ALTER TABLE oof_cos_analytics RENAME COLUMN "frameworkTermsFound" TO framework_terms_found;
ALTER TABLE oof_cos_analytics RENAME COLUMN "overallQualityScore" TO overall_quality_score;
ALTER TABLE oof_cos_analytics RENAME COLUMN "validationPassed" TO validation_passed;
ALTER TABLE oof_cos_analytics RENAME COLUMN "criticalIssues" TO critical_issues;
ALTER TABLE oof_cos_analytics RENAME COLUMN "warningIssues" TO warning_issues;
ALTER TABLE oof_cos_analytics RENAME COLUMN "createdAt" TO created_at;

-- ============================================
-- interaction_psychology
-- ============================================
ALTER TABLE interaction_psychology RENAME COLUMN "userId" TO user_id;
ALTER TABLE interaction_psychology RENAME COLUMN "sessionId" TO session_id;
ALTER TABLE interaction_psychology RENAME COLUMN "organizationId" TO organization_id;
ALTER TABLE interaction_psychology RENAME COLUMN "turnNumber" TO turn_number;
ALTER TABLE interaction_psychology RENAME COLUMN "claimedTopics" TO claimed_topics;
ALTER TABLE interaction_psychology RENAME COLUMN "shouldCount" TO should_count;
ALTER TABLE interaction_psychology RENAME COLUMN "wantCount" TO want_count;
ALTER TABLE interaction_psychology RENAME COLUMN "needCount" TO need_count;
ALTER TABLE interaction_psychology RENAME COLUMN "qualifierCount" TO qualifier_count;
ALTER TABLE interaction_psychology RENAME COLUMN "firstPersonCount" TO first_person_count;
ALTER TABLE interaction_psychology RENAME COLUMN "distancingCount" TO distancing_count;
ALTER TABLE interaction_psychology RENAME COLUMN "futureCommitment" TO future_commitment;
ALTER TABLE interaction_psychology RENAME COLUMN "messageLength" TO message_length;
ALTER TABLE interaction_psychology RENAME COLUMN "responseLatency" TO response_latency;
ALTER TABLE interaction_psychology RENAME COLUMN "contentCategories" TO content_categories;
ALTER TABLE interaction_psychology RENAME COLUMN "primaryCategory" TO primary_category;
ALTER TABLE interaction_psychology RENAME COLUMN "contentDepth" TO content_depth;
ALTER TABLE interaction_psychology RENAME COLUMN "shadowProximity" TO shadow_proximity;
ALTER TABLE interaction_psychology RENAME COLUMN "intensityLevel" TO intensity_level;
ALTER TABLE interaction_psychology RENAME COLUMN "goalsPresented" TO goals_presented;
ALTER TABLE interaction_psychology RENAME COLUMN "insightsPresented" TO insights_presented;
ALTER TABLE interaction_psychology RENAME COLUMN "questionsPresented" TO questions_presented;
ALTER TABLE interaction_psychology RENAME COLUMN "createdAt" TO created_at;

-- ============================================
-- element_actions
-- ============================================
ALTER TABLE element_actions RENAME COLUMN "userId" TO user_id;
ALTER TABLE element_actions RENAME COLUMN "sessionId" TO session_id;
ALTER TABLE element_actions RENAME COLUMN "organizationId" TO organization_id;
ALTER TABLE element_actions RENAME COLUMN "elementType" TO element_type;
ALTER TABLE element_actions RENAME COLUMN "elementId" TO element_id;
ALTER TABLE element_actions RENAME COLUMN "elementCategories" TO element_categories;
ALTER TABLE element_actions RENAME COLUMN "elementDepth" TO element_depth;
ALTER TABLE element_actions RENAME COLUMN "elementShadowProximity" TO element_shadow_proximity;
ALTER TABLE element_actions RENAME COLUMN "timeToAction" TO time_to_action;
ALTER TABLE element_actions RENAME COLUMN "optionChosen" TO option_chosen;
ALTER TABLE element_actions RENAME COLUMN "optionPosition" TO option_position;
ALTER TABLE element_actions RENAME COLUMN "createdAt" TO created_at;

-- ============================================
-- session_psychology
-- ============================================
ALTER TABLE session_psychology RENAME COLUMN "userId" TO user_id;
ALTER TABLE session_psychology RENAME COLUMN "sessionId" TO session_id;
ALTER TABLE session_psychology RENAME COLUMN "organizationId" TO organization_id;
ALTER TABLE session_psychology RENAME COLUMN "sessionStart" TO session_start;
ALTER TABLE session_psychology RENAME COLUMN "sessionEnd" TO session_end;
ALTER TABLE session_psychology RENAME COLUMN "durationMs" TO duration_ms;
ALTER TABLE session_psychology RENAME COLUMN "turnCount" TO turn_count;
ALTER TABLE session_psychology RENAME COLUMN "depthProgression" TO depth_progression;
ALTER TABLE session_psychology RENAME COLUMN "maxDepthReached" TO max_depth_reached;
ALTER TABLE session_psychology RENAME COLUMN "categoriesEngaged" TO categories_engaged;
ALTER TABLE session_psychology RENAME COLUMN "categoriesAvoided" TO categories_avoided;
ALTER TABLE session_psychology RENAME COLUMN "categoriesPresented" TO categories_presented;
ALTER TABLE session_psychology RENAME COLUMN "exitTrigger" TO exit_trigger;
ALTER TABLE session_psychology RENAME COLUMN "lastContentCategories" TO last_content_categories;
ALTER TABLE session_psychology RENAME COLUMN "lastContentDepth" TO last_content_depth;
ALTER TABLE session_psychology RENAME COLUMN "lastShadowProximity" TO last_shadow_proximity;
ALTER TABLE session_psychology RENAME COLUMN "lastIntensityLevel" TO last_intensity_level;
ALTER TABLE session_psychology RENAME COLUMN "avgShadowProximity" TO avg_shadow_proximity;
ALTER TABLE session_psychology RENAME COLUMN "avgIntensityLevel" TO avg_intensity_level;
ALTER TABLE session_psychology RENAME COLUMN "totalSkips" TO total_skips;
ALTER TABLE session_psychology RENAME COLUMN "totalEngagements" TO total_engagements;
ALTER TABLE session_psychology RENAME COLUMN "createdAt" TO created_at;
ALTER TABLE session_psychology RENAME COLUMN "updatedAt" TO updated_at;

-- ============================================
-- user_psychology_profiles
-- ============================================
ALTER TABLE user_psychology_profiles RENAME COLUMN "userId" TO user_id;
ALTER TABLE user_psychology_profiles RENAME COLUMN "organizationId" TO organization_id;
ALTER TABLE user_psychology_profiles RENAME COLUMN "sayDoGaps" TO say_do_gaps;
ALTER TABLE user_psychology_profiles RENAME COLUMN "overallSayDoGap" TO overall_say_do_gap;
ALTER TABLE user_psychology_profiles RENAME COLUMN "avoidanceScores" TO avoidance_scores;
ALTER TABLE user_psychology_profiles RENAME COLUMN "primaryAvoidanceCategory" TO primary_avoidance_category;
ALTER TABLE user_psychology_profiles RENAME COLUMN "overallAvoidanceScore" TO overall_avoidance_score;
ALTER TABLE user_psychology_profiles RENAME COLUMN "ratingAuthenticityType" TO rating_authenticity_type;
ALTER TABLE user_psychology_profiles RENAME COLUMN "ratingVariance" TO rating_variance;
ALTER TABLE user_psychology_profiles RENAME COLUMN "ratingMean" TO rating_mean;
ALTER TABLE user_psychology_profiles RENAME COLUMN "shadowRatingDifferential" TO shadow_rating_differential;
ALTER TABLE user_psychology_profiles RENAME COLUMN "totalRatings" TO total_ratings;
ALTER TABLE user_psychology_profiles RENAME COLUMN "depthTrajectory" TO depth_trajectory;
ALTER TABLE user_psychology_profiles RENAME COLUMN "depthTolerance" TO depth_tolerance;
ALTER TABLE user_psychology_profiles RENAME COLUMN "maxDepthReached" TO max_depth_reached;
ALTER TABLE user_psychology_profiles RENAME COLUMN "depthProgressionSpeed" TO depth_progression_speed;
ALTER TABLE user_psychology_profiles RENAME COLUMN "externalAuthorityScore" TO external_authority_score;
ALTER TABLE user_psychology_profiles RENAME COLUMN "selfPermissionScore" TO self_permission_score;
ALTER TABLE user_psychology_profiles RENAME COLUMN "qualifierDensity" TO qualifier_density;
ALTER TABLE user_psychology_profiles RENAME COLUMN "ownershipRatio" TO ownership_ratio;
ALTER TABLE user_psychology_profiles RENAME COLUMN "commitmentStrength" TO commitment_strength;
ALTER TABLE user_psychology_profiles RENAME COLUMN "psychologicalSegment" TO psychological_segment;
ALTER TABLE user_psychology_profiles RENAME COLUMN "segmentConfidence" TO segment_confidence;
ALTER TABLE user_psychology_profiles RENAME COLUMN "previousSegment" TO previous_segment;
ALTER TABLE user_psychology_profiles RENAME COLUMN "segmentStability" TO segment_stability;
ALTER TABLE user_psychology_profiles RENAME COLUMN "primaryDefense" TO primary_defense;
ALTER TABLE user_psychology_profiles RENAME COLUMN "defenseProfile" TO defense_profile;
ALTER TABLE user_psychology_profiles RENAME COLUMN "defenseTriggerShadowThreshold" TO defense_trigger_shadow_threshold;
ALTER TABLE user_psychology_profiles RENAME COLUMN "goalConflictCount" TO goal_conflict_count;
ALTER TABLE user_psychology_profiles RENAME COLUMN "commitmentFollowThrough" TO commitment_follow_through;
ALTER TABLE user_psychology_profiles RENAME COLUMN "ratingBehaviorMismatch" TO rating_behavior_mismatch;
ALTER TABLE user_psychology_profiles RENAME COLUMN "overallContradictionIndex" TO overall_contradiction_index;
ALTER TABLE user_psychology_profiles RENAME COLUMN "churnRisk" TO churn_risk;
ALTER TABLE user_psychology_profiles RENAME COLUMN "churnRiskFactors" TO churn_risk_factors;
ALTER TABLE user_psychology_profiles RENAME COLUMN "upgradeLikelihood" TO upgrade_likelihood;
ALTER TABLE user_psychology_profiles RENAME COLUMN "upgradeFactors" TO upgrade_factors;
ALTER TABLE user_psychology_profiles RENAME COLUMN "totalSessions" TO total_sessions;
ALTER TABLE user_psychology_profiles RENAME COLUMN "avgSessionDuration" TO avg_session_duration;
ALTER TABLE user_psychology_profiles RENAME COLUMN "avgGapBetweenSessions" TO avg_gap_between_sessions;
ALTER TABLE user_psychology_profiles RENAME COLUMN "sessionFrequencyTrend" TO session_frequency_trend;
ALTER TABLE user_psychology_profiles RENAME COLUMN "lastSessionAt" TO last_session_at;
ALTER TABLE user_psychology_profiles RENAME COLUMN "exitAfterShadowRate" TO exit_after_shadow_rate;
ALTER TABLE user_psychology_profiles RENAME COLUMN "exitAfterIntensityRate" TO exit_after_intensity_rate;
ALTER TABLE user_psychology_profiles RENAME COLUMN "avgReturnGapAfterShadow" TO avg_return_gap_after_shadow;
ALTER TABLE user_psychology_profiles RENAME COLUMN "lastCalculated" TO last_calculated;
ALTER TABLE user_psychology_profiles RENAME COLUMN "createdAt" TO created_at;
ALTER TABLE user_psychology_profiles RENAME COLUMN "updatedAt" TO updated_at;

-- ============================================
-- psychology_population_metrics
-- ============================================
ALTER TABLE psychology_population_metrics RENAME COLUMN "organizationId" TO organization_id;
ALTER TABLE psychology_population_metrics RENAME COLUMN "periodType" TO period_type;
ALTER TABLE psychology_population_metrics RENAME COLUMN "periodStart" TO period_start;
ALTER TABLE psychology_population_metrics RENAME COLUMN "periodEnd" TO period_end;
ALTER TABLE psychology_population_metrics RENAME COLUMN "totalUsers" TO total_users;
ALTER TABLE psychology_population_metrics RENAME COLUMN "activeUsers" TO active_users;
ALTER TABLE psychology_population_metrics RENAME COLUMN "achieverCount" TO achiever_count;
ALTER TABLE psychology_population_metrics RENAME COLUMN "seekerCount" TO seeker_count;
ALTER TABLE psychology_population_metrics RENAME COLUMN "validatorCount" TO validator_count;
ALTER TABLE psychology_population_metrics RENAME COLUMN "resisterCount" TO resister_count;
ALTER TABLE psychology_population_metrics RENAME COLUMN "integratorCount" TO integrator_count;
ALTER TABLE psychology_population_metrics RENAME COLUMN "unknownCount" TO unknown_count;
ALTER TABLE psychology_population_metrics RENAME COLUMN "categoryAvoidanceRates" TO category_avoidance_rates;
ALTER TABLE psychology_population_metrics RENAME COLUMN "categorySayDoGaps" TO category_say_do_gaps;
ALTER TABLE psychology_population_metrics RENAME COLUMN "categoryEngagementRates" TO category_engagement_rates;
ALTER TABLE psychology_population_metrics RENAME COLUMN "peoplePleaserCount" TO people_pleaser_count;
ALTER TABLE psychology_population_metrics RENAME COLUMN "resisterRatingCount" TO resister_rating_count;
ALTER TABLE psychology_population_metrics RENAME COLUMN "disengagedCount" TO disengaged_count;
ALTER TABLE psychology_population_metrics RENAME COLUMN "authenticCount" TO authentic_count;
ALTER TABLE psychology_population_metrics RENAME COLUMN "shadowDefensiveCount" TO shadow_defensive_count;
ALTER TABLE psychology_population_metrics RENAME COLUMN "ascendingCount" TO ascending_count;
ALTER TABLE psychology_population_metrics RENAME COLUMN "descendingCount" TO descending_count;
ALTER TABLE psychology_population_metrics RENAME COLUMN "oscillatingCount" TO oscillating_count;
ALTER TABLE psychology_population_metrics RENAME COLUMN "stuckCount" TO stuck_count;
ALTER TABLE psychology_population_metrics RENAME COLUMN "avgDepthTolerance" TO avg_depth_tolerance;
ALTER TABLE psychology_population_metrics RENAME COLUMN "avgExternalAuthority" TO avg_external_authority;
ALTER TABLE psychology_population_metrics RENAME COLUMN "avgSelfPermission" TO avg_self_permission;
ALTER TABLE psychology_population_metrics RENAME COLUMN "avgQualifierDensity" TO avg_qualifier_density;
ALTER TABLE psychology_population_metrics RENAME COLUMN "avgOwnershipRatio" TO avg_ownership_ratio;
ALTER TABLE psychology_population_metrics RENAME COLUMN "avgExitAfterShadow" TO avg_exit_after_shadow;
ALTER TABLE psychology_population_metrics RENAME COLUMN "avgExitAfterIntensity" TO avg_exit_after_intensity;
ALTER TABLE psychology_population_metrics RENAME COLUMN "avgSessionDuration" TO avg_session_duration;
ALTER TABLE psychology_population_metrics RENAME COLUMN "avgChurnRisk" TO avg_churn_risk;
ALTER TABLE psychology_population_metrics RENAME COLUMN "highChurnRiskCount" TO high_churn_risk_count;
ALTER TABLE psychology_population_metrics RENAME COLUMN "avgUpgradeLikelihood" TO avg_upgrade_likelihood;
ALTER TABLE psychology_population_metrics RENAME COLUMN "highUpgradeCount" TO high_upgrade_count;
ALTER TABLE psychology_population_metrics RENAME COLUMN "psychologyEngagementCorrelations" TO psychology_engagement_correlations;
ALTER TABLE psychology_population_metrics RENAME COLUMN "createdAt" TO created_at;

-- ============================================
-- user_intelligences
-- ============================================
ALTER TABLE user_intelligences RENAME COLUMN "userId" TO user_id;
ALTER TABLE user_intelligences RENAME COLUMN "organizationId" TO organization_id;
ALTER TABLE user_intelligences RENAME COLUMN "metricTrends" TO metric_trends;
ALTER TABLE user_intelligences RENAME COLUMN "actionPatterns" TO action_patterns;
ALTER TABLE user_intelligences RENAME COLUMN "progressVelocity" TO progress_velocity;
ALTER TABLE user_intelligences RENAME COLUMN "milestoneCount" TO milestone_count;
ALTER TABLE user_intelligences RENAME COLUMN "avgSessionDurationMin" TO avg_session_duration_min;
ALTER TABLE user_intelligences RENAME COLUMN "likelyBlockers" TO likely_blockers;
ALTER TABLE user_intelligences RENAME COLUMN "milestoneProbability" TO milestone_probability;
ALTER TABLE user_intelligences RENAME COLUMN "recommendedActions" TO recommended_actions;
ALTER TABLE user_intelligences RENAME COLUMN "primaryArchetype" TO primary_archetype;
ALTER TABLE user_intelligences RENAME COLUMN "archetypeStability" TO archetype_stability;
ALTER TABLE user_intelligences RENAME COLUMN "archetypeEvolution" TO archetype_evolution;
ALTER TABLE user_intelligences RENAME COLUMN "goalsCompleted" TO goals_completed;
ALTER TABLE user_intelligences RENAME COLUMN "goalsAbandoned" TO goals_abandoned;
ALTER TABLE user_intelligences RENAME COLUMN "avgGoalDurationDays" TO avg_goal_duration_days;
ALTER TABLE user_intelligences RENAME COLUMN "goalAchievementPatterns" TO goal_achievement_patterns;
ALTER TABLE user_intelligences RENAME COLUMN "sessionsAnalyzed" TO sessions_analyzed;
ALTER TABLE user_intelligences RENAME COLUMN "firstSessionDate" TO first_session_date;
ALTER TABLE user_intelligences RENAME COLUMN "lastSessionDate" TO last_session_date;
ALTER TABLE user_intelligences RENAME COLUMN "confidenceLevel" TO confidence_level;
ALTER TABLE user_intelligences RENAME COLUMN "createdAt" TO created_at;
ALTER TABLE user_intelligences RENAME COLUMN "updatedAt" TO updated_at;

-- ============================================
-- operator_time_series
-- ============================================
ALTER TABLE operator_time_series RENAME COLUMN "userId" TO user_id;
ALTER TABLE operator_time_series RENAME COLUMN "sessionId" TO session_id;
ALTER TABLE operator_time_series RENAME COLUMN "metricName" TO metric_name;
ALTER TABLE operator_time_series RENAME COLUMN "measurementType" TO measurement_type;
ALTER TABLE operator_time_series RENAME COLUMN "createdAt" TO created_at;

-- ============================================
-- behavior_patterns
-- ============================================
ALTER TABLE behavior_patterns RENAME COLUMN "userId" TO user_id;
ALTER TABLE behavior_patterns RENAME COLUMN "patternType" TO pattern_type;
ALTER TABLE behavior_patterns RENAME COLUMN "firstDetected" TO first_detected;
ALTER TABLE behavior_patterns RENAME COLUMN "lastDetected" TO last_detected;
ALTER TABLE behavior_patterns RENAME COLUMN "createdAt" TO created_at;
ALTER TABLE behavior_patterns RENAME COLUMN "updatedAt" TO updated_at;

-- ============================================
-- global_patterns
-- ============================================
ALTER TABLE global_patterns RENAME COLUMN "organizationId" TO organization_id;
ALTER TABLE global_patterns RENAME COLUMN "patternCategory" TO pattern_category;
ALTER TABLE global_patterns RENAME COLUMN "patternData" TO pattern_data;
ALTER TABLE global_patterns RENAME COLUMN "sampleSize" TO sample_size;
ALTER TABLE global_patterns RENAME COLUMN "confidenceLevel" TO confidence_level;
ALTER TABLE global_patterns RENAME COLUMN "lastUpdated" TO last_updated;
ALTER TABLE global_patterns RENAME COLUMN "createdAt" TO created_at;

-- ============================================
-- archetype_insights
-- ============================================
ALTER TABLE archetype_insights RENAME COLUMN "archetypeName" TO archetype_name;
ALTER TABLE archetype_insights RENAME COLUMN "successPatterns" TO success_patterns;
ALTER TABLE archetype_insights RENAME COLUMN "commonBlockers" TO common_blockers;
ALTER TABLE archetype_insights RENAME COLUMN "optimalInterventions" TO optimal_interventions;
ALTER TABLE archetype_insights RENAME COLUMN "keyOperators" TO key_operators;
ALTER TABLE archetype_insights RENAME COLUMN "transformationVelocityAvg" TO transformation_velocity_avg;
ALTER TABLE archetype_insights RENAME COLUMN "sampleSize" TO sample_size;
ALTER TABLE archetype_insights RENAME COLUMN "confidenceLevel" TO confidence_level;
ALTER TABLE archetype_insights RENAME COLUMN "createdAt" TO created_at;
ALTER TABLE archetype_insights RENAME COLUMN "updatedAt" TO updated_at;

-- ============================================
-- goals
-- ============================================
ALTER TABLE goals RENAME COLUMN "userId" TO user_id;
ALTER TABLE goals RENAME COLUMN "organizationId" TO organization_id;
ALTER TABLE goals RENAME COLUMN "goalText" TO goal_text;
ALTER TABLE goals RENAME COLUMN "sessionId" TO session_id;
ALTER TABLE goals RENAME COLUMN "lockedAt" TO locked_at;
ALTER TABLE goals RENAME COLUMN "metricTargets" TO metric_targets;
ALTER TABLE goals RENAME COLUMN "metricTargetsCalculatedBy" TO metric_targets_calculated_by;
ALTER TABLE goals RENAME COLUMN "metricTargetsCalculatedAt" TO metric_targets_calculated_at;
ALTER TABLE goals RENAME COLUMN "matrixRows" TO matrix_rows;
ALTER TABLE goals RENAME COLUMN "matrixColumns" TO matrix_columns;
ALTER TABLE goals RENAME COLUMN "matrixGeneration" TO matrix_generation;
ALTER TABLE goals RENAME COLUMN "successCriteria" TO success_criteria;
ALTER TABLE goals RENAME COLUMN "createdAt" TO created_at;
ALTER TABLE goals RENAME COLUMN "updatedAt" TO updated_at;

-- ============================================
-- matrix_values
-- ============================================
ALTER TABLE matrix_values RENAME COLUMN "userId" TO user_id;
ALTER TABLE matrix_values RENAME COLUMN "organizationId" TO organization_id;
ALTER TABLE matrix_values RENAME COLUMN "sessionId" TO session_id;
ALTER TABLE matrix_values RENAME COLUMN "goalId" TO goal_id;
ALTER TABLE matrix_values RENAME COLUMN "cellRow" TO cell_row;
ALTER TABLE matrix_values RENAME COLUMN "cellColumn" TO cell_column;
ALTER TABLE matrix_values RENAME COLUMN "dimensionName" TO dimension_name;
ALTER TABLE matrix_values RENAME COLUMN "dimensionIndex" TO dimension_index;
ALTER TABLE matrix_values RENAME COLUMN "valueId" TO value_id;
ALTER TABLE matrix_values RENAME COLUMN "currentValue" TO current_value;
ALTER TABLE matrix_values RENAME COLUMN "targetValue" TO target_value;
ALTER TABLE matrix_values RENAME COLUMN "questionnaireValue" TO questionnaire_value;
ALTER TABLE matrix_values RENAME COLUMN "fileDataValue" TO file_data_value;
ALTER TABLE matrix_values RENAME COLUMN "userActionValue" TO user_action_value;
ALTER TABLE matrix_values RENAME COLUMN "goalContextValue" TO goal_context_value;
ALTER TABLE matrix_values RENAME COLUMN "lastUpdatedSession" TO last_updated_session;
ALTER TABLE matrix_values RENAME COLUMN "createdAt" TO created_at;
ALTER TABLE matrix_values RENAME COLUMN "updatedAt" TO updated_at;

-- ============================================
-- gap_topologies
-- ============================================
ALTER TABLE gap_topologies RENAME COLUMN "userId" TO user_id;
ALTER TABLE gap_topologies RENAME COLUMN "organizationId" TO organization_id;
ALTER TABLE gap_topologies RENAME COLUMN "goalId" TO goal_id;
ALTER TABLE gap_topologies RENAME COLUMN "valueId" TO value_id;
ALTER TABLE gap_topologies RENAME COLUMN "masterLineValue" TO master_line_value;
ALTER TABLE gap_topologies RENAME COLUMN "unlocksCount" TO unlocks_count;
ALTER TABLE gap_topologies RENAME COLUMN "blocksCount" TO blocks_count;
ALTER TABLE gap_topologies RENAME COLUMN "dependsOn" TO depends_on;
ALTER TABLE gap_topologies RENAME COLUMN "criticalPathRank" TO critical_path_rank;
ALTER TABLE gap_topologies RENAME COLUMN "mustCloseBySession" TO must_close_by_session;
ALTER TABLE gap_topologies RENAME COLUMN "branchExploration" TO branch_exploration;
ALTER TABLE gap_topologies RENAME COLUMN "openedInSession" TO opened_in_session;
ALTER TABLE gap_topologies RENAME COLUMN "closedInSession" TO closed_in_session;
ALTER TABLE gap_topologies RENAME COLUMN "branchReason" TO branch_reason;
ALTER TABLE gap_topologies RENAME COLUMN "branchAcceptable" TO branch_acceptable;
ALTER TABLE gap_topologies RENAME COLUMN "autoImprovesWhen" TO auto_improves_when;
ALTER TABLE gap_topologies RENAME COLUMN "improvementMechanism" TO improvement_mechanism;
ALTER TABLE gap_topologies RENAME COLUMN "expectedImprovement" TO expected_improvement;
ALTER TABLE gap_topologies RENAME COLUMN "createdAt" TO created_at;
ALTER TABLE gap_topologies RENAME COLUMN "updatedAt" TO updated_at;

-- ============================================
-- coherence_snapshots
-- ============================================
ALTER TABLE coherence_snapshots RENAME COLUMN "userId" TO user_id;
ALTER TABLE coherence_snapshots RENAME COLUMN "organizationId" TO organization_id;
ALTER TABLE coherence_snapshots RENAME COLUMN "sessionId" TO session_id;
ALTER TABLE coherence_snapshots RENAME COLUMN "goalId" TO goal_id;
ALTER TABLE coherence_snapshots RENAME COLUMN "overallCoherence" TO overall_coherence;
ALTER TABLE coherence_snapshots RENAME COLUMN "masterLineCoherence" TO master_line_coherence;
ALTER TABLE coherence_snapshots RENAME COLUMN "branchCoherence" TO branch_coherence;
ALTER TABLE coherence_snapshots RENAME COLUMN "rowCoherence" TO row_coherence;
ALTER TABLE coherence_snapshots RENAME COLUMN "columnCoherence" TO column_coherence;
ALTER TABLE coherence_snapshots RENAME COLUMN "dimensionLayerCoherence" TO dimension_layer_coherence;
ALTER TABLE coherence_snapshots RENAME COLUMN "temporalCoherence" TO temporal_coherence;
ALTER TABLE coherence_snapshots RENAME COLUMN "goalCoherence" TO goal_coherence;
ALTER TABLE coherence_snapshots RENAME COLUMN "coherenceDelta" TO coherence_delta;
ALTER TABLE coherence_snapshots RENAME COLUMN "gapClosureDelta" TO gap_closure_delta;
ALTER TABLE coherence_snapshots RENAME COLUMN "coherenceViolations" TO coherence_violations;
ALTER TABLE coherence_snapshots RENAME COLUMN "goalUnchanged" TO goal_unchanged;
ALTER TABLE coherence_snapshots RENAME COLUMN "matrixStructureStable" TO matrix_structure_stable;
ALTER TABLE coherence_snapshots RENAME COLUMN "operatorTargetsConsistent" TO operator_targets_consistent;
ALTER TABLE coherence_snapshots RENAME COLUMN "createdAt" TO created_at;

-- ============================================
-- value_trajectories
-- ============================================
ALTER TABLE value_trajectories RENAME COLUMN "userId" TO user_id;
ALTER TABLE value_trajectories RENAME COLUMN "organizationId" TO organization_id;
ALTER TABLE value_trajectories RENAME COLUMN "sessionId" TO session_id;
ALTER TABLE value_trajectories RENAME COLUMN "goalId" TO goal_id;
ALTER TABLE value_trajectories RENAME COLUMN "valueId" TO value_id;
ALTER TABLE value_trajectories RENAME COLUMN "interventionStatus" TO intervention_status;
ALTER TABLE value_trajectories RENAME COLUMN "remainingGap" TO remaining_gap;
ALTER TABLE value_trajectories RENAME COLUMN "predictedSessionsToTarget" TO predicted_sessions_to_target;

-- ============================================
-- discovered_goals
-- ============================================
ALTER TABLE discovered_goals RENAME COLUMN "sessionId" TO session_id;
ALTER TABLE discovered_goals RENAME COLUMN "oneLiner" TO one_liner;
ALTER TABLE discovered_goals RENAME COLUMN "relevantOperators" TO relevant_operators;
ALTER TABLE discovered_goals RENAME COLUMN "operatorDeficit" TO operator_deficit;
ALTER TABLE discovered_goals RENAME COLUMN "operatorConfusion" TO operator_confusion;
ALTER TABLE discovered_goals RENAME COLUMN "operatorPotential" TO operator_potential;
ALTER TABLE discovered_goals RENAME COLUMN "operatorShadow" TO operator_shadow;
ALTER TABLE discovered_goals RENAME COLUMN "consciousnessEvolution" TO consciousness_evolution;
ALTER TABLE discovered_goals RENAME COLUMN "sourceFiles" TO source_files;
ALTER TABLE discovered_goals RENAME COLUMN "createdAt" TO created_at;
ALTER TABLE discovered_goals RENAME COLUMN "isSelected" TO is_selected;
ALTER TABLE discovered_goals RENAME COLUMN "selectedAt" TO selected_at;

-- ============================================
-- user_goal_inventories
-- ============================================
ALTER TABLE user_goal_inventories RENAME COLUMN "odId" TO od_id;
ALTER TABLE user_goal_inventories RENAME COLUMN "createdAt" TO created_at;
ALTER TABLE user_goal_inventories RENAME COLUMN "updatedAt" TO updated_at;

-- ============================================
-- documents
-- ============================================
ALTER TABLE documents RENAME COLUMN "userId" TO user_id;
ALTER TABLE documents RENAME COLUMN "organizationId" TO organization_id;
ALTER TABLE documents RENAME COLUMN "businessContext" TO business_context;
ALTER TABLE documents RENAME COLUMN "categoryMapping" TO category_mapping;
ALTER TABLE documents RENAME COLUMN "isActive" TO is_active;
ALTER TABLE documents RENAME COLUMN "parentDocumentId" TO parent_document_id;
ALTER TABLE documents RENAME COLUMN "updatedContext" TO updated_context;
ALTER TABLE documents RENAME COLUMN "conversationId" TO conversation_id;
ALTER TABLE documents RENAME COLUMN "goalTitle" TO goal_title;
ALTER TABLE documents RENAME COLUMN "goalId" TO goal_id;
ALTER TABLE documents RENAME COLUMN "completedAt" TO completed_at;
ALTER TABLE documents RENAME COLUMN "cascadeRules" TO cascade_rules;
ALTER TABLE documents RENAME COLUMN "lastUpdatedAt" TO last_updated_at;
ALTER TABLE documents RENAME COLUMN "createdAt" TO created_at;

-- ============================================
-- breakthrough_concepts
-- ============================================
ALTER TABLE breakthrough_concepts RENAME COLUMN "progressionPattern" TO progression_pattern;
ALTER TABLE breakthrough_concepts RENAME COLUMN "metricMapping" TO metric_mapping;
ALTER TABLE breakthrough_concepts RENAME COLUMN "createdAt" TO created_at;
ALTER TABLE breakthrough_concepts RENAME COLUMN "updatedAt" TO updated_at;

-- ============================================
-- document_breakthrough_mappings
-- ============================================
ALTER TABLE document_breakthrough_mappings RENAME COLUMN "documentId" TO document_id;
ALTER TABLE document_breakthrough_mappings RENAME COLUMN "milestoneConceptId" TO milestone_concept_id;
ALTER TABLE document_breakthrough_mappings RENAME COLUMN "currentStage" TO current_stage;
ALTER TABLE document_breakthrough_mappings RENAME COLUMN "stageConfidence" TO stage_confidence;
ALTER TABLE document_breakthrough_mappings RENAME COLUMN "stageDescription" TO stage_description;
ALTER TABLE document_breakthrough_mappings RENAME COLUMN "nextStageSuggestion" TO next_stage_suggestion;
ALTER TABLE document_breakthrough_mappings RENAME COLUMN "isComplete" TO is_complete;
ALTER TABLE document_breakthrough_mappings RENAME COLUMN "detectedAt" TO detected_at;
ALTER TABLE document_breakthrough_mappings RENAME COLUMN "lastAnalyzedAt" TO last_analyzed_at;
ALTER TABLE document_breakthrough_mappings RENAME COLUMN "analysisReasoning" TO analysis_reasoning;

-- ============================================
-- super_tasks
-- ============================================
ALTER TABLE super_tasks RENAME COLUMN "userId" TO user_id;
ALTER TABLE super_tasks RENAME COLUMN "organizationId" TO organization_id;
ALTER TABLE super_tasks RENAME COLUMN "totalSubTasks" TO total_sub_tasks;
ALTER TABLE super_tasks RENAME COLUMN "completedSubTasks" TO completed_sub_tasks;
ALTER TABLE super_tasks RENAME COLUMN "detectionReasoning" TO detection_reasoning;
ALTER TABLE super_tasks RENAME COLUMN "detectedAt" TO detected_at;
ALTER TABLE super_tasks RENAME COLUMN "completedAt" TO completed_at;
ALTER TABLE super_tasks RENAME COLUMN "createdAt" TO created_at;
ALTER TABLE super_tasks RENAME COLUMN "updatedAt" TO updated_at;

-- ============================================
-- super_task_documents
-- ============================================
ALTER TABLE super_task_documents RENAME COLUMN "superTaskId" TO super_task_id;
ALTER TABLE super_task_documents RENAME COLUMN "documentId" TO document_id;

-- ============================================
-- sub_tasks
-- ============================================
ALTER TABLE sub_tasks RENAME COLUMN "documentId" TO document_id;
ALTER TABLE sub_tasks RENAME COLUMN "superTaskId" TO super_task_id;
ALTER TABLE sub_tasks RENAME COLUMN "isComplete" TO is_complete;
ALTER TABLE sub_tasks RENAME COLUMN "completedAt" TO completed_at;
ALTER TABLE sub_tasks RENAME COLUMN "createdAt" TO created_at;
ALTER TABLE sub_tasks RENAME COLUMN "updatedAt" TO updated_at;

-- ============================================
-- document_assumptions
-- ============================================
ALTER TABLE document_assumptions RENAME COLUMN "documentId" TO document_id;
ALTER TABLE document_assumptions RENAME COLUMN "affectedCells" TO affected_cells;
ALTER TABLE document_assumptions RENAME COLUMN "createdAt" TO created_at;
ALTER TABLE document_assumptions RENAME COLUMN "updatedAt" TO updated_at;

-- ============================================
-- document_goal_connections
-- ============================================
ALTER TABLE document_goal_connections RENAME COLUMN "documentId" TO document_id;
ALTER TABLE document_goal_connections RENAME COLUMN "goalText" TO goal_text;
ALTER TABLE document_goal_connections RENAME COLUMN "contributionType" TO contribution_type;
ALTER TABLE document_goal_connections RENAME COLUMN "supportingCells" TO supporting_cells;
ALTER TABLE document_goal_connections RENAME COLUMN "createdAt" TO created_at;
ALTER TABLE document_goal_connections RENAME COLUMN "updatedAt" TO updated_at;

-- ============================================
-- document_progress
-- ============================================
ALTER TABLE document_progress RENAME COLUMN "documentId" TO document_id;
ALTER TABLE document_progress RENAME COLUMN "overallProgress" TO overall_progress;
ALTER TABLE document_progress RENAME COLUMN "createdAt" TO created_at;
ALTER TABLE document_progress RENAME COLUMN "updatedAt" TO updated_at;

-- ============================================
-- consciousness_snapshots
-- ============================================
ALTER TABLE consciousness_snapshots RENAME COLUMN "goalId" TO goal_id;
ALTER TABLE consciousness_snapshots RENAME COLUMN "userId" TO user_id;
ALTER TABLE consciousness_snapshots RENAME COLUMN "awarenessLevel" TO awareness_level;
ALTER TABLE consciousness_snapshots RENAME COLUMN "readinessLevel" TO readiness_level;
ALTER TABLE consciousness_snapshots RENAME COLUMN "sophisticationLevel" TO sophistication_level;
ALTER TABLE consciousness_snapshots RENAME COLUMN "urgencyLevel" TO urgency_level;
ALTER TABLE consciousness_snapshots RENAME COLUMN "detectionCriteria" TO detection_criteria;
ALTER TABLE consciousness_snapshots RENAME COLUMN "frameworkVersion" TO framework_version;
ALTER TABLE consciousness_snapshots RENAME COLUMN "calculatedAt" TO calculated_at;

-- ============================================
-- operator_executions
-- ============================================
ALTER TABLE operator_executions RENAME COLUMN "goalId" TO goal_id;
ALTER TABLE operator_executions RENAME COLUMN "transformId" TO transform_id;
ALTER TABLE operator_executions RENAME COLUMN "transformName" TO transform_name;
ALTER TABLE operator_executions RENAME COLUMN "processingType" TO processing_type;
ALTER TABLE operator_executions RENAME COLUMN "inputValue" TO input_value;
ALTER TABLE operator_executions RENAME COLUMN "outputValue" TO output_value;
ALTER TABLE operator_executions RENAME COLUMN "contextAwareness" TO context_awareness;
ALTER TABLE operator_executions RENAME COLUMN "actionReadiness" TO action_readiness;
ALTER TABLE operator_executions RENAME COLUMN "skillLevel" TO skill_level;
ALTER TABLE operator_executions RENAME COLUMN "timeConstraint" TO time_constraint;
ALTER TABLE operator_executions RENAME COLUMN "frameworkVersion" TO framework_version;
ALTER TABLE operator_executions RENAME COLUMN "executedAt" TO executed_at;

-- ============================================
-- cascade_executions
-- ============================================
ALTER TABLE cascade_executions RENAME COLUMN "goalId" TO goal_id;
ALTER TABLE cascade_executions RENAME COLUMN "calculationMethod" TO calculation_method;
ALTER TABLE cascade_executions RENAME COLUMN "matrixValues" TO matrix_values;
ALTER TABLE cascade_executions RENAME COLUMN "rowCalculations" TO row_calculations;
ALTER TABLE cascade_executions RENAME COLUMN "coherenceScore" TO coherence_score;
ALTER TABLE cascade_executions RENAME COLUMN "frameworkVersion" TO framework_version;
ALTER TABLE cascade_executions RENAME COLUMN "calculatedAt" TO calculated_at;
ALTER TABLE cascade_executions RENAME COLUMN "durationMs" TO duration_ms;

-- ============================================
-- questionnaire_sessions
-- ============================================
ALTER TABLE questionnaire_sessions RENAME COLUMN "goalId" TO goal_id;
ALTER TABLE questionnaire_sessions RENAME COLUMN "userId" TO user_id;
ALTER TABLE questionnaire_sessions RENAME COLUMN "questionsAsked" TO questions_asked;
ALTER TABLE questionnaire_sessions RENAME COLUMN "answersProvided" TO answers_provided;
ALTER TABLE questionnaire_sessions RENAME COLUMN "coherenceGaps" TO coherence_gaps;
ALTER TABLE questionnaire_sessions RENAME COLUMN "startedAt" TO started_at;
ALTER TABLE questionnaire_sessions RENAME COLUMN "completedAt" TO completed_at;
ALTER TABLE questionnaire_sessions RENAME COLUMN "totalQuestions" TO total_questions;
ALTER TABLE questionnaire_sessions RENAME COLUMN "answeredQuestions" TO answered_questions;
ALTER TABLE questionnaire_sessions RENAME COLUMN "frameworkVersion" TO framework_version;

-- ============================================
-- global_settings
-- ============================================
ALTER TABLE global_settings RENAME COLUMN "freeTrialCredits" TO free_trial_credits;
ALTER TABLE global_settings RENAME COLUMN "trialDurationDays" TO trial_duration_days;
ALTER TABLE global_settings RENAME COLUMN "updatedAt" TO updated_at;
ALTER TABLE global_settings RENAME COLUMN "updatedBy" TO updated_by;

-- ============================================
-- promo_codes
-- ============================================
ALTER TABLE promo_codes RENAME COLUMN "maxUses" TO max_uses;
ALTER TABLE promo_codes RENAME COLUMN "usedCount" TO used_count;
ALTER TABLE promo_codes RENAME COLUMN "createdBy" TO created_by;
ALTER TABLE promo_codes RENAME COLUMN "createdAt" TO created_at;
ALTER TABLE promo_codes RENAME COLUMN "expiresAt" TO expires_at;
ALTER TABLE promo_codes RENAME COLUMN "isActive" TO is_active;

-- ============================================
-- promo_code_redemptions
-- ============================================
ALTER TABLE promo_code_redemptions RENAME COLUMN "promoCodeId" TO promo_code_id;
ALTER TABLE promo_code_redemptions RENAME COLUMN "userId" TO user_id;
ALTER TABLE promo_code_redemptions RENAME COLUMN "redeemedAt" TO redeemed_at;

COMMIT;
