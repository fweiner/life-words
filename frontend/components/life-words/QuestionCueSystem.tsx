'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { speak, waitForVoices } from '@/lib/utils/textToSpeech'
import SpeechRecognitionButton from '@/components/shared/SpeechRecognitionButton'
import { evaluateQuestionAnswer } from '@/lib/api/matching'

interface GeneratedQuestion {
  contact_id: string
  contact_name: string
  contact_photo_url: string
  question_type: number
  question_text: string
  expected_answer: string
  acceptable_answers: string[]
}

interface QuestionCueSystemProps {
  question: GeneratedQuestion
  cuesUsed: number
  onAnswer: (answer: string, isCorrect: boolean) => void
  onFinalAnswer: () => void
  onContinue: () => void
}

// Generate cue types based on question type and expected answer
function getCueTypes(question: GeneratedQuestion) {
  const cues: { level: number; name: string; getText: () => string }[] = []
  const answer = question.expected_answer

  // Level 1: Repeat the question
  cues.push({
    level: 1,
    name: 'Repeat Question',
    getText: () => `Let me ask again: ${question.question_text}`
  })

  // Level 2: Category hint based on question type
  cues.push({
    level: 2,
    name: 'Category Hint',
    getText: () => {
      switch (question.question_type) {
        case 1:
          return `Think about how ${question.contact_name} is related to you. Are they family? A friend?`
        case 2:
          return `Think about where you usually spend time with ${question.contact_name}.`
        case 3:
          return `Think about what ${question.contact_name} likes to do for fun or hobbies.`
        case 4:
          return `Think about what kind of person ${question.contact_name} is. How would you describe them?`
        case 5:
          return `Think about someone special in your life. Who fits this description?`
        default:
          return `Think carefully about ${question.contact_name}.`
      }
    }
  })

  // Level 3: First letter hint
  cues.push({
    level: 3,
    name: 'First Letter',
    getText: () => `The answer starts with the letter '${answer[0].toUpperCase()}'`
  })

  // Level 4: Word count / length hint
  const wordCount = answer.split(' ').length
  cues.push({
    level: 4,
    name: 'Length Hint',
    getText: () => {
      if (wordCount > 1) {
        return `The answer has ${wordCount} words. It starts with '${answer[0].toUpperCase()}'`
      } else {
        return `The answer is one word with ${answer.length} letters, starting with '${answer[0].toUpperCase()}'`
      }
    }
  })

  // Level 5: Partial answer (first word or half the answer)
  cues.push({
    level: 5,
    name: 'Partial Answer',
    getText: () => {
      if (wordCount > 1) {
        const firstWord = answer.split(' ')[0]
        return `The answer starts with '${firstWord}...'`
      } else {
        const halfLength = Math.ceil(answer.length / 2)
        return `The answer starts with '${answer.substring(0, halfLength)}...'`
      }
    }
  })

  // Level 6: Full answer shown
  cues.push({
    level: 6,
    name: 'Answer Shown',
    getText: () => `The answer is: ${answer}`
  })

  // Level 7: Say together
  cues.push({
    level: 7,
    name: 'Say Together',
    getText: () => `Say the answer with me: ${answer}`
  })

  return cues
}

// evaluateAnswer is now handled by the backend via evaluateQuestionAnswer API

