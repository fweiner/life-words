'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { createClient } from '@/lib/supabase'
import Image from 'next/image'
import SpeechRecognitionButton from '@/components/shared/SpeechRecognitionButton'
import { PersonalizedCueSystem, getItemPhrase } from '@/components/life-words/PersonalizedCueSystem'
import { speak, waitForVoices } from '@/lib/utils/textToSpeech'
import { useVoicePreference } from '@/hooks/useVoicePreference'
import { getRandomPositiveFeedback } from '@/lib/utils/positiveFeedback'
import { evaluateNameAnswer } from '@/lib/api/matching'
import { apiClient } from '@/lib/api/client'

interface PersonalContact {
  id: string
  name: string
  nickname?: string
  pronunciation?: string  // How to pronounce the name (e.g., "Wyner" for "Weiner")
  relationship: string
  photo_url: string
  first_letter?: string
  category?: string
  description?: string
  association?: string
  location_context?: string
  // Personal characteristics
  interests?: string
  personality?: string
  values?: string
  social_behavior?: string
}

interface Session {
  id: string
  user_id: string
  contact_ids: string[]
  started_at: string
  is_completed: boolean
}

// matchPersonalAnswer is now handled by the backend via evaluateNameAnswer API

export default function LifeWordsSessionPage() {
  const router = useRouter()
  const params = useParams()
  const sessionId = params.id as string
  const supabase = createClient()
  const voiceGender = useVoicePreference()

  const [session, setSession] = useState<Session | null>(null)
  const [contacts, setContacts] = useState<PersonalContact[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [currentContact, setCurrentContact] = useState<PersonalContact | null>(null)
  const [cuesUsed, setCuesUsed] = useState(0)
  const [isAnswering, setIsAnswering] = useState(false)
  const [isCompleted, setIsCompleted] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [micPermissionGranted, setMicPermissionGranted] = useState(false)
  const [sessionStarted, setSessionStarted] = useState(false)
  const [isProcessingAnswer, setIsProcessingAnswer] = useState(false)
  const [, setHasSpokenFirstPrompt] = useState(false)
  const [isWaitingForNext, setIsWaitingForNext] = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)
  const [sessionPhase, setSessionPhase] = useState<'teaching' | 'testing'>('teaching')
  const [teachingSpoken, setTeachingSpoken] = useState(false)
  const [attemptCount, setAttemptCount] = useState(0)
  const [showTryAgain, setShowTryAgain] = useState(false)
  const [isTransitioning, setIsTransitioning] = useState(false)
  const [isSpeechReady, setIsSpeechReady] = useState(false) // Track when speech recognition is listening
  // Session statistics for progress report
  const [sessionStats, setSessionStats] = useState({
    totalCorrect: 0,
    totalIncorrect: 0,
    totalCuesUsed: 0,
    responseTimes: [] as number[],
    confidenceScores: [] as number[],  // Speech clarity scores (0-1)
  })
  const trialStartTimeRef = useRef<number>(0)

  const isProcessingAnswerRef = useRef(false)
  const currentContactRef = useRef<PersonalContact | null>(null)
  const currentIndexRef = useRef(0)
  const hasSpokenFirstPromptRef = useRef(false)
  const isTeachingSpeakingRef = useRef(false)

  // Request microphone permission first, before loading session
  useEffect(() => {
    const requestMicPermission = async () => {
      try {
        // Request microphone access - this triggers the browser permission prompt
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        // Stop the stream immediately - we just needed the permission
        stream.getTracks().forEach(track => track.stop())
        setMicPermissionGranted(true)
      } catch (err) {
        console.error('Microphone permission denied:', err)
        // Still allow session to proceed - the speech recognition component will handle the error
        setMicPermissionGranted(true)
      }
    }
    requestMicPermission()
  }, [])

  const initializeSession = useCallback(async () => {
    try {
      setLoading(true)

      const { data: { user } } = await supabase.auth.getUser()
      if (!user) {
        router.push('/login')
        return
      }

      const sessionData = await apiClient.get<Record<string, unknown>>(`/api/life-words/sessions/${sessionId}`)
      setSession(sessionData.session as Session)
      setContacts(sessionData.contacts as PersonalContact[])

      const firstContact = (sessionData.contacts as PersonalContact[])[0]
      setCurrentIndex(0)
      currentIndexRef.current = 0
      setCurrentContact(firstContact)
      currentContactRef.current = firstContact
      setSessionPhase('teaching')
      setTeachingSpoken(false)
      setIsAnswering(false)
      isTeachingSpeakingRef.current = false

      hasSpokenFirstPromptRef.current = false
      setHasSpokenFirstPrompt(false)

      setLoading(false)

    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      console.error('Session initialization error:', err)
      setError(`Failed to initialize session: ${message}`)
      setLoading(false)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId])

  // Initialize session only after user clicks Start
  useEffect(() => {
    if (sessionStarted) {
      initializeSession()
    }
  }, [sessionStarted, initializeSession])

  // Handle teaching phase - speak name and auto-advance
  useEffect(() => {
    if (sessionPhase !== 'teaching' || !currentContact || loading || teachingSpoken) return

    // Prevent concurrent speech
    if (isTeachingSpeakingRef.current) return

    const speakAndAdvance = async () => {
      // Double-check we're not already speaking
      if (isTeachingSpeakingRef.current) return
      isTeachingSpeakingRef.current = true
      setTeachingSpoken(true)

      try {
        await waitForVoices()
        // Say "This is [name]" (with correct grammar for items)
        // Use pronunciation if available, otherwise use name
        const spokenName = currentContact.pronunciation || currentContact.name
        const isItem = currentContact.relationship === 'item'
        const phrase = isItem ? getItemPhrase(spokenName) : `This is ${spokenName}`

        // Retry speech up to 3 times if it fails
        let speechSuccess = false
        for (let attempt = 0; attempt < 3 && !speechSuccess; attempt++) {
          try {
            await speak(phrase, { gender: voiceGender })
            speechSuccess = true
          } catch (speechError) {
            console.warn(`Speech attempt ${attempt + 1} failed:`, speechError)
            if (attempt < 2) {
              await new Promise(resolve => setTimeout(resolve, 500))
            }
          }
        }

        // Wait a moment to let user see the photo and hear the name
        await new Promise(resolve => setTimeout(resolve, speechSuccess ? 2500 : 3000))

        // Move to next contact in teaching phase or switch to testing
        const nextIndex = currentIndex + 1
        if (nextIndex >= contacts.length) {
          // Teaching complete, start testing phase
          await speak(`Now let's practice! Look at each picture and say who it is.`, { gender: voiceGender })
          await new Promise(resolve => setTimeout(resolve, 2000))

          // Reset to first contact for testing
          isTeachingSpeakingRef.current = false
          setCurrentIndex(0)
          currentIndexRef.current = 0
          setCurrentContact(contacts[0])
          currentContactRef.current = contacts[0]
          setAttemptCount(0)
          setShowTryAgain(false)
          setIsSpeechReady(false)
          setIsTransitioning(true)
          setSessionPhase('testing')
          // Reset trial timer when entering testing phase
          trialStartTimeRef.current = Date.now()
          // Delay before enabling speech recognition to avoid picking up TTS
          setTimeout(() => {
            setIsTransitioning(false)
            setIsAnswering(true)
          }, 1500)
        } else {
          // Move to next contact in teaching
          isTeachingSpeakingRef.current = false
          setCurrentIndex(nextIndex)
          currentIndexRef.current = nextIndex
          setCurrentContact(contacts[nextIndex])
          currentContactRef.current = contacts[nextIndex]
          setTeachingSpoken(false)
        }
      } catch (error: unknown) {
        const msg = error instanceof Error ? error.message : error
        console.warn('Teaching phase speech failed:', msg)
        isTeachingSpeakingRef.current = false
        // Still advance even if speech fails
        const nextIndex = currentIndex + 1
        if (nextIndex >= contacts.length) {
          setCurrentIndex(0)
          currentIndexRef.current = 0
          setCurrentContact(contacts[0])
          currentContactRef.current = contacts[0]
          setAttemptCount(0)
          setShowTryAgain(false)
          setIsSpeechReady(false)
          setIsTransitioning(true)
          setSessionPhase('testing')
          // Reset trial timer when entering testing phase
          trialStartTimeRef.current = Date.now()
          // Delay before enabling speech recognition
          setTimeout(() => {
            setIsTransitioning(false)
            setIsAnswering(true)
          }, 1500)
        } else {
          setCurrentIndex(nextIndex)
          currentIndexRef.current = nextIndex
          setCurrentContact(contacts[nextIndex])
          currentContactRef.current = contacts[nextIndex]
          setTeachingSpoken(false)
        }
      }
    }

    // Delay before speaking to let image load
    const timer = setTimeout(speakAndAdvance, 800)
    return () => clearTimeout(timer)
  }, [sessionPhase, currentContact, currentIndex, contacts, loading, teachingSpoken, voiceGender])

  // Track if prompt has been spoken for current image (to avoid speaking twice)
  const hasSpokenForCurrentImageRef = useRef(false)

  // Reset spoken flag when moving to new image
  useEffect(() => {
    if (!isSpeechReady) {
      hasSpokenForCurrentImageRef.current = false
    }
  }, [isSpeechReady])

  const handleAnswer = async (transcript: string, confidence?: number) => {
    const currentCont = currentContactRef.current
    const isProcessing = isProcessingAnswerRef.current

    if (!currentCont || !session || isProcessing) {
      return
    }

    setIsProcessingAnswer(true)
    isProcessingAnswerRef.current = true

    try {
      const matchResult = await evaluateNameAnswer(transcript, currentCont.name, {
        nickname: currentCont.nickname,
      })
      const isCorrect = matchResult.is_correct

      if (isCorrect) {
        await handleCorrectAnswer(transcript, confidence)
      } else {
        // Answer is incorrect
        const newAttemptCount = attemptCount + 1
        setAttemptCount(newAttemptCount)
        setIsProcessingAnswer(false)
        isProcessingAnswerRef.current = false

        // After 2 attempts, show hints. Otherwise offer "Try Again"
        if (newAttemptCount >= 2) {
          setCuesUsed(0)
          setIsAnswering(false)
          setShowTryAgain(false)
        } else {
          // Show "Try Again" option
          setShowTryAgain(true)
          setIsAnswering(false)
        }
      }
    } catch (err) {
      console.error('Error handling answer:', err)
      setIsProcessingAnswer(false)
      isProcessingAnswerRef.current = false
    }
  }

  const handleCorrectAnswer = async (userAnswer: string, confidence?: number) => {
    const currentCont = currentContactRef.current
    if (!currentCont || !session) {
      setIsProcessingAnswer(false)
      isProcessingAnswerRef.current = false
      return
    }

    // Calculate response time
    const responseTime = (Date.now() - trialStartTimeRef.current) / 1000

    setIsAnswering(false)
    setIsWaitingForNext(true)
    setShowSuccess(true)

    // Update session stats (include confidence if available)
    setSessionStats(prev => ({
      ...prev,
      totalCorrect: prev.totalCorrect + 1,
      totalCuesUsed: prev.totalCuesUsed + cuesUsed,
      responseTimes: [...prev.responseTimes, responseTime],
      confidenceScores: confidence !== undefined
        ? [...prev.confidenceScores, confidence]
        : prev.confidenceScores,
    }))

    await saveResponse(true, userAnswer, undefined, responseTime, confidence)

    try {
      const feedbackMessage = getRandomPositiveFeedback()
      await speak(feedbackMessage, { gender: voiceGender })
    } catch (speakError: unknown) {
      const msg = speakError instanceof Error ? speakError.message : speakError
      console.warn('Text-to-speech failed:', msg)
    }

    setTimeout(async () => {
      setShowSuccess(false)
      await moveToNext()
    }, 2000)
  }

  const handleCueAnswer = async (userAnswer: string, isCorrect: boolean, confidence?: number) => {
    if (!currentContact || !session) return

    if (isCorrect) {
      // Calculate response time
      const responseTime = (Date.now() - trialStartTimeRef.current) / 1000
      const totalCues = cuesUsed + 1

      // Update session stats (include confidence if available)
      setSessionStats(prev => ({
        ...prev,
        totalCorrect: prev.totalCorrect + 1,
        totalCuesUsed: prev.totalCuesUsed + totalCues,
        responseTimes: [...prev.responseTimes, responseTime],
        confidenceScores: confidence !== undefined
          ? [...prev.confidenceScores, confidence]
          : prev.confidenceScores,
      }))

      await saveResponse(true, userAnswer, totalCues, responseTime, confidence)
      try {
        const feedbackMessage = getRandomPositiveFeedback()
        await speak(feedbackMessage, { gender: voiceGender })
      } catch (speakError: unknown) {
        const msg = speakError instanceof Error ? speakError.message : speakError
        console.warn('Text-to-speech failed:', msg)
      }
      setShowSuccess(true)
      setTimeout(() => {
        setShowSuccess(false)
        moveToNext()
      }, 2000)
    } else {
      setCuesUsed((prev) => prev + 1)
    }
  }

  const handleFinalAnswer = async () => {
    if (!currentContact || !session) return

    // Calculate response time for incorrect answer
    const responseTime = (Date.now() - trialStartTimeRef.current) / 1000

    // Update session stats for incorrect answer
    setSessionStats(prev => ({
      ...prev,
      totalIncorrect: prev.totalIncorrect + 1,
      totalCuesUsed: prev.totalCuesUsed + 7,
      responseTimes: [...prev.responseTimes, responseTime],
    }))

    await saveResponse(false, null, 7, responseTime)
    moveToNext()
  }

  // Handle no response after max speech recognition restarts
  const handleNoResponse = async () => {
    if (!currentContact || !session) return

    // Calculate response time
    const responseTime = (Date.now() - trialStartTimeRef.current) / 1000

    // Update session stats for no response (treated as incorrect, no cues used)
    setSessionStats(prev => ({
      ...prev,
      totalIncorrect: prev.totalIncorrect + 1,
      responseTimes: [...prev.responseTimes, responseTime],
    }))

    await saveResponse(false, null, 0, responseTime)
    // Move directly to next item without showing hints or try again
    moveToNext()
  }

  const saveResponse = async (
    isCorrect: boolean,
    userAnswer: string | null,
    cuesUsedOverride?: number,
    responseTime?: number,
    confidence?: number
  ) => {
    const currentCont = currentContactRef.current
    if (!currentCont || !session) return

    const actualCuesUsed = cuesUsedOverride !== undefined ? cuesUsedOverride : cuesUsed

    try {
      await apiClient.post(`/api/life-words/sessions/${session.id}/responses`, {
        contact_id: currentCont.id,
        is_correct: isCorrect,
        cues_used: actualCuesUsed,
        response_time: responseTime ?? null,
        user_answer: userAnswer,
        correct_answer: currentCont.name,
        speech_confidence: confidence ?? null,
      })
    } catch (error) {
      console.error('Error saving response:', error)
    }
  }

  const moveToNext = async () => {
    const currentIdx = currentIndexRef.current
    const nextIndex = currentIdx + 1

    if (nextIndex >= contacts.length) {
      completeSession()
      return
    }

    const nextContact = contacts[nextIndex]

    currentIndexRef.current = nextIndex
    currentContactRef.current = nextContact
    isProcessingAnswerRef.current = false

    // Reset trial timer for next contact
    trialStartTimeRef.current = Date.now()

    setCurrentIndex(nextIndex)
    setCurrentContact(nextContact)
    setCuesUsed(0)
    setAttemptCount(0)
    setShowTryAgain(false)
    setIsSpeechReady(false) // Reset speech ready state for new image
    setIsAnswering(true)
    setIsProcessingAnswer(false)
    setIsWaitingForNext(false)
    // Note: The prompt is spoken by onStartListening in SpeechRecognitionButton
  }

  const completeSession = async () => {
    if (!session) return

    setIsCompleted(true)
    setIsAnswering(false)

    try {
      await apiClient.put(`/api/life-words/sessions/${session.id}/complete`)
    } catch (error) {
      console.error('Error completing session:', error)
    }
  }

  const handleDone = () => {
    router.push('/dashboard/treatments/life-words')
  }

  if (!micPermissionGranted) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">🎤</div>
          <p className="text-xl text-gray-700 mb-2">Please allow microphone access</p>
          <p className="text-lg text-gray-500">This is needed for speech recognition</p>
        </div>
      </div>
    )
  }

  if (!sessionStarted) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">✓</div>
          <p className="text-xl text-gray-700 mb-6">Microphone ready!</p>
          <button
            onClick={() => setSessionStarted(true)}
            className="bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-bold py-4 px-8 rounded-lg text-2xl"
          >
            Start Session
          </button>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-[var(--color-primary)] mx-auto mb-4"></div>
          <p className="text-xl text-gray-700">Starting session...</p>
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

  if (isCompleted) {
    const totalAttempts = sessionStats.totalCorrect + sessionStats.totalIncorrect
    const accuracy = totalAttempts > 0 ? Math.round((sessionStats.totalCorrect / totalAttempts) * 100) : 0
    const avgResponseTime = sessionStats.responseTimes.length > 0
      ? (sessionStats.responseTimes.reduce((a, b) => a + b, 0) / sessionStats.responseTimes.length).toFixed(1)
      : '0'
    const avgCues = totalAttempts > 0 ? (sessionStats.totalCuesUsed / totalAttempts).toFixed(1) : '0'
    // Calculate speech clarity (confidence scores are 0-1, convert to percentage)
    const avgSpeechClarity = sessionStats.confidenceScores.length > 0
      ? Math.round((sessionStats.confidenceScores.reduce((a, b) => a + b, 0) / sessionStats.confidenceScores.length) * 100)
      : null

    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="text-center max-w-md w-full">
          <h2 className="text-4xl font-bold text-green-600 mb-4">Great job!</h2>
          <p className="text-xl text-gray-700 mb-6">
            You completed today&apos;s practice session.
          </p>

          {/* Progress Report */}
          <div className="bg-white border-2 border-gray-200 rounded-lg p-6 mb-6 text-left">
            <h3 className="text-2xl font-bold text-gray-800 mb-4 text-center">Session Progress</h3>

            <div className="space-y-4">
              <div className="flex justify-between items-center border-b pb-2">
                <span className="text-lg text-gray-600">Accuracy:</span>
                <span className="text-2xl font-bold text-green-600">{accuracy}%</span>
              </div>

              <div className="flex justify-between items-center border-b pb-2">
                <span className="text-lg text-gray-600">Correct:</span>
                <span className="text-2xl font-bold text-gray-800">{sessionStats.totalCorrect} / {totalAttempts}</span>
              </div>

              <div className="flex justify-between items-center border-b pb-2">
                <span className="text-lg text-gray-600">Avg Response Time:</span>
                <span className="text-2xl font-bold text-blue-600">{avgResponseTime}s</span>
              </div>

              <div className="flex justify-between items-center border-b pb-2">
                <span className="text-lg text-gray-600">Avg Hints Used:</span>
                <span className="text-2xl font-bold text-orange-600">{avgCues}</span>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-lg text-gray-600">Speech Clarity:</span>
                <span className="text-2xl font-bold text-purple-600">
                  {avgSpeechClarity !== null ? `${avgSpeechClarity}%` : 'N/A'}
                </span>
              </div>
            </div>
          </div>

          <button
            onClick={handleDone}
            className="bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-bold py-4 px-8 rounded-lg text-xl w-full"
          >
            Done
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8">
      {/* Phase indicator */}
      <div className="mb-4">
        <span className={`inline-block px-4 py-2 rounded-full text-lg font-semibold ${
          sessionPhase === 'teaching'
            ? 'bg-blue-100 text-blue-700'
            : 'bg-green-100 text-green-700'
        }`}>
          {sessionPhase === 'teaching' ? '📚 Learning' : '✏️ Practice'}
        </span>
      </div>

      {/* Progress indicator - simple dots */}
      <div className="flex gap-2 mb-8">
        {contacts.map((_, idx) => (
          <div
            key={idx}
            className={`w-3 h-3 rounded-full transition-colors ${
              sessionPhase === 'teaching'
                ? idx < currentIndex
                  ? 'bg-blue-500'
                  : idx === currentIndex
                  ? 'bg-blue-600'
                  : 'bg-gray-300'
                : idx < currentIndex
                ? 'bg-green-500'
                : idx === currentIndex
                ? 'bg-[var(--color-primary)]'
                : 'bg-gray-300'
            }`}
          />
        ))}
      </div>

      {currentContact && (
        <>
          {/* Photo display - hidden during testing/transition until speech recognition is ready */}
          {(sessionPhase === 'teaching' || isSpeechReady || showSuccess || isWaitingForNext || showTryAgain) ? (
            <div className={`relative w-40 h-40 md:w-48 md:h-48 rounded-lg overflow-hidden shadow-lg mb-6 transition-all duration-300 ${
              showSuccess
                ? 'ring-8 ring-green-500'
                : sessionPhase === 'teaching'
                ? 'border-4 border-blue-300'
                : 'border-4 border-gray-200'
            }`}>
              <Image
                src={currentContact.photo_url}
                alt={sessionPhase === 'teaching' ? currentContact.name : "Who is this?"}
                fill
                className="object-cover"
              />
              {showSuccess && (
                <div className="absolute inset-0 bg-green-500/30 flex items-center justify-center">
                  <span className="text-8xl">✓</span>
                </div>
              )}
            </div>
          ) : (
            <div className="w-40 h-40 md:w-48 md:h-48 mb-6 flex items-center justify-center">
              <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-[var(--color-primary)]"></div>
            </div>
          )}

          {/* Teaching phase - show the name */}
          {sessionPhase === 'teaching' ? (
            <div className="text-center">
              <p className="text-3xl font-bold text-blue-700 mb-4">
                {currentContact.name}
              </p>
              <p className="text-xl text-gray-600 mb-2">
                {currentContact.relationship === 'item'
                  ? (currentContact.category || 'item')
                  : currentContact.relationship}
              </p>
              <p className="text-lg text-gray-500 animate-pulse">
                Learning names... {currentIndex + 1} of {contacts.length}
              </p>
            </div>
          ) : (
            <>
              {/* Testing phase - prompt text (hidden until speech recognition ready) */}
              {(isSpeechReady || showSuccess || isWaitingForNext || showTryAgain) && (
                <p className="text-2xl text-gray-700 mb-6 text-center">
                  {currentContact.relationship === 'item' ? 'What is this?' : 'Who is this?'}
                </p>
              )}

              {isWaitingForNext && !isAnswering ? (
                <div className="text-center">
                  <p className="text-xl text-green-700">Moving to next...</p>
                </div>
              ) : showTryAgain ? (
                <div className="text-center space-y-4">
                  <p className="text-xl text-gray-600">That&apos;s not quite right. Want to try again?</p>
                  <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <button
                      onClick={() => {
                        setShowTryAgain(false)
                        setIsAnswering(true)
                      }}
                      className="bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-bold py-4 px-8 rounded-lg text-xl"
                    >
                      Try Again
                    </button>
                    <button
                      onClick={() => {
                        setShowTryAgain(false)
                        setAttemptCount(2)
                        setCuesUsed(0)
                        setIsAnswering(false)
                      }}
                      className="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold py-4 px-8 rounded-lg text-xl"
                    >
                      Get a Hint
                    </button>
                  </div>
                </div>
              ) : isTransitioning ? (
                <div className="text-center">
                  <p className="text-2xl text-green-600 font-semibold animate-pulse">Get ready to practice!</p>
                </div>
              ) : isAnswering ? (
                <SpeechRecognitionButton
                  key={`speech-${currentIndex}-${attemptCount}`}
                  onResult={handleAnswer}
                  disabled={isProcessingAnswer}
                  resetTrigger={currentIndex}
                  autoStart={true}
                  onListeningChange={(listening) => setIsSpeechReady(listening)}
                  onNoResponse={handleNoResponse}
                  noResponseTimeout={60}
                  onStartListening={async () => {
                    // Speak the prompt BEFORE speech recognition starts
                    // This prevents the microphone from picking up the TTS
                    if (attemptCount === 0 && !hasSpokenForCurrentImageRef.current) {
                      hasSpokenForCurrentImageRef.current = true
                      try {
                        const prompt = currentContact.relationship === 'item' ? 'What is this?' : 'Who is this?'
                        await speak(prompt, { gender: voiceGender })
                        // Extra delay after TTS to ensure audio has stopped
                        await new Promise(resolve => setTimeout(resolve, 1000))
                      } catch (error: unknown) {
                        console.warn('Failed to speak prompt:', error)
                      }
                    }
                  }}
                />
              ) : (
                <PersonalizedCueSystem
                  contact={currentContact}
                  cuesUsed={cuesUsed}
                  onAnswer={handleCueAnswer}
                  onFinalAnswer={handleFinalAnswer}
                  voiceGender={voiceGender}
                />
              )}
            </>
          )}

          {/* Done button - always visible */}
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
