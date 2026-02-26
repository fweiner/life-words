/**
 * TypeScript types mirroring backend Pydantic response schemas.
 *
 * These are used with the API client for type-safe responses.
 */

// Re-export matching types
export type {
  MatchSettings,
  NameMatchResult,
  QuestionMatchResult,
  InformationMatchResult,
  WordFindingMatchResult,
  ExtractAnswerResult,
} from './matching'

// Profile
export interface ProfileResponse {
  id: string
  email: string
  full_name: string | null
  voice_gender: string | null
  [key: string]: unknown
}

// Contact
export interface PersonalContactResponse {
  id: string
  user_id: string
  name: string
  nickname: string | null
  relationship: string
  photo_url: string | null
  category: string | null
  description: string | null
  association: string | null
  location_context: string | null
  interests: string | null
  personality: string | null
  values: string | null
  social_behavior: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

// Invite
export interface ContactInviteResponse {
  id: string
  user_id: string
  recipient_email: string
  recipient_name: string
  token: string
  custom_message: string | null
  status: string
  created_at: string
  expires_at: string
  completed_at: string | null
  contact_id: string | null
}

export interface InviteVerifyResponse {
  valid: boolean
  status: string
  inviter_name?: string
  recipient_name?: string
  contact_name?: string
}

// Messaging
export interface MessageResponse {
  id: string
  user_id: string
  contact_id: string
  direction: 'user_to_contact' | 'contact_to_user'
  text_content: string | null
  photo_url: string | null
  voice_url: string | null
  voice_duration_seconds: number | null
  is_read: boolean
  read_at: string | null
  created_at: string
}

export interface ConversationSummary {
  contact_id: string
  contact_name: string
  contact_photo_url: string | null
  contact_relationship: string
  last_message_text: string | null
  last_message_at: string | null
  last_message_direction: string | null
  unread_count: number
  has_messaging_token: boolean
}

export interface MessagingTokenResponse {
  id: string
  contact_id: string
  token: string
  messaging_url: string
  is_active: boolean
  created_at: string
  last_used_at: string | null
}

// Treatment session
export interface TreatmentSessionResponse {
  id: string
  user_id: string
  treatment_type: string
  status: string
  started_at: string
  completed_at: string | null
  [key: string]: unknown
}

// Admin
export interface AdminUserStats {
  id: string
  email: string
  full_name: string | null
  created_at: string
  contact_count: number
  item_count: number
  session_count: number
  last_active_at: string | null
  account_status: string
  trial_ends_at: string | null
  stripe_customer_id: string | null
  subscription_plan: string | null
  subscription_current_period_end: string | null
}

export interface AdminCreateUserRequest {
  email: string
  password: string
  full_name?: string
  account_status?: string
  subscription_plan?: string
  trial_days?: number
}

export interface AdminCreateUserResponse {
  success: boolean
  message: string
  user_id: string
}

export interface AdminUpdateUserRequest {
  email?: string
  password?: string
  full_name?: string
  account_status?: string
  subscription_plan?: string
  trial_ends_at?: string
}

export interface AdminUpdateUserResponse {
  success: boolean
  message: string
  user: AdminUserStats
}

export interface AdminToggleUserResponse {
  success: boolean
  message: string
  user_id: string
  new_status: string
}

export interface ErrorLogEntry {
  id: string
  created_at: string
  error_message: string
  error_type: string | null
  stacktrace: string | null
  endpoint: string | null
  http_method: string | null
  request_body: Record<string, unknown> | null
  query_params: Record<string, unknown> | null
  status_code: number | null
  user_id: string | null
  user_email: string | null
  source: string
  service_name: string | null
  function_name: string | null
  environment: string | null
  is_resolved: boolean
  resolved_at: string | null
  resolved_by: string | null
  notes: string | null
}

export interface ErrorLogListResponse {
  errors: ErrorLogEntry[]
  total: number
  page: number
  per_page: number
}

// Subscription
export interface SubscriptionStatus {
  account_status: string
  trial_ends_at: string | null
  is_trial_active: boolean
  is_paid: boolean
  can_practice: boolean
  subscription_plan: string | null
  subscription_current_period_end: string | null
  has_stripe_customer: boolean
  has_subscription: boolean
}

// Items
export interface PersonalItemResponse {
  id: string
  user_id: string
  name: string
  category: string
  description: string | null
  photo_url: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}
