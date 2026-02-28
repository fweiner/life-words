-- Add answer matching accommodation columns to profiles
ALTER TABLE profiles
  ADD COLUMN IF NOT EXISTS match_acceptable_alternatives boolean DEFAULT true,
  ADD COLUMN IF NOT EXISTS match_partial_substring boolean DEFAULT true,
  ADD COLUMN IF NOT EXISTS match_word_overlap boolean DEFAULT true,
  ADD COLUMN IF NOT EXISTS match_stop_word_filtering boolean DEFAULT true,
  ADD COLUMN IF NOT EXISTS match_synonyms boolean DEFAULT true,
  ADD COLUMN IF NOT EXISTS match_first_name_only boolean DEFAULT true;