export function QuestionCueSystem({
  question,
  cuesUsed,
  onAnswer,
  onFinalAnswer,
  onContinue,
}: QuestionCueSystemProps) {
  const CUE_TYPES = getCueTypes(question)
  const [currentCueLevel, setCurrentCueLevel] = useState(cuesUsed + 1)
  const [cueText, setCueText] = useState('')
  const [hasSpoken, setHasSpoken] = useState(false)
  const [isShowingFinalAnswer, setIsShowingFinalAnswer] = useState(false)
  const finalAnswerCalledRef = useRef(false)
  const currentSpeechRef = useRef<{ level: number; cancelled: boolean } | null>(null)
  const initializedRef = useRef(false)
  const previousCuesUsedRef = useRef(cuesUsed)

  // Sync currentCueLevel when cuesUsed prop changes
  useEffect(() => {
    const expectedLevel = cuesUsed + 1
    const cuesUsedChanged = previousCuesUsedRef.current !== cuesUsed

    if (cuesUsed === 0) {
      initializedRef.current = false
    }

    if (cuesUsedChanged) {
      setCurrentCueLevel(expectedLevel) // eslint-disable-line react-hooks/set-state-in-effect
      setHasSpoken(false)
      initializedRef.current = true
      previousCuesUsedRef.current = cuesUsed
    } else if (!initializedRef.current) {
      setCurrentCueLevel(expectedLevel)
      setHasSpoken(false)
      initializedRef.current = true
      previousCuesUsedRef.current = cuesUsed
    }
  }, [cuesUsed])

  const handleFinalAnswer = useCallback(async () => {
    if (finalAnswerCalledRef.current) {
      return
    }
    finalAnswerCalledRef.current = true

    setIsShowingFinalAnswer(true)
    setHasSpoken(false)

    try {
      await speak(`The answer is: ${question.expected_answer}`)
    } catch (error) {
      console.warn('Failed to speak final answer:', error)
    }

    onFinalAnswer()
  }, [question.expected_answer, onFinalAnswer])

  useEffect(() => {
    finalAnswerCalledRef.current = false
    setIsShowingFinalAnswer(false) // eslint-disable-line react-hooks/set-state-in-effect

    if (currentCueLevel > 7) {
      if (!finalAnswerCalledRef.current) {
        finalAnswerCalledRef.current = true
        handleFinalAnswer()
      }
      return
    }

    const cue = CUE_TYPES[currentCueLevel - 1]
    if (!cue) return

    const text = cue.getText()
    setCueText(text)
    setHasSpoken(false)

    const speechOperation = { level: currentCueLevel, cancelled: false }
    currentSpeechRef.current = speechOperation

    const speakCue = async () => {
      if (speechOperation.cancelled || currentSpeechRef.current !== speechOperation) {
        return
      }

      try {
        await waitForVoices()

        if (speechOperation.cancelled || currentSpeechRef.current !== speechOperation) {
          return
        }

        await new Promise(resolve => setTimeout(resolve, 300))

        if (speechOperation.cancelled || currentSpeechRef.current !== speechOperation) {
          return
        }

        await speak(text)

        if (speechOperation.cancelled || currentSpeechRef.current !== speechOperation) {
          return
        }

        setHasSpoken(true)
      } catch (error) {
        console.warn(`Failed to speak cue ${currentCueLevel}:`, error)
        if (!speechOperation.cancelled && currentSpeechRef.current === speechOperation) {
          setHasSpoken(true)
        }
      }
    }

    const speakDelay = setTimeout(() => {
      if (currentCueLevel > 7 || speechOperation.cancelled) {
        return
      }
      speakCue()
    }, 100)

    return () => {
      clearTimeout(speakDelay)
      if (currentSpeechRef.current === speechOperation) {
        speechOperation.cancelled = true
        currentSpeechRef.current = null
      }
    }
  }, [currentCueLevel, question, CUE_TYPES, handleFinalAnswer])

  const handleAnswer = async (transcript: string) => {
    try {
      const result = await evaluateQuestionAnswer(
        transcript,
        question.expected_answer,
        question.acceptable_answers
      )

      if (result.is_correct) {
        onAnswer(transcript, true)
      } else {
        if (currentCueLevel < 7) {
          onAnswer(transcript, false)
        } else {
          if (!finalAnswerCalledRef.current) {
            handleFinalAnswer()
          }
        }
      }
    } catch (error) {
      console.warn('Matching API error, treating as incorrect:', error)
      if (currentCueLevel < 7) {
        onAnswer(transcript, false)
      } else {
        if (!finalAnswerCalledRef.current) {
          handleFinalAnswer()
        }
      }
    }
  }

  const handleNeedMoreHelp = () => {
    if (currentCueLevel < 7) {
      onAnswer('', false) // Trigger next cue
    } else {
      handleFinalAnswer()
    }
  }

  if (currentCueLevel > 7) {
    return (
      <div className="text-center max-w-2xl">
        <p className="text-xl mb-6">The answer has been provided.</p>
        <button
          className="bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-bold py-6 px-12 rounded-lg text-2xl transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2"
          onClick={onContinue}
          style={{ minHeight: '44px' }}
        >
          Continue to Next Question
        </button>
      </div>
    )
  }

  const currentCue = CUE_TYPES[currentCueLevel - 1]
  if (!currentCue) return null

  return (
    <div className="text-center w-full max-w-2xl">
      {/* Question reminder */}
      <div className="bg-white rounded-lg shadow-md p-4 mb-4">
        <p className="text-lg text-gray-600 mb-1">Question:</p>
        <p className="text-xl text-gray-800 font-medium">{question.question_text}</p>
      </div>

      {/* Cue/Hint display */}
      <div className="bg-amber-50 border-4 border-amber-300 rounded-lg p-8 mb-6">
        <p className="text-sm text-amber-600 mb-2">Hint {currentCueLevel} of 7</p>
        <p className="text-2xl text-amber-800">{cueText}</p>
      </div>

      {hasSpoken && !isShowingFinalAnswer && (
        <>
          <SpeechRecognitionButton
            onResult={handleAnswer}
            disabled={false}
            autoStart={true}
          />
          <button
            onClick={handleNeedMoreHelp}
            className="mt-4 text-gray-500 hover:text-gray-700 underline text-lg"
          >
            I need another hint
          </button>
        </>
      )}

      {isShowingFinalAnswer && (
        <div className="text-center mt-6">
          <p className="text-gray-600 text-xl">Moving to next question...</p>
        </div>
      )}
    </div>
  )
}
