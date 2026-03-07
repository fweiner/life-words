-- Remove duplicate (session_id, contact_id) rows, keeping only the most recent.
DELETE FROM life_words_responses
WHERE id NOT IN (
  SELECT DISTINCT ON (session_id, contact_id) id
  FROM life_words_responses
  ORDER BY session_id, contact_id, created_at DESC
);

-- Add unique constraint on (session_id, contact_id) so PostgREST upsert works.
-- Without this, the on_conflict=session_id,contact_id parameter returns 400.
ALTER TABLE life_words_responses
  ADD CONSTRAINT life_words_responses_session_contact_unique
  UNIQUE (session_id, contact_id);
