'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { createClient } from '@/lib/supabase'
import Image from 'next/image'
import SpeechRecognitionButton from '@/components/shared/SpeechRecognitionButton'
import { speak, waitForVoices } from '@/lib/utils/textToSpeech'
import { useVoicePreference } from '@/hooks/useVoicePreference'
import { getRandomPositiveFeedback } from '@/lib/utils/positiveFeedback'
import { evaluateQuestionAnswer } from '@/lib/api/matching'
import { apiClient } from '@/lib/api/client'

interface PersonalContact {
  id: string
  name: string
  nickname?: string
  relationship: string
  photo_url: string
  interests?: string
  personality?: string
  location_context?: string
  association?: string
}

interface GeneratedQuestion {
  contact_id: string
  contact_name: string
  contact_photo_url: string
  question_type: number
  question_text: string
  expected_answer: string
  acceptable_answers: string[]
}

interface QuestionSession {
  id: string
  user_id: string
  contact_ids: string[]
  is_completed: boolean
  total_questions: number
  total_correct: number
}

interface QuestionResponse {
  question_type: number
  is_correct: boolean
  is_partial: boolean
  response_time: number
  correctness_score: number
}

// Session phases
type SessionPhase = 'study' | 'quiz' | 'completed'

// Question type names for display
const QUESTION_TYPE_NAMES: Record<number, string> = {
  1: 'Relationship',
  2: 'Association',
  3: 'Interests',
  4: 'Personality',
  5: 'Name Recall'
}

// Answer evaluation is now handled by the backend via evaluateQuestionAnswer API

// Accommodation settings interface (used for UI state, sent to backend)
interface AccommodationSettings {
  match_acceptable_alternatives: boolean
  match_partial_substring: boolean
  match_word_overlap: boolean
  match_stop_word_filtering: boolean
  match_synonyms: boolean
  match_first_name_only: boolean
}

const DEFAULT_ACCOMMODATIONS: AccommodationSettings = {
  match_acceptable_alternatives: true,
  match_partial_substring: true,
  match_word_overlap: true,
  match_stop_word_filtering: true,
  match_synonyms: true,
  match_first_name_only: true,
}

// Generate contextual cues based on question type and contact info
function generateCue(
  question: GeneratedQuestion,
  contact: PersonalContact | undefined,
  cueLevel: number
): string {
  const questionType = question.question_type

  // Question Type 1: Relationship - "What is X's relationship to you?"
  if (questionType === 1) {
    if (cueLevel === 1) {
      // First cue: category hint
      if (contact?.personality) {
        return `Think about someone who is ${contact.personality}`
      }
      if (contact?.location_context) {
        return `Think about who you see ${contact.location_context}`
      }
      return "Think about how this person is connected to your family"
    }
    if (cueLevel === 2) {
      // Second cue: more specific
      if (contact?.interests) {
        return `This person enjoys ${contact.interests}`
      }
      if (contact?.association) {
        return `Remember: ${contact.association}`
      }
      return "Look at the photo - how do you know this person?"
    }
  }

  // Question Type 2: Association/Location - "Where do you usually see X?"
  if (questionType === 2) {
    if (cueLevel === 1) {
      const rel = contact?.relationship
      const relLabel = rel && rel !== 'other' ? rel : 'loved one'
      return `Think about where you spend time with your ${relLabel}`
    }
    if (cueLevel === 2) {
      if (contact?.interests) {
        return `This person enjoys ${contact.interests} - where might that happen?`
      }
      return `Picture yourself with ${question.contact_name} - where are you?`
    }
  }

  // Question Type 3: Interests - "What does X enjoy doing?"
  if (questionType === 3) {
    if (cueLevel === 1) {
      if (contact?.personality) {
        return `This person is ${contact.personality} - what might they enjoy?`
      }
      return `Think about what makes ${question.contact_name} happy`
    }
    if (cueLevel === 2) {
      if (contact?.location_context) {
        return `When you see them ${contact.location_context}, what are they often doing?`
      }
      return `What do you do together with ${question.contact_name}?`
    }
  }

  // Question Type 4: Personality - "How would you describe X's personality?"
  if (questionType === 4) {
    if (cueLevel === 1) {
      if (contact?.interests) {
        return `Someone who enjoys ${contact.interests} - how would you describe them?`
      }
      return `When you think of ${question.contact_name}, what kind of person comes to mind?`
    }
    if (cueLevel === 2) {
      if (contact?.association) {
        return `Remember: ${contact.association}. What does that tell you about them?`
      }
      return `Is ${question.contact_name} more outgoing or quiet? Calm or energetic?`
    }
  }

  // Question Type 5: Name from description - "Who is your X who...?"
  if (questionType === 5) {
    if (cueLevel === 1) {
      return `Look at the photo carefully - who do you see?`
    }
    if (cueLevel === 2) {
      if (contact?.nickname) {
        return `You might call this person "${contact.nickname}"`
      }
      // Give first letter hint for names
      const firstLetter = question.expected_answer.charAt(0).toUpperCase()
      return `The name starts with the letter ${firstLetter}`
    }
  }

  // Default fallback
  return "Take another look and give it another try"
}

