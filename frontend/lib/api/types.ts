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
