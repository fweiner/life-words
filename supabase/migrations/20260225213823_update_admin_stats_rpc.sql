DROP FUNCTION IF EXISTS get_admin_user_stats();

CREATE OR REPLACE FUNCTION get_admin_user_stats()
RETURNS TABLE (
  id UUID, email TEXT, full_name TEXT, created_at TIMESTAMPTZ,
  contact_count BIGINT, item_count BIGINT, session_count BIGINT,
  last_active_at TIMESTAMPTZ, account_status TEXT, trial_ends_at TIMESTAMPTZ
)
LANGUAGE sql SECURITY DEFINER AS $$
  SELECT p.id, p.email, p.full_name, p.created_at,
    (SELECT COUNT(*) FROM personal_contacts WHERE user_id = p.id AND is_active = TRUE),
    (SELECT COUNT(*) FROM personal_items WHERE user_id = p.id AND is_active = TRUE),
    (SELECT COUNT(*) FROM life_words_sessions WHERE user_id = p.id)
    + (SELECT COUNT(*) FROM life_words_question_sessions WHERE user_id = p.id)
    + (SELECT COUNT(*) FROM life_words_information_sessions WHERE user_id = p.id),
    GREATEST(
      (SELECT MAX(started_at) FROM life_words_sessions WHERE user_id = p.id),
      (SELECT MAX(started_at) FROM life_words_question_sessions WHERE user_id = p.id),
      (SELECT MAX(started_at) FROM life_words_information_sessions WHERE user_id = p.id)
    ),
    p.account_status,
    p.trial_ends_at
  FROM profiles p ORDER BY p.created_at DESC;
$$;
