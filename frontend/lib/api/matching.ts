/**
 * Typed helpers for the answer matching API endpoints.
 *
 * These are public endpoints (no auth needed) — they're called during
 * practice sessions and don't require user identity.
 */
import { apiClient } from './client'

// ============== Request/Response types ==============

export interface MatchSettings {
  match_acceptable_alternatives?: boolean
  match_partial_substring?: boolean
  match_word_overlap?: boolean
  match_stop_word_filtering?: boolean
  match_synonyms?: boolean
  match_first_name_only?: boolean
}

export interface NameMatchResult {
  is_correct: boolean
  matched_via: string | null
}

export interface QuestionMatchResult {
  is_correct: boolean
  is_partial: boolean
  score: number
}

export interface InformationMatchResult {
  is_correct: boolean
  confidence: number
}

export interface WordFindingMatchResult {
  is_correct: boolean
}

export interface ExtractAnswerResult {
  answer: string
}

// ============== API functions ==============

export async function evaluateNameAnswer(
  userAnswer: string,
  expectedName: string,
  options?: {
    nickname?: string
    alternatives?: string[]
    settings?: MatchSettings
  }
): Promise<NameMatchResult> {
  return apiClient.postPublic<NameMatchResult>('/api/matching/evaluate/name', {
    user_answer: userAnswer,
    expected_name: expectedName,
    nickname: options?.nickname,
    alternatives: options?.alternatives || [],
    settings: options?.settings,
  })
}

export async function evaluateQuestionAnswer(
  userAnswer: string,
  expectedAnswer: string,
  acceptableAnswers: string[] = [],
  settings?: MatchSettings
): Promise<QuestionMatchResult> {
  return apiClient.postPublic<QuestionMatchResult>('/api/matching/evaluate/question', {
    user_answer: userAnswer,
    expected_answer: expectedAnswer,
    acceptable_answers: acceptableAnswers,
    settings,
  })
}

export async function evaluateInformationAnswer(
  userAnswer: string,
  expectedValue: string,
  fieldName: string
): Promise<InformationMatchResult> {
  return apiClient.postPublic<InformationMatchResult>('/api/matching/evaluate/information', {
    user_answer: userAnswer,
    expected_value: expectedValue,
    field_name: fieldName,
  })
}

export async function evaluateWordFindingAnswer(
  userAnswer: string,
  expectedName: string,
  alternatives: string[] = []
): Promise<WordFindingMatchResult> {
  return apiClient.postPublic<WordFindingMatchResult>('/api/matching/evaluate/word-finding', {
    user_answer: userAnswer,
    expected_name: expectedName,
    alternatives,
  })
}

export async function extractAnswer(
  transcript: string
): Promise<string> {
  const result = await apiClient.postPublic<ExtractAnswerResult>('/api/matching/extract-answer', {
    transcript,
  })
  return result.answer
}
