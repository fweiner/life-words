ALTER TABLE profiles ADD COLUMN account_status TEXT DEFAULT 'trial' NOT NULL;
ALTER TABLE profiles ADD COLUMN trial_ends_at TIMESTAMPTZ;

-- Existing users predate the trial system — mark them as paid
UPDATE profiles SET account_status = 'paid', trial_ends_at = NULL;

-- Update signup trigger to give new users a 7-day trial
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name, account_status, trial_ends_at)
    VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'full_name', 'trial', NOW() + INTERVAL '7 days');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
