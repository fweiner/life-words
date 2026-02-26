-- Enhance error_logs table with full context, classification, and resolution tracking.

-- Rename existing columns for consistency with the new schema
ALTER TABLE public.error_logs RENAME COLUMN method TO http_method;
ALTER TABLE public.error_logs RENAME COLUMN traceback TO stacktrace;

-- Drop redundant timestamp column (created_at already tracks this)
DROP INDEX IF EXISTS error_logs_timestamp_idx;
ALTER TABLE public.error_logs DROP COLUMN timestamp;

-- Make endpoint and status_code nullable (manual/swallowed logs may not have these)
ALTER TABLE public.error_logs ALTER COLUMN endpoint DROP NOT NULL;
ALTER TABLE public.error_logs ALTER COLUMN status_code DROP NOT NULL;

-- Add new columns
ALTER TABLE public.error_logs
    ADD COLUMN error_type      TEXT,
    ADD COLUMN request_body    JSONB,
    ADD COLUMN query_params    JSONB,
    ADD COLUMN user_email      TEXT,
    ADD COLUMN source          TEXT NOT NULL DEFAULT 'unhandled',
    ADD COLUMN service_name    TEXT,
    ADD COLUMN function_name   TEXT,
    ADD COLUMN environment     TEXT,
    ADD COLUMN is_resolved     BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN resolved_at     TIMESTAMPTZ,
    ADD COLUMN resolved_by     TEXT,
    ADD COLUMN notes           TEXT;

-- Add indexes for common query patterns
CREATE INDEX idx_error_logs_unresolved ON error_logs (is_resolved) WHERE is_resolved = FALSE;
CREATE INDEX idx_error_logs_source ON error_logs (source);
CREATE INDEX idx_error_logs_endpoint ON error_logs (endpoint);
