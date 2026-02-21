'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { createClient } from '@/lib/supabase'
import SpeechRecognitionButton from '@/components/shared/SpeechRecognitionButton'
import { speak, waitForVoices } from '@/lib/utils/textToSpeech'
import { useVoicePreference } from '@/hooks/useVoicePreference'
import { getRandomPositiveFeedback } from '@/lib/utils/positiveFeedback'
import { evaluateInformationAnswer } from '@/lib/api/matching'
import { apiClient } from '@/lib/api/client'

interface InformationItem {
  field_name: string
  field_label: string
  teach_text: string // TTS version with pronunciation/formatting
  display_text: string // Display version with actual values
  question_text: string
  expected_answer: string
  hint_text: string
}

interface InformationSession {
  id: string
  user_id: string
  is_completed: boolean
  total_items: number
  total_correct: number
  total_hints_used: number
  total_timeouts: number
}

interface ResponseRecord {
  field_name: string
  is_correct: boolean
  used_hint: boolean
  timed_out: boolean
  response_time: number
}

// Session phases
type SessionPhase = 'ready' | 'teach' | 'quiz' | 'hint' | 'reveal' | 'completed'

const TIMEOUT_MS = 30000 // 30 seconds

export default function InformationPracticeSessionPage() {
  const router = useRouter()
  const params = useParams()
  const sessionId = params.id as string
  const supabase = createClient()
  const voiceGender = useVoicePreference()

  // Session state
  const [session, setSession] = useState<InformationSession | null>(null)
  const [items, setItems] = useState<InformationItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Phase state - start with 'ready' to require user click (browser autoplay policy)
  const [phase, setPhase] = useState<SessionPhase>('ready')
  const [currentIndex, setCurrentIndex] = useState(0)
  const [currentItem, setCurrentItem] = useState<InformationItem | null>(null)
  const [teachingSpoken, setTeachingSpoken] = useState(false)

  // Quiz state
  const [isAnswering, setIsAnswering] = useState(false)
  const [isProcessingAnswer, setIsProcessingAnswer] = useState(false)
  const [showFeedback, setShowFeedback] = useState(false)
  const [lastResult, setLastResult] = useState<{
    isCorrect: boolean
    userAnswer: string
    expectedAnswer: string
  } | null>(null)
  const [responses, setResponses] = useState<ResponseRecord[]>([])
  const [, setQuestionStartTime] = useState<number>(0)
  const [usedHintForCurrent, setUsedHintForCurrent] = useState(false)
  const [, setTimedOutForCurrent] = useState(false)

  // Refs for async callbacks
  const isProcessingAnswerRef = useRef(false)
  const isTeachingSpeakingRef = useRef(false)
  const currentItemRef = useRef<InformationItem | null>(null)
  const currentIndexRef = useRef(0)
  const questionStartTimeRef = useRef(0)
  const timeoutRef = useRef<NodeJS.Timeout | null>(null)
  const phaseRef = useRef<SessionPhase>('teach')

  const initializeSession = useCallback(async () => {
    try {
      setLoading(true)

      const { data: { user } } = await supabase.auth.getUser()
      if (!user) {
        router.push('/login')
        return
      }

      // Get the session data
      const sessionData = await apiClient.get<Record<string, unknown>>(
        `/api/life-words/information-sessions/${sessionId}`
      )
      setSession(sessionData.session as InformationSession)

      // If session has existing responses, it might be resumed
      if (sessionData.responses && (sessionData.responses as unknown[]).length > 0) {
        setResponses((sessionData.responses as Record<string, unknown>[]).map((r) => ({
          field_name: r.field_name as string,
          is_correct: r.is_correct as boolean,
          used_hint: r.used_hint as boolean,
          timed_out: r.timed_out as boolean,
          response_time: (r.response_time as number) || 0
        })))
      }

      // Get user profile to regenerate items (items are generated dynamically from profile)
      try {
        const profile = await apiClient.get<Record<string, unknown>>('/api/profile')
        const generatedItems = generateItemsFromProfile(profile)

        if (generatedItems.length > 0) {
          setItems(generatedItems)
          setCurrentItem(generatedItems[0])
          currentItemRef.current = generatedItems[0]
          setPhase('ready')
          phaseRef.current = 'ready'
        } else {
          setError('Not enough profile information to practice. Please fill in more fields in My Info.')
        }
      } catch (profileError) {
        console.error('Error loading profile:', profileError)
        setError('Failed to load profile information')
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
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [initializeSession])

  // Generate items from user profile (mirrors backend logic)
  const generateItemsFromProfile = (profile: Record<string, unknown>): InformationItem[] => {
    const PRACTICE_FIELDS: Record<string, { label: string; teachTemplate: string; question: string; hintType: string }> = {
      phone_number: { label: 'phone number', teachTemplate: 'Your phone number is {value}', question: 'What is your phone number?', hintType: 'first_digit' },
      address_city: { label: 'city', teachTemplate: 'You live in {value}', question: 'What city do you live in?', hintType: 'first_letter' },
      address_state: { label: 'state', teachTemplate: 'You live in the state of {value}', question: 'What state do you live in?', hintType: 'first_letter' },
      address_zip: { label: 'zip code', teachTemplate: 'Your zip code is {value}', question: 'What is your zip code?', hintType: 'first_digit' },
      date_of_birth: { label: 'birthday', teachTemplate: 'Your birthday is {value}', question: 'When is your birthday?', hintType: 'first_letter' },
      full_name: { label: 'full name', teachTemplate: 'Your full name is {value}', question: 'What is your full name?', hintType: 'first_letter' },
      job: { label: 'job', teachTemplate: 'Your job is {value}', question: 'What is your job?', hintType: 'first_letter' },
      marital_status: { label: 'marital status', teachTemplate: 'Your marital status is {value}', question: 'What is your marital status?', hintType: 'first_letter' },
      number_of_children: { label: 'number of children', teachTemplate: 'You have {value} children', question: 'How many children do you have?', hintType: 'first_digit' },
      favorite_food: { label: 'favorite food', teachTemplate: 'Your favorite food is {value}', question: 'What is your favorite food?', hintType: 'first_letter' },
      favorite_music: { label: 'favorite music', teachTemplate: 'Your favorite music is {value}', question: 'What is your favorite music?', hintType: 'first_letter' },
      hair_color: { label: 'hair color', teachTemplate: 'Your hair color is {value}', question: 'What is your hair color?', hintType: 'first_letter' },
      eye_color: { label: 'eye color', teachTemplate: 'Your eye color is {value}', question: 'What is your eye color?', hintType: 'first_letter' },
    }

    const formatDate = (dateValue: unknown): string => {
      if (!dateValue) return ''
      try {
        const date = new Date(dateValue as string | number)
        return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric' })
      } catch {
        return String(dateValue)
      }
    }

    const formatPhoneForTTS = (phone: string): string => {
      const digits = String(phone).replace(/\D/g, '')
      if (digits.length === 10) {
        // Format as spaced digits for TTS: "2 4 8, 7 2 2, 3 4 2 8"
        return `${digits[0]} ${digits[1]} ${digits[2]}, ${digits[3]} ${digits[4]} ${digits[5]}, ${digits[6]} ${digits[7]} ${digits[8]} ${digits[9]}`
      } else if (digits.length === 7) {
        return `${digits[0]} ${digits[1]} ${digits[2]}, ${digits[3]} ${digits[4]} ${digits[5]} ${digits[6]}`
      }
      return digits.split('').join(' ')
    }

    const formatZipForTTS = (zip: string): string => {
      const digits = String(zip).replace(/\D/g, '')
      return digits.split('').join(' ')
    }

    // US State abbreviation to full name mapping
    const STATE_ABBREVIATIONS: Record<string, string> = {
      "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
      "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
      "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
      "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
      "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
      "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
      "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
      "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
      "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
      "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
      "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
      "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
      "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia",
    }

    const formatStateForTTS = (state: string): string => {
      const stateUpper = String(state).trim().toUpperCase()
      return STATE_ABBREVIATIONS[stateUpper] || state
    }

    const generateHint = (value: string, hintType: string): string => {
      if (!value) return ''
      const valueStr = String(value).trim()
      if (hintType === 'first_letter') {
        return `It starts with the letter ${valueStr[0]?.toUpperCase() || ''}`
      } else if (hintType === 'first_digit') {
        const firstDigit = valueStr.match(/\d/)?.[0]
        if (firstDigit) return `The first digit is ${firstDigit}`
        return `It starts with ${valueStr[0] || ''}`
      }
      return `The first character is ${valueStr[0] || ''}`
    }

    const filledFields: { fieldName: string; config: typeof PRACTICE_FIELDS[string]; value: unknown }[] = []
    for (const [fieldName, config] of Object.entries(PRACTICE_FIELDS)) {
      const value = profile[fieldName]
      if (value !== null && value !== undefined && String(value).trim()) {
        filledFields.push({ fieldName, config, value })
      }
    }

    // Shuffle and pick up to 5
    const shuffled = filledFields.sort(() => Math.random() - 0.5).slice(0, 5)

    return shuffled.map(({ fieldName, config, value }) => {
      const displayValue = fieldName === 'date_of_birth' ? formatDate(value) : String(value)
      // Format for TTS (spoken version - digits read individually, abbreviations expanded)
      let ttsValue = displayValue
      if (fieldName === 'phone_number') {
        ttsValue = formatPhoneForTTS(String(value))
      } else if (fieldName === 'address_zip') {
        ttsValue = formatZipForTTS(String(value))
      } else if (fieldName === 'address_state') {
        ttsValue = formatStateForTTS(String(value))
      } else if (fieldName === 'full_name') {
        // Use pronunciation if available
        const pronunciation = profile.full_name_pronunciation
        if (pronunciation && String(pronunciation).trim()) {
          ttsValue = String(pronunciation)
        }
      }
      const hintValue = fieldName === 'date_of_birth' ? displayValue.split(' ')[0] || displayValue : displayValue
      return {
        field_name: fieldName,
        field_label: config.label,
        teach_text: config.teachTemplate.replace('{value}', ttsValue),
        display_text: config.teachTemplate.replace('{value}', displayValue),
        question_text: config.question,
        expected_answer: displayValue,
        hint_text: generateHint(hintValue, config.hintType),
      }
    })
  }

  // Ref to store items for use in callbacks without causing re-renders
  const itemsRef = useRef<InformationItem[]>([])
  useEffect(() => {
    itemsRef.current = items
  }, [items])

  const handleTimeoutRef = useRef<() => void>(() => {})

  // Handle timeout for quiz phase (defined before teaching useEffect to avoid reference error)
  const startTimeoutTimer = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }
    timeoutRef.current = setTimeout(() => {
      if (phaseRef.current === 'quiz' || phaseRef.current === 'hint') {
        handleTimeoutRef.current()
      }
    }, TIMEOUT_MS)
  }, [])

  // Handle teaching phase - speak item and auto-advance
  useEffect(() => {
    // Only run when in teach phase, not loading, and haven't spoken yet
    if (phase !== 'teach' || loading || teachingSpoken) return
    if (itemsRef.current.length === 0) return

    // Prevent concurrent speech
    if (isTeachingSpeakingRef.current) return

    // Helper to speak with retry
    const speakWithRetry = async (text: string, maxRetries = 2): Promise<boolean> => {
      for (let attempt = 0; attempt <= maxRetries; attempt++) {
        try {
          await speak(text, { gender: voiceGender })
          return true
        } catch (error: unknown) {
          const msg = error instanceof Error ? error.message : error
          console.warn(`Speech attempt ${attempt + 1} failed:`, msg)
          if (attempt < maxRetries) {
            // Brief delay before retry
            await new Promise(resolve => setTimeout(resolve, 200))
          }
        }
      }
      return false
    }

    const speakAndAdvance = async () => {
      // Double-check we're not already speaking
      if (isTeachingSpeakingRef.current) return
      isTeachingSpeakingRef.current = true
      setTeachingSpoken(true)

      const currentIdx = currentIndexRef.current
      const allItems = itemsRef.current
      const item = allItems[currentIdx]

      if (!item) {
        isTeachingSpeakingRef.current = false
        return
      }

      try {
        await waitForVoices()
        const speechSucceeded = await speakWithRetry(item.teach_text)

        // Wait a moment to let user hear and process (longer if speech failed so they can read)
        await new Promise(resolve => setTimeout(resolve, speechSucceeded ? 2500 : 3500))

        // Move to next item or switch to quiz
        const nextIndex = currentIdx + 1
        if (nextIndex >= allItems.length) {
          // Teaching complete, start quiz phase
          await speakWithRetry("Now let's see what you remember!")
          await new Promise(resolve => setTimeout(resolve, 1500))

          // Reset to first item for quiz
          isTeachingSpeakingRef.current = false
          setCurrentIndex(0)
          currentIndexRef.current = 0
          setCurrentItem(allItems[0])
          currentItemRef.current = allItems[0]
          setPhase('quiz')
          phaseRef.current = 'quiz'
          setIsAnswering(true)
          setUsedHintForCurrent(false)
          setTimedOutForCurrent(false)

          const startTime = Date.now()
          setQuestionStartTime(startTime)
          questionStartTimeRef.current = startTime

          // Speak the first question
          await speakWithRetry(allItems[0].question_text)
          startTimeoutTimer()
        } else {
          // Move to next teaching item
          isTeachingSpeakingRef.current = false
          setCurrentIndex(nextIndex)
          currentIndexRef.current = nextIndex
          setCurrentItem(allItems[nextIndex])
          currentItemRef.current = allItems[nextIndex]
          setTeachingSpoken(false)
        }
      } catch (error: unknown) {
        const msg = error instanceof Error ? error.message : error
        console.warn('Teaching phase failed:', msg)
        isTeachingSpeakingRef.current = false

        // Wait so user can read the text on screen
        await new Promise(resolve => setTimeout(resolve, 3500))

        // Advance even if speech fails
        const nextIndex = currentIdx + 1
        const allItems = itemsRef.current
        if (nextIndex >= allItems.length) {
          setCurrentIndex(0)
          currentIndexRef.current = 0
          setCurrentItem(allItems[0])
          currentItemRef.current = allItems[0]
          setPhase('quiz')
          phaseRef.current = 'quiz'
          setIsAnswering(true)
          setUsedHintForCurrent(false)
          setTimedOutForCurrent(false)

          const startTime = Date.now()
          setQuestionStartTime(startTime)
          questionStartTimeRef.current = startTime
          startTimeoutTimer()
        } else {
          setCurrentIndex(nextIndex)
          currentIndexRef.current = nextIndex
          setCurrentItem(allItems[nextIndex])
          currentItemRef.current = allItems[nextIndex]
          setTeachingSpoken(false)
        }
      }
    }

    // Delay before speaking to let UI render
    const timer = setTimeout(speakAndAdvance, 800)
    return () => clearTimeout(timer)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [phase, loading, teachingSpoken, voiceGender, items.length])

  // Handle start button click - user interaction unlocks audio
  const handleStartLearning = async () => {
    if (items.length === 0) return

    // Set phase to teach (will trigger the useEffect)
    setPhase('teach')
    phaseRef.current = 'teach'

    // Speak the first item immediately (user-initiated, bypasses autoplay policy)
    isTeachingSpeakingRef.current = true
    setTeachingSpoken(true)

    // Helper to speak with retry (inline for user-initiated context)
    const speakWithRetry = async (text: string, maxRetries = 2): Promise<boolean> => {
      for (let attempt = 0; attempt <= maxRetries; attempt++) {
        try {
          await speak(text, { gender: voiceGender })
          return true
        } catch (error: unknown) {
          const msg = error instanceof Error ? error.message : error
          console.warn(`Speech attempt ${attempt + 1} failed:`, msg)
          if (attempt < maxRetries) {
            await new Promise(resolve => setTimeout(resolve, 200))
          }
        }
      }
      return false
    }

    const item = items[0]
    try {
      await waitForVoices()
      const speechSucceeded = await speakWithRetry(item.teach_text)

      // Wait a moment then advance (longer if speech failed)
      await new Promise(resolve => setTimeout(resolve, speechSucceeded ? 2500 : 3500))

      const nextIndex = 1
      if (nextIndex >= items.length) {
        // Only one item, go to quiz
        await speakWithRetry("Now let's see what you remember!")
        await new Promise(resolve => setTimeout(resolve, 1500))

        isTeachingSpeakingRef.current = false
        setCurrentIndex(0)
        currentIndexRef.current = 0
        setCurrentItem(items[0])
        currentItemRef.current = items[0]
        setPhase('quiz')
        phaseRef.current = 'quiz'
        setIsAnswering(true)

        const startTime = Date.now()
        setQuestionStartTime(startTime)
        questionStartTimeRef.current = startTime
        await speakWithRetry(items[0].question_text)
        startTimeoutTimer()
      } else {
        // Move to next item
        isTeachingSpeakingRef.current = false
        setCurrentIndex(nextIndex)
        currentIndexRef.current = nextIndex
        setCurrentItem(items[nextIndex])
        currentItemRef.current = items[nextIndex]
        setTeachingSpoken(false) // This will trigger the useEffect for auto-advance
      }
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : error
      console.warn('Start learning speech failed:', msg)
      isTeachingSpeakingRef.current = false
      // Still advance after a delay so user can read
      await new Promise(resolve => setTimeout(resolve, 3500))
      setCurrentIndex(1)
      currentIndexRef.current = 1
      if (items[1]) {
        setCurrentItem(items[1])
        currentItemRef.current = items[1]
      }
      setTeachingSpoken(false)
    }
  }

  // ==================== TEACH PHASE ====================
  // Teaching is handled by the useEffect above - auto-speak and auto-advance

  // ==================== QUIZ PHASE ====================

  const handleAnswer = async (transcript: string) => {
    const currentItemVal = currentItemRef.current
    const isProcessing = isProcessingAnswerRef.current
    const startTime = questionStartTimeRef.current

    if (!currentItemVal || !session || isProcessing) {
      return
    }

    // Clear timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }

    setIsProcessingAnswer(true)
    isProcessingAnswerRef.current = true

    try {
      const responseTime = Date.now() - startTime
      let result: { is_correct: boolean; confidence: number }
      try {
        result = await evaluateInformationAnswer(
          transcript,
          currentItemVal.expected_answer,
          currentItemVal.field_name
        )
      } catch (error) {
        console.warn('Matching API error, treating as incorrect:', error)
        result = { is_correct: false, confidence: 0 }
      }

      // Show feedback
      setLastResult({
        isCorrect: result.is_correct,
        userAnswer: transcript,
        expectedAnswer: currentItemVal.expected_answer
      })
      setShowFeedback(true)
      setIsAnswering(false)

      if (result.is_correct) {
        // Correct answer - save and move on
        await saveResponse(currentItemVal, transcript, true, responseTime, usedHintForCurrent, false)
        const feedback = getRandomPositiveFeedback()
        await speak(feedback, { gender: voiceGender })

        // Move to next after delay
        setTimeout(() => {
          setShowFeedback(false)
          moveToNext()
        }, 3000)
      } else {
        // Wrong answer
        if (!usedHintForCurrent) {
          // Give hint
          setUsedHintForCurrent(true)
          setPhase('hint')
          phaseRef.current = 'hint'

          await speak(`Not quite. Here's a hint: ${currentItemVal.hint_text}. Try again.`, { gender: voiceGender })

          // Allow retry
          setTimeout(() => {
            setShowFeedback(false)
            setIsAnswering(true)
            setIsProcessingAnswer(false)
            isProcessingAnswerRef.current = false
            startTimeoutTimer()
          }, 4000)
        } else {
          // Already used hint - reveal answer
          setPhase('reveal')
          phaseRef.current = 'reveal'

          await saveResponse(currentItemVal, transcript, false, responseTime, true, false)
          await speak(`The answer was ${currentItemVal.expected_answer}`, { gender: voiceGender })

          // Move to next after delay
          setTimeout(() => {
            setShowFeedback(false)
            moveToNext()
          }, 4000)
        }
      }
    } catch (err) {
      console.error('Error handling answer:', err)
      setIsProcessingAnswer(false)
      isProcessingAnswerRef.current = false
    }
  }

  const saveResponse = async (
    item: InformationItem,
    userAnswer: string,
    isCorrect: boolean,
    responseTime: number,
    usedHint: boolean,
    timedOut: boolean
  ) => {
    if (!session) return

    try {
      await apiClient.post(
        `/api/life-words/information-sessions/${session.id}/responses`,
        {
          field_name: item.field_name,
          field_label: item.field_label,
          teach_text: item.teach_text,
          question_text: item.question_text,
          expected_answer: item.expected_answer,
          hint_text: item.hint_text,
          user_answer: userAnswer,
          is_correct: isCorrect,
          used_hint: usedHint,
          timed_out: timedOut,
          response_time: responseTime,
        }
      )

      // Track locally
      setResponses(prev => [...prev, {
        field_name: item.field_name,
        is_correct: isCorrect,
        used_hint: usedHint,
        timed_out: timedOut,
        response_time: responseTime
      }])
    } catch (error) {
      console.error('Error saving response:', error)
    }
  }

  const moveToNext = async () => {
    const currentIdx = currentIndexRef.current
    const nextIndex = currentIdx + 1

    if (nextIndex >= items.length) {
      completeSession()
      return
    }

    const nextItem = items[nextIndex]

    currentIndexRef.current = nextIndex
    currentItemRef.current = nextItem
    isProcessingAnswerRef.current = false

    const startTime = Date.now()
    questionStartTimeRef.current = startTime

    setCurrentIndex(nextIndex)
    setCurrentItem(nextItem)
    setQuestionStartTime(startTime)
    setIsProcessingAnswer(false)
    setIsAnswering(true)
    setUsedHintForCurrent(false)
    setTimedOutForCurrent(false)
    setPhase('quiz')
    phaseRef.current = 'quiz'

    try {
      await speak(nextItem.question_text, { gender: voiceGender })
    } catch (speakError: unknown) {
      const msg = speakError instanceof Error ? speakError.message : speakError
      console.warn('Text-to-speech failed:', msg)
    }

    startTimeoutTimer()
  }

  const handleTimeout = async () => {
    const currentItemVal = currentItemRef.current
    if (!currentItemVal || !session) return

    setTimedOutForCurrent(true)
    setIsAnswering(false)

    await saveResponse(currentItemVal, '', false, TIMEOUT_MS, usedHintForCurrent, true)

    try {
      await speak(`Time's up. ${currentItemVal.teach_text}`, { gender: voiceGender })
    } catch (e) {
      console.warn('TTS failed:', e)
    }

    setLastResult({
      isCorrect: false,
      userAnswer: '(no response)',
      expectedAnswer: currentItemVal.expected_answer
    })
    setShowFeedback(true)
    setPhase('reveal')
    phaseRef.current = 'reveal'

    setTimeout(() => {
      setShowFeedback(false)
      moveToNext()
    }, 5000)
  }

  handleTimeoutRef.current = handleTimeout

  const completeSession = async () => {
    if (!session) return

    // Clear any pending timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }

    setPhase('completed')
    phaseRef.current = 'completed'
    setIsAnswering(false)

    try {
      await apiClient.put(`/api/life-words/information-sessions/${session.id}/complete`)
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
          <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-teal-600 mx-auto mb-4"></div>
          <p className="text-xl text-gray-700">Starting information practice...</p>
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

  // ==================== READY PHASE UI ====================
  if (phase === 'ready' && items.length > 0) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-8">
        <div className="text-center max-w-2xl">
          <h2 className="text-4xl font-bold text-teal-600 mb-6">Information Practice</h2>
          <p className="text-xl text-gray-700 mb-8">
            You&apos;ll learn to provide personal information to others.
          </p>

          <div className="bg-teal-50 border-2 border-teal-200 rounded-lg p-6 mb-8">
            <p className="text-lg text-teal-800">
              Listen carefully as each item is read aloud. The quiz will follow!
            </p>
          </div>

          <button
            onClick={handleStartLearning}
            className="bg-teal-600 hover:bg-teal-700 text-white font-bold py-4 px-12 rounded-lg text-2xl transition-colors"
          >
            Start Learning
          </button>

          <div className="mt-6">
            <button
              onClick={handleDone}
              className="text-gray-500 hover:text-gray-700 underline text-lg"
            >
              Done for now
            </button>
          </div>
        </div>
      </div>
    )
  }

  // ==================== TEACH PHASE UI ====================
  if (phase === 'teach' && items.length > 0 && currentItem) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-8">
        {/* Phase indicator */}
        <div className="mb-6">
          <span className="bg-teal-100 text-teal-800 px-6 py-2 rounded-full text-xl font-semibold">
            Teaching Phase - Learn Your Information
          </span>
        </div>

        {/* Progress indicator */}
        <div className="flex gap-2 mb-6">
          {items.map((_, idx) => (
            <div
              key={idx}
              className={`w-3 h-3 rounded-full transition-colors ${
                idx < currentIndex
                  ? 'bg-teal-500'
                  : idx === currentIndex
                  ? 'bg-teal-600 ring-2 ring-teal-300'
                  : 'bg-gray-300'
              }`}
            />
          ))}
        </div>

        {/* Field label badge */}
        <div className="mb-4">
          <span className="bg-blue-100 text-blue-800 px-4 py-2 rounded-full text-lg font-semibold capitalize">
            {currentItem.field_label}
          </span>
        </div>

        {/* Teach text (display version - actual values, not TTS formatting) */}
        <div className="bg-teal-50 border-2 border-teal-300 rounded-lg p-8 mb-8 max-w-2xl">
          <p className="text-3xl md:text-4xl text-teal-800 text-center font-medium">
            {currentItem.display_text}
          </p>
        </div>

        {/* Auto-advance indicator */}
        <div className="flex flex-col items-center gap-2 mb-4">
          <div className="flex items-center gap-3">
            <div className="animate-pulse w-3 h-3 bg-teal-500 rounded-full"></div>
            <p className="text-lg text-gray-600">
              {currentIndex < items.length - 1
                ? `Item ${currentIndex + 1} of ${items.length} - Listen and remember...`
                : `Last item - Quiz starting next...`
              }
            </p>
          </div>
        </div>

        {/* Done for now */}
        <div className="mt-4">
          <button
            onClick={handleDone}
            className="text-gray-500 hover:text-gray-700 underline text-lg"
          >
            Done for now
          </button>
        </div>
      </div>
    )
  }

  // ==================== COMPLETED PHASE UI ====================
  if (phase === 'completed') {
    const totalCorrect = responses.filter(r => r.is_correct).length
    const totalHints = responses.filter(r => r.used_hint).length
    const totalTimeouts = responses.filter(r => r.timed_out).length
    const avgResponseTime = responses.length > 0
      ? Math.round(responses.reduce((sum, r) => sum + r.response_time, 0) / responses.length)
      : 0

    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="text-center max-w-2xl">
          <h2 className="text-4xl font-bold text-teal-600 mb-6">Session Complete!</h2>

          <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
            <h3 className="text-2xl font-bold mb-6 text-gray-900">Your Results</h3>

            <div className="grid grid-cols-2 gap-6 mb-6">
              <div className="bg-green-50 rounded-lg p-4">
                <div className="text-4xl font-bold text-green-600">{totalCorrect}</div>
                <div className="text-gray-600">Correct</div>
              </div>
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="text-4xl font-bold text-blue-600">{items.length}</div>
                <div className="text-gray-600">Total Items</div>
              </div>
              <div className="bg-amber-50 rounded-lg p-4">
                <div className="text-4xl font-bold text-amber-600">{totalHints}</div>
                <div className="text-gray-600">Hints Used</div>
              </div>
              <div className="bg-red-50 rounded-lg p-4">
                <div className="text-4xl font-bold text-red-600">{totalTimeouts}</div>
                <div className="text-gray-600">Timeouts</div>
              </div>
            </div>

            {avgResponseTime > 0 && (
              <div className="bg-purple-50 rounded-lg p-4 mb-6">
                <div className="text-2xl font-bold text-purple-600">
                  {(avgResponseTime / 1000).toFixed(1)}s
                </div>
                <div className="text-gray-600">Average Response Time</div>
              </div>
            )}

            <div className="text-left">
              <h4 className="text-lg font-bold mb-3 text-gray-900">By Field:</h4>
              <div className="space-y-2">
                {responses.map((r, idx) => {
                  const item = items[idx]
                  return (
                    <div key={r.field_name} className="flex justify-between items-center bg-gray-50 p-2 rounded">
                      <span className="text-gray-700 capitalize">{item?.field_label || r.field_name}</span>
                      <span className={`font-bold ${
                        r.is_correct ? 'text-green-600' : r.timed_out ? 'text-red-600' : 'text-amber-600'
                      }`}>
                        {r.is_correct ? 'Correct' : r.timed_out ? 'Timed Out' : 'Incorrect'}
                        {r.used_hint && !r.is_correct && ' (with hint)'}
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

  // ==================== QUIZ/HINT/REVEAL PHASE UI ====================
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8">
      {/* Phase indicator */}
      <div className="mb-6">
        <span className={`px-6 py-2 rounded-full text-xl font-semibold ${
          phase === 'hint'
            ? 'bg-amber-100 text-amber-800'
            : phase === 'reveal'
            ? 'bg-red-100 text-red-800'
            : 'bg-blue-100 text-blue-800'
        }`}>
          {phase === 'hint' ? 'Hint Given - Try Again' :
           phase === 'reveal' ? 'Answer Revealed' :
           'Quiz Phase - Answer the Questions'}
        </span>
      </div>

      {/* Progress indicator */}
      <div className="flex gap-2 mb-6">
        {items.map((_, idx) => (
          <div
            key={idx}
            className={`w-3 h-3 rounded-full transition-colors ${
              idx < currentIndex
                ? responses[idx]?.is_correct
                  ? 'bg-green-500'
                  : 'bg-red-400'
                : idx === currentIndex
                ? 'bg-teal-600'
                : 'bg-gray-300'
            }`}
          />
        ))}
      </div>

      {currentItem && (
        <>
          {/* Field label badge */}
          <div className="mb-4">
            <span className="bg-blue-100 text-blue-800 px-4 py-2 rounded-full text-lg font-semibold capitalize">
              {currentItem.field_label}
            </span>
          </div>

          {/* Question text */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6 max-w-2xl">
            <p className="text-2xl md:text-3xl text-gray-800 text-center font-medium">
              {currentItem.question_text}
            </p>
          </div>

          {/* Hint display (when in hint phase and not showing feedback) */}
          {phase === 'hint' && !showFeedback && (
            <div className="bg-amber-50 border-2 border-amber-300 rounded-lg p-4 mb-6 max-w-xl">
              <div className="text-center">
                <span className="text-2xl mr-2">💡</span>
                <span className="text-lg text-amber-800 italic">{currentItem.hint_text}</span>
              </div>
            </div>
          )}

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
                    <p className="text-xl font-bold">Correct!</p>
                    <p className="text-lg mt-2">You said: &quot;{lastResult.userAnswer}&quot;</p>
                  </div>
                ) : phase === 'hint' ? (
                  <div className="text-amber-800">
                    <span className="text-4xl mb-2 block">💡</span>
                    <p className="text-xl font-bold">Here&apos;s a hint</p>
                    <p className="text-lg mt-2">You said: &quot;{lastResult.userAnswer}&quot;</p>
                    <p className="text-lg mt-3 italic bg-amber-100 p-3 rounded-lg">
                      {currentItem.hint_text}
                    </p>
                    <p className="text-base mt-4 text-gray-600">Try again!</p>
                  </div>
                ) : (
                  <div className="text-amber-800">
                    <span className="text-4xl mb-2 block">~</span>
                    <p className="text-xl font-bold">The answer was:</p>
                    <p className="text-2xl mt-2 font-bold text-teal-700">
                      {lastResult.expectedAnswer}
                    </p>
                    {lastResult.userAnswer !== '(no response)' && (
                      <p className="text-base mt-3 text-gray-600">You said: &quot;{lastResult.userAnswer}&quot;</p>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Speech input or waiting */}
          {isAnswering && !showFeedback ? (
            <div className="flex flex-col items-center gap-4">
              <p className="text-lg text-gray-600 mb-2">
                {phase === 'hint' ? 'Try again - listening for your answer...' : 'Listening for your answer...'}
              </p>
              <SpeechRecognitionButton
                key={`speech-${currentIndex}-${phase}`}
                onResult={handleAnswer}
                disabled={isProcessingAnswer}
                resetTrigger={currentIndex}
                autoStart={true}
              />
              <p className="text-sm text-gray-500 mt-2">
                30 seconds to answer
              </p>
            </div>
          ) : !showFeedback && phase !== 'reveal' && (
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
