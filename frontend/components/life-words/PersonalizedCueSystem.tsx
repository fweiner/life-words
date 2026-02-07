'use client'

import { useState, useEffect, useRef } from 'react'
import { speak, waitForVoices, type VoiceGender } from '@/lib/utils/textToSpeech'
import SpeechRecognitionButton from '@/components/shared/SpeechRecognitionButton'
import { evaluateNameAnswer } from '@/lib/api/matching'

interface PersonalContact {
  id: string
  name: string
  nickname?: string
  relationship: string
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

interface PersonalizedCueSystemProps {
  contact: PersonalContact
  cuesUsed: number
  onAnswer: (answer: string, isCorrect: boolean, confidence?: number) => void
  onFinalAnswer: () => void
  onContinue: () => void
  voiceGender?: VoiceGender
}

const RELATIONSHIP_LABELS: Record<string, string> = {
  spouse: 'your spouse',
  child: 'your child',
  grandchild: 'your grandchild',
  parent: 'your parent',
  sibling: 'your sibling',
  friend: 'your friend',
  pet: 'your pet',
  caregiver: 'your caregiver',
  neighbor: 'your neighbor',
  other: 'someone you know',
}

const PERSONALITY_LABELS: Record<string, string> = {
  outgoing: 'outgoing',
  reserved: 'reserved',
  optimistic: 'optimistic',
  cautious: 'cautious',
  friendly: 'friendly',
  quiet: 'quiet',
  energetic: 'energetic',
  calm: 'calm',
}

// Generate cue types based on available contact data
function getCueTypes(contact: PersonalContact) {
  const cues: { level: number; name: string; getText: () => string }[] = []
  const isItem = contact.relationship === 'item'
  const possessivePronoun = isItem ? 'The' : 'Their'

  // Level 1: First letter (always available)
  cues.push({
    level: 1,
    name: 'First Letter',
    getText: () => `${possessivePronoun} name starts with '${contact.first_letter || contact.name[0].toUpperCase()}'`
  })

  // Level 2: Relationship (always available)
  cues.push({
    level: 2,
    name: 'Relationship',
    getText: () => `This is ${RELATIONSHIP_LABELS[contact.relationship] || contact.relationship}`
  })

  // Level 3: Description or Personality (context about who they are)
  if (contact.description) {
    cues.push({
      level: 3,
      name: 'Description',
      getText: () => contact.description!
    })
  } else if (contact.personality) {
    const personality = contact.personality
    cues.push({
      level: 3,
      name: 'Personality',
      getText: () => `This person is ${PERSONALITY_LABELS[personality] || personality}`
    })
  } else {
    cues.push({
      level: 3,
      name: 'Hint',
      getText: () => `Think about ${RELATIONSHIP_LABELS[contact.relationship] || 'someone special'} in your life`
    })
  }

  // Level 4: Phonemic cue (first syllable approximation)
  const firstTwoLetters = contact.name.substring(0, Math.min(3, contact.name.length))
  cues.push({
    level: 4,
    name: 'Phonemic',
    getText: () => `${possessivePronoun} name sounds like '${firstTwoLetters}...'`
  })

  // Level 5: Association, Interests, Social Behavior, or Location (meaningful memory cues)
  if (contact.association) {
    cues.push({
      level: 5,
      name: 'Association',
      getText: () => contact.association!
    })
  } else if (contact.interests) {
    cues.push({
      level: 5,
      name: 'Interests',
      getText: () => `This person loves ${contact.interests}`
    })
  } else if (contact.social_behavior) {
    cues.push({
      level: 5,
      name: 'Social',
      getText: () => contact.social_behavior!
    })
  } else if (contact.values) {
    cues.push({
      level: 5,
      name: 'Values',
      getText: () => `This person values ${contact.values}`
    })
  } else if (contact.location_context) {
    cues.push({
      level: 5,
      name: 'Location',
      getText: () => contact.location_context!
    })
  } else {
    cues.push({
      level: 5,
      name: 'Memory',
      getText: () => `Think of a happy memory with ${RELATIONSHIP_LABELS[contact.relationship] || 'this person'}`
    })
  }

  // Level 6: Full name shown (visual cue)
  cues.push({
    level: 6,
    name: 'Name Shown',
    getText: () => `${possessivePronoun} name is: ${contact.name}`
  })

  // Level 7: Full name + audio (repetition)
  cues.push({
    level: 7,
    name: 'Say Together',
    getText: () => `Say the name with me: ${contact.name}`
  })

  return cues
}

// matchPersonalAnswer is now handled by the backend via evaluateNameAnswer API

export function PersonalizedCueSystem({
  contact,
  cuesUsed,
  onAnswer,
  onFinalAnswer,
  onContinue,
  voiceGender = 'female',
}: PersonalizedCueSystemProps) {
  const CUE_TYPES = getCueTypes(contact)
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
      setCurrentCueLevel(expectedLevel)
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

  useEffect(() => {
    finalAnswerCalledRef.current = false
    setIsShowingFinalAnswer(false)

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

        await speak(text, { gender: voiceGender })

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
  }, [currentCueLevel, contact])

  const handleFinalAnswer = async () => {
    if (finalAnswerCalledRef.current) {
      return
    }
    finalAnswerCalledRef.current = true

    setIsShowingFinalAnswer(true)
    setHasSpoken(false)

    try {
      await speak(`This is ${contact.name}`, { gender: voiceGender })
    } catch (error) {
      console.warn('Failed to speak final answer:', error)
    }

    onFinalAnswer()
  }

  const handleAnswer = async (transcript: string, confidence?: number) => {
    try {
      const result = await evaluateNameAnswer(transcript, contact.name, {
        nickname: contact.nickname,
      })
      const isCorrect = result.is_correct

      if (isCorrect) {
        onAnswer(transcript, true, confidence)
      } else {
        if (currentCueLevel < 7) {
          onAnswer(transcript, false, confidence)
        } else {
          if (!finalAnswerCalledRef.current) {
            handleFinalAnswer()
          }
        }
      }
    } catch (error) {
      console.warn('Matching API error, treating as incorrect:', error)
      if (currentCueLevel < 7) {
        onAnswer(transcript, false, confidence)
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
        <p className="text-xl mb-6">The name has been provided.</p>
        <button
          className="bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-bold py-6 px-12 rounded-lg text-2xl transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2"
          onClick={onContinue}
          style={{ minHeight: '44px' }}
        >
          Continue to Next Person
        </button>
      </div>
    )
  }

  const currentCue = CUE_TYPES[currentCueLevel - 1]
  if (!currentCue) return null

  return (
    <div className="text-center w-full max-w-2xl">
      <div className="bg-blue-50 border-4 border-blue-300 rounded-lg p-8 mb-6">
        <p className="text-sm text-blue-600 mb-2">Hint {currentCueLevel} of 7</p>
        <p className="text-2xl text-blue-800">{cueText}</p>
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
          <p className="text-gray-600 text-xl">Moving to next person...</p>
        </div>
      )}
    </div>
  )
}
