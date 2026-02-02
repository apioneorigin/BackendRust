-- Migration: Drop deprecated matrix_data column
-- Date: 2026-02-02
-- Reason: matrix_data is now stored per-document in generated_documents column

-- Drop the legacy matrix_data column from chat_conversations
ALTER TABLE chat_conversations DROP COLUMN IF EXISTS matrix_data;