export default function LifeWordsQuestionSessionPage() {
  const router = useRouter()
  const params = useParams()
  const sessionId = params.id as string
  const supabase = createClient()
  const voiceGender = useVoicePreference()

  // Session state
  const [session, setSession] = useState<QuestionSession | null>(null)
  const [questions, setQuestions] = useState<GeneratedQuestion[]>([])
  const [contacts, setContacts] = useState<PersonalContact[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [accommodations, setAccommodations] = useState<AccommodationSettings>(DEFAULT_ACCOMMODATIONS)

  // Phase state
  const [phase, setPhase] = useState<SessionPhase>('study')
  const [studyIndex, setStudyIndex] = useState(0)

  // Quiz state
  const [currentIndex, setCurrentIndex] = useState(0)
  const [currentQuestion, setCurrentQuestion] = useState<GeneratedQuestion | null>(null)
  const [isAnswering, setIsAnswering] = useState(false)
  const [isProcessingAnswer, setIsProcessingAnswer] = useState(false)
  const [showFeedback, setShowFeedback] = useState(false)
  const [lastResult, setLastResult] = useState<{
    isCorrect: boolean
    isPartial: boolean
    userAnswer: string
    expectedAnswer: string
  } | null>(null)
  const [responses, setResponses] = useState<QuestionResponse[]>([])
  const [, setQuestionStartTime] = useState<number>(0)
  const [, setStatistics] = useState<unknown>(null)

  // Cueing state
  const [cueLevel, setCueLevel] = useState(0) // 0 = no cue, 1 = first cue, 2 = second cue, 3 = reveal answer
  const [currentCue, setCurrentCue] = useState<string | null>(null)
  const [showCue, setShowCue] = useState(false)
  const [cuesUsedForQuestion, setCuesUsedForQuestion] = useState(0)
  const MAX_CUES = 2 // Number of cues before revealing answer

  // Refs for async callbacks
  const isProcessingAnswerRef = useRef(false)
  const currentQuestionRef = useRef<GeneratedQuestion | null>(null)
  const currentIndexRef = useRef(0)
  const questionStartTimeRef = useRef(0)
  const pendingSavesRef = useRef<Promise<void>[]>([])
  const hasSpokenForCurrentQuestionRef = useRef(false)

  const initializeSession = useCallback(async () => {
    try {
      setLoading(true)

      const { data: { user } } = await supabase.auth.getUser()
      if (!user) {
        router.push('/login')
        return
      }

      // Load user's accommodation settings from profile
      try {
        const profile = await apiClient.get<Record<string, unknown>>('/api/profile')
        setAccommodations({
          match_acceptable_alternatives: (profile.match_acceptable_alternatives as boolean) ?? true,
          match_partial_substring: (profile.match_partial_substring as boolean) ?? true,
          match_word_overlap: (profile.match_word_overlap as boolean) ?? true,
          match_stop_word_filtering: (profile.match_stop_word_filtering as boolean) ?? true,
          match_synonyms: (profile.match_synonyms as boolean) ?? true,
          match_first_name_only: (profile.match_first_name_only as boolean) ?? true,
        })
      } catch {
        console.warn('Could not load accommodation settings, using defaults')
      }

      const sessionData = await apiClient.get<Record<string, unknown>>(
        `/api/life-words/question-sessions/${sessionId}`
      )
      setSession(sessionData.session as QuestionSession)
      setContacts(sessionData.contacts as PersonalContact[])

      // If session has existing responses, this is a resumed session - skip to quiz
      if (sessionData.responses && (sessionData.responses as unknown[]).length > 0) {
        setResponses(sessionData.responses as QuestionResponse[])
      }

      // Generate questions from contacts
      const questionsResponse = await regenerateQuestions(
        sessionData.contacts as PersonalContact[]
      )

      if (questionsResponse && questionsResponse.length > 0) {
        setQuestions(questionsResponse)
        // Start in study phase
        setPhase('study')
        setStudyIndex(0)
      }

      setLoading(false)
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      console.error('Session initialization error:', err)
      setError(`Failed to initialize session: ${message}`)
      setLoading(false)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId])

  // Initialize session
  useEffect(() => {
    initializeSession()
  }, [initializeSession])

  const regenerateQuestions = async (
    contactList: PersonalContact[]
  ): Promise<GeneratedQuestion[]> => {
    const generated: GeneratedQuestion[] = []

    if (contactList.length < 2) return generated

    const shuffled = [...contactList].sort(() => Math.random() - 0.5)
    const c1 = shuffled[0]
    const c2 = shuffled[1] || shuffled[0]

    // Question 1: Relationship
    generated.push({
      contact_id: c1.id,
      contact_name: c1.name,
      contact_photo_url: c1.photo_url,
      question_type: 1,
      question_text: `What is ${c1.name}'s relationship to you?`,
      expected_answer: c1.relationship,
      acceptable_answers: [c1.relationship.toLowerCase(), c1.relationship]
    })

    // Question 2: Association
    const location = c2.location_context || c2.association || 'at home'
    generated.push({
      contact_id: c2.id,
      contact_name: c2.name,
      contact_photo_url: c2.photo_url,
      question_type: 2,
      question_text: `Where do you usually see ${c2.name}?`,
      expected_answer: location,
      acceptable_answers: [location.toLowerCase()]
    })

    // Question 3: Interests
    const interests = c1.interests || 'spending time together'
    generated.push({
      contact_id: c1.id,
      contact_name: c1.name,
      contact_photo_url: c1.photo_url,
      question_type: 3,
      question_text: `What does ${c1.name} enjoy doing?`,
      expected_answer: interests,
      acceptable_answers: [interests.toLowerCase()]
    })

    // Question 4: Personality
    const personality = c2.personality || 'kind and caring'
    generated.push({
      contact_id: c2.id,
      contact_name: c2.name,
      contact_photo_url: c2.photo_url,
      question_type: 4,
      question_text: `How would you describe ${c2.name}'s personality?`,
      expected_answer: personality,
      acceptable_answers: [personality.toLowerCase()]
    })

    // Question 5: Name from description
    const hint = c1.interests || c1.personality || 'is special to you'
    let q5Text: string
    if (c1.relationship === 'other') {
      q5Text = `Who is someone special to you who ${hint}?`
    } else if (c1.relationship === 'pet') {
      q5Text = `What is the name of your pet that ${hint}?`
    } else {
      q5Text = `Who is your ${c1.relationship} who ${hint}?`
    }
    generated.push({
      contact_id: c1.id,
      contact_name: c1.name,
      contact_photo_url: c1.photo_url,
      question_type: 5,
      question_text: q5Text,
      expected_answer: c1.name,
      acceptable_answers: [
        c1.name.toLowerCase(),
        c1.name.split(' ')[0].toLowerCase(),
        c1.nickname?.toLowerCase() || ''
      ].filter(Boolean)
    })

    return generated
  }

  // ==================== STUDY PHASE ====================

  const handleStudyNext = async () => {
    if (studyIndex < questions.length - 1) {
      const nextIndex = studyIndex + 1
      setStudyIndex(nextIndex)

      // Speak the next answer
      const nextQ = questions[nextIndex]
      try {
        await speak(`${nextQ.question_text} The answer is: ${nextQ.expected_answer}`, { gender: voiceGender })
      } catch (e) {
        console.warn('TTS failed:', e)
      }
    } else {
      // Done with study phase, start quiz
      startQuizPhase()
    }
  }

  const startQuizPhase = () => {
    setPhase('quiz')
    setCurrentIndex(0)
    currentIndexRef.current = 0

    const firstQuestion = questions[0]
    setCurrentQuestion(firstQuestion)
    currentQuestionRef.current = firstQuestion
    setIsAnswering(true)
    hasSpokenForCurrentQuestionRef.current = false

    const startTime = Date.now()
    setQuestionStartTime(startTime)
    questionStartTimeRef.current = startTime
  }

  // Speak study item when it changes
  useEffect(() => {
    if (phase === 'study' && questions.length > 0 && studyIndex === 0) {
      const speakFirst = async () => {
        try {
          await waitForVoices()
          const q = questions[0]
          await speak(`${q.question_text} The answer is: ${q.expected_answer}`, { gender: voiceGender })
        } catch (e) {
          console.warn('TTS failed:', e)
        }
      }
      speakFirst()
    }
  }, [phase, questions, studyIndex, voiceGender])

  // ==================== QUIZ PHASE ====================

  const handleAnswer = async (transcript: string) => {
    const currentQ = currentQuestionRef.current
    const isProcessing = isProcessingAnswerRef.current
    const startTime = questionStartTimeRef.current

    if (!currentQ || !session || isProcessing) {
      return
    }

    setIsProcessingAnswer(true)
    isProcessingAnswerRef.current = true

    try {
      const responseTime = Date.now() - startTime
      let evaluation: { is_correct: boolean; is_partial: boolean; score: number }
      try {
        evaluation = await evaluateQuestionAnswer(
          transcript,
          currentQ.expected_answer,
          currentQ.acceptable_answers,
          accommodations
        )
      } catch (error) {
        console.warn('Matching API error, treating as incorrect:', error)
        evaluation = { is_correct: false, is_partial: false, score: 0 }
      }

      // Show feedback
      setLastResult({
        isCorrect: evaluation.is_correct,
        isPartial: evaluation.is_partial,
        userAnswer: transcript,
        expectedAnswer: currentQ.expected_answer
      })
      setShowFeedback(true)
      setIsAnswering(false)

      if (evaluation.is_correct) {
        // Correct answer - save and move on
        saveResponse(currentQ, transcript, evaluation, responseTime, cuesUsedForQuestion)
        const feedback = getRandomPositiveFeedback()
        await speak(feedback, { gender: voiceGender })

        // Move to next after delay
        setTimeout(() => {
          setShowFeedback(false)
          setCueLevel(0)
          setCurrentCue(null)
          setShowCue(false)
          setCuesUsedForQuestion(0)
          moveToNext()
        }, 3000)
      } else {
        // Wrong answer - check if we should offer a cue or reveal the answer
        const nextCueLevel = cueLevel + 1

        if (nextCueLevel <= MAX_CUES) {
          // Offer a cue
          const contact = contacts.find(c => c.id === currentQ.contact_id)
          const cue = generateCue(currentQ, contact, nextCueLevel)
          setCueLevel(nextCueLevel)
          setCurrentCue(cue)
          setShowCue(true)
          setCuesUsedForQuestion(nextCueLevel)

          await speak(`Almost! Here's a hint: ${cue}`, { gender: voiceGender })

          // Allow retry - keep feedback showing but re-enable answering after delay
          setTimeout(() => {
            setShowFeedback(false)
            setIsAnswering(true)
            setIsProcessingAnswer(false)
            isProcessingAnswerRef.current = false
          }, 4000)
        } else {
          // Max cues reached - clear cue display and reveal answer
          setShowCue(false)
          setCurrentCue(null)

          saveResponse(currentQ, transcript, evaluation, responseTime, cuesUsedForQuestion)
          await speak(`The answer was ${currentQ.expected_answer}`, { gender: voiceGender })

          // Move to next after delay
          setTimeout(() => {
            setShowFeedback(false)
            setCueLevel(0)
            setCuesUsedForQuestion(0)
            moveToNext()
          }, 3000)
        }
      }
    } catch (err) {
      console.error('Error handling answer:', err)
      setIsProcessingAnswer(false)
      isProcessingAnswerRef.current = false
    }
  }

  const saveResponse = (
    question: GeneratedQuestion,
    userAnswer: string,
    evaluation: { is_correct: boolean; is_partial: boolean; score: number },
    responseTime: number,
    cuesUsed: number = 0
  ) => {
    if (!session) return

    // Track locally immediately
    setResponses(prev => [...prev, {
      question_type: question.question_type,
      is_correct: evaluation.is_correct,
      is_partial: evaluation.is_partial,
      response_time: responseTime,
      correctness_score: evaluation.score
    }])

    // Fire-and-forget with retry — don't block the UX
    const payload = {
      contact_id: question.contact_id,
      question_type: question.question_type,
      question_text: question.question_text,
      expected_answer: question.expected_answer,
      user_answer: userAnswer,
      is_correct: evaluation.is_correct,
      is_partial: evaluation.is_partial,
      response_time: responseTime,
      clarity_score: 0.8,
      correctness_score: evaluation.score,
      cues_used: cuesUsed,
    }
    const trySave = async (attempt: number) => {
      try {
        await apiClient.post(`/api/life-words/question-sessions/${session.id}/responses`, payload)
      } catch {
        if (attempt < 2) {
          await new Promise(r => setTimeout(r, 1000))
          await trySave(attempt + 1)
        } else {
          console.warn('Could not save response after retries')
        }
      }
    }
    const savePromise = trySave(0)
    pendingSavesRef.current.push(savePromise)
    savePromise.finally(() => {
      pendingSavesRef.current = pendingSavesRef.current.filter(p => p !== savePromise)
    })
  }

  const moveToNext = () => {
    const currentIdx = currentIndexRef.current
    const nextIndex = currentIdx + 1

    if (nextIndex >= questions.length) {
      completeSession()
      return
    }

    const nextQuestion = questions[nextIndex]

    currentIndexRef.current = nextIndex
    currentQuestionRef.current = nextQuestion
    isProcessingAnswerRef.current = false
    hasSpokenForCurrentQuestionRef.current = false

    const startTime = Date.now()
    questionStartTimeRef.current = startTime

    setCurrentIndex(nextIndex)
    setCurrentQuestion(nextQuestion)
    setQuestionStartTime(startTime)
    setIsProcessingAnswer(false)
    setIsAnswering(true)
  }

  const completeSession = async () => {
    if (!session) return

    setPhase('completed')
    setIsAnswering(false)

    // Wait for any in-flight response saves to finish
    if (pendingSavesRef.current.length > 0) {
      await Promise.allSettled(pendingSavesRef.current)
    }

    try {
      const data = await apiClient.put<Record<string, unknown>>(
        `/api/life-words/question-sessions/${session.id}/complete`
      )
      setStatistics(data.statistics)
    } catch (error) {
      console.error('Error completing session:', error)
    }
  }

  const handleDone = () => {
    router.push('/dashboard/treatments/life-words')
  }

  // ==================== RENDER ====================

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-[var(--color-primary)] mx-auto mb-4"></div>
          <p className="text-xl text-gray-700">Starting question session...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="bg-red-50 border-2 border-red-300 rounded-lg p-8 max-w-2xl">
          <h4 className="text-2xl font-bold text-red-900 mb-4">Error</h4>
          <p className="text-xl text-red-700 mb-6">{error}</p>
          <button
            className="bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-bold py-4 px-8 rounded-lg text-xl"
            onClick={() => router.push('/dashboard/treatments/life-words')}
          >
            Go Back
          </button>
        </div>
      </div>
    )
  }

  // ==================== STUDY PHASE UI ====================
  if (phase === 'study' && questions.length > 0) {
    const currentStudyQuestion = questions[studyIndex]
    const isLastStudyItem = studyIndex === questions.length - 1

    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-8">
        {/* Phase indicator */}
        <div className="mb-6">
          <span className="bg-purple-100 text-purple-800 px-6 py-2 rounded-full text-xl font-semibold">
            Study Phase - Learn the Answers
          </span>
        </div>

        {/* Progress indicator */}
        <div className="flex gap-2 mb-6">
          {questions.map((_, idx) => (
            <div
              key={idx}
              className={`w-3 h-3 rounded-full transition-colors ${
                idx < studyIndex
                  ? 'bg-purple-500'
                  : idx === studyIndex
                  ? 'bg-purple-600 ring-2 ring-purple-300'
                  : 'bg-gray-300'
              }`}
            />
          ))}
        </div>

        {/* Question type badge */}
        <div className="mb-4">
          <span className="bg-blue-100 text-blue-800 px-4 py-2 rounded-full text-lg font-semibold">
            {QUESTION_TYPE_NAMES[currentStudyQuestion.question_type]}
          </span>
        </div>

        {/* Contact photo (not for question type 5) */}
        {currentStudyQuestion.question_type !== 5 && (
          <div className="relative w-48 h-48 md:w-64 md:h-64 rounded-lg overflow-hidden shadow-lg mb-6 border-4 border-purple-200">
            <Image
              src={currentStudyQuestion.contact_photo_url}
              alt="Contact"
              fill
              className="object-cover"
            />
          </div>
        )}

        {/* Question */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-4 max-w-2xl">
          <p className="text-2xl md:text-3xl text-gray-800 text-center font-medium">
            {currentStudyQuestion.question_text}
          </p>
        </div>

        {/* Answer (highlighted) */}
        <div className="bg-green-50 border-2 border-green-300 rounded-lg p-6 mb-8 max-w-2xl">
          <p className="text-lg text-green-700 text-center mb-2">The answer is:</p>
          <p className="text-3xl md:text-4xl text-green-800 text-center font-bold">
            {currentStudyQuestion.expected_answer}
          </p>
        </div>

        {/* Navigation */}
        <div className="flex gap-4">
          <button
            onClick={handleStudyNext}
            className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-4 px-12 rounded-lg text-2xl transition-colors"
          >
            {isLastStudyItem ? "I'm Ready - Start Quiz" : 'Next'}
          </button>
        </div>

        {/* Back */}
        <div className="mt-4">
          <button
            onClick={handleDone}
            className="text-gray-500 hover:text-gray-700 underline text-lg"
          >
            ← Back
          </button>
        </div>
      </div>
    )
  }

  // ==================== COMPLETED PHASE UI ====================
  if (phase === 'completed') {
    const totalCorrect = responses.filter(r => r.is_correct).length
    const totalPartial = responses.filter(r => r.is_partial && !r.is_correct).length
    const avgResponseTime = responses.length > 0
      ? Math.round(responses.reduce((sum, r) => sum + r.response_time, 0) / responses.length)
      : 0

    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="text-center max-w-2xl">
          <h2 className="text-4xl font-bold text-green-600 mb-6">Session Complete!</h2>

          <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
            <h3 className="text-2xl font-bold mb-6 text-gray-900">Your Results</h3>

            <div className="grid grid-cols-2 gap-6 mb-6">
              <div className="bg-green-50 rounded-lg p-4">
                <div className="text-4xl font-bold text-green-600">{totalCorrect}</div>
                <div className="text-gray-600">Correct</div>
              </div>
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="text-4xl font-bold text-blue-600">{questions.length}</div>
                <div className="text-gray-600">Total Questions</div>
              </div>
              <div className="bg-amber-50 rounded-lg p-4">
                <div className="text-4xl font-bold text-amber-600">{totalPartial}</div>
                <div className="text-gray-600">Partial Correct</div>
              </div>
              <div className="bg-purple-50 rounded-lg p-4">
                <div className="text-4xl font-bold text-purple-600">
                  {avgResponseTime > 0 ? `${(avgResponseTime / 1000).toFixed(1)}s` : '-'}
                </div>
                <div className="text-gray-600">Avg Response Time</div>
              </div>
            </div>

            <div className="text-left">
              <h4 className="text-lg font-bold mb-3 text-gray-900">By Question Type:</h4>
              <div className="space-y-2">
                {Object.entries(QUESTION_TYPE_NAMES).map(([type, name]) => {
                  const typeResponses = responses.filter(r => r.question_type === parseInt(type))
                  const typeCorrect = typeResponses.filter(r => r.is_correct).length
                  return (
                    <div key={type} className="flex justify-between items-center bg-gray-50 p-2 rounded">
                      <span className="text-gray-700">{name}</span>
                      <span className={`font-bold ${typeCorrect > 0 ? 'text-green-600' : 'text-gray-400'}`}>
                        {typeCorrect}/{typeResponses.length}
                      </span>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>

          <button
            onClick={handleDone}
            className="bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-bold py-4 px-8 rounded-lg text-xl"
          >
            Done
          </button>
        </div>
      </div>
    )
  }

  // ==================== QUIZ PHASE UI ====================
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8">
      {/* Phase indicator */}
      <div className="mb-6">
        <span className="bg-blue-100 text-blue-800 px-6 py-2 rounded-full text-xl font-semibold">
          Quiz Phase - Answer the Questions
        </span>
      </div>

      {/* Progress indicator */}
      <div className="flex gap-2 mb-6">
        {questions.map((_, idx) => (
          <div
            key={idx}
            className={`w-3 h-3 rounded-full transition-colors ${
              idx < currentIndex
                ? responses[idx]?.is_correct
                  ? 'bg-green-500'
                  : 'bg-red-400'
                : idx === currentIndex
                ? 'bg-[var(--color-primary)]'
                : 'bg-gray-300'
            }`}
          />
        ))}
      </div>

      {/* Question type badge */}
      {currentQuestion && (
        <div className="mb-4">
          <span className="bg-blue-100 text-blue-800 px-4 py-2 rounded-full text-lg font-semibold">
            {QUESTION_TYPE_NAMES[currentQuestion.question_type]}
          </span>
        </div>
      )}

      {currentQuestion && (
        <>
          {/* Contact photo for visual context (not for Question 5 - name recall) */}
          {currentQuestion.question_type !== 5 && (
            <div className="relative w-48 h-48 md:w-64 md:h-64 rounded-lg overflow-hidden shadow-lg mb-6 border-4 border-gray-200">
              <Image
                src={currentQuestion.contact_photo_url}
                alt="Contact"
                fill
                className="object-cover"
              />
            </div>
          )}

          {/* Question text */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6 max-w-2xl">
            <p className="text-2xl md:text-3xl text-gray-800 text-center font-medium">
              {currentQuestion.question_text}
            </p>
          </div>

          {/* Feedback display */}
          {showFeedback && lastResult && (
            <div
              className={`rounded-lg p-6 mb-6 max-w-xl ${
                lastResult.isCorrect
                  ? 'bg-green-50 border-2 border-green-300'
                  : 'bg-amber-50 border-2 border-amber-300'
              }`}
            >
              <div className="text-center">
                {lastResult.isCorrect ? (
                  <div className="text-green-700">
                    <span className="text-4xl mb-2 block">✓</span>
                    <p className="text-xl font-bold">
                      {lastResult.isPartial ? 'Partial Match!' : 'Correct!'}
                    </p>
                    <p className="text-lg mt-2">You said: &quot;{lastResult.userAnswer}&quot;</p>
                  </div>
                ) : showCue && currentCue ? (
                  // Show cue instead of answer (showCue is true when hint is being offered)
                  <div className="text-amber-800">
                    <span className="text-4xl mb-2 block">💡</span>
                    <p className="text-xl font-bold">Here&apos;s a hint</p>
                    <p className="text-lg mt-2">You said: &quot;{lastResult.userAnswer}&quot;</p>
                    <p className="text-lg mt-3 italic bg-amber-100 p-3 rounded-lg">
                      {currentCue}
                    </p>
                    <p className="text-base mt-4 text-gray-600">
                      Try again! ({MAX_CUES - cueLevel + 1} {MAX_CUES - cueLevel + 1 === 1 ? 'hint' : 'hints'} remaining)
                    </p>
                  </div>
                ) : (
                  // Max cues reached or no cue - reveal answer
                  <div className="text-amber-800">
                    <span className="text-4xl mb-2 block">~</span>
                    <p className="text-xl font-bold">The answer was:</p>
                    <p className="text-2xl mt-2 font-bold text-[var(--color-primary)]">
                      {lastResult.expectedAnswer}
                    </p>
                    <p className="text-base mt-3 text-gray-600">You said: &quot;{lastResult.userAnswer}&quot;</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Show current cue when answering (after hint given) */}
          {showCue && currentCue && isAnswering && !showFeedback && (
            <div className="bg-blue-50 border-2 border-blue-300 rounded-lg p-4 mb-6 max-w-xl">
              <div className="text-center">
                <span className="text-2xl mr-2">💡</span>
                <span className="text-lg text-blue-800 italic">{currentCue}</span>
              </div>
            </div>
          )}

          {/* Speech input or waiting */}
          {isAnswering && !showFeedback ? (
            <div className="flex flex-col items-center gap-4">
              <p className="text-lg text-gray-600 mb-2">Listen to the question, then speak your answer</p>
              <SpeechRecognitionButton
                key={`speech-${currentIndex}-${cueLevel}`}
                onResult={handleAnswer}
                disabled={isProcessingAnswer}
                resetTrigger={currentIndex}
                autoStart={true}
                onStartListening={async () => {
                  if (!hasSpokenForCurrentQuestionRef.current) {
                    hasSpokenForCurrentQuestionRef.current = true
                    try {
                      const questionText = currentQuestionRef.current?.question_text || ''
                      const isFirstQuestion = currentIndexRef.current === 0
                      const prompt = isFirstQuestion
                        ? "Now let's see what you remember. " + questionText
                        : questionText
                      await speak(prompt, { gender: voiceGender })
                      await new Promise(resolve => setTimeout(resolve, 1000))
                    } catch (error) {
                      console.warn('Failed to speak question:', error)
                    }
                  }
                }}
              />
            </div>
          ) : !showFeedback && (
            <div className="text-center">
              <p className="text-xl text-gray-600">Processing...</p>
            </div>
          )}

          {/* Done button */}
          <div className="mt-12">
            <button
              onClick={handleDone}
              className="text-gray-500 hover:text-gray-700 underline text-lg"
            >
              Done for now
            </button>
          </div>
        </>
      )}
    </div>
  )
}
