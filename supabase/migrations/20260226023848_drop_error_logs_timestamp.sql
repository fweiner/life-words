-- Drop redundant timestamp column (created_at already tracks this)
DROP INDEX IF EXISTS error_logs_timestamp_idx;
ALTER TABLE public.error_logs DROP COLUMN IF EXISTS timestamp;
