/**
 * Text-to-speech utility using Amazon Polly via backend API
 */

export type VoiceGender = 'male' | 'female' | 'neutral'

export interface SpeechOptions {
  rate?: number // Not used with Polly, kept for interface compatibility
  pitch?: number // Not used with Polly, kept for interface compatibility
  volume?: number // 0 to 1, default 1
  lang?: string // Not used with Polly, kept for interface compatibility
  voice?: SpeechSynthesisVoice // Not used with Polly, kept for interface compatibility
  gender?: VoiceGender // Preferred voice gender
}

// Reuse single Audio element to maintain iOS Safari "unlock" state
// On iOS, each new Audio() element requires a fresh user gesture to play.
// By reusing the same element, we keep it "unlocked" after the first user-initiated play.
let audioElement: HTMLAudioElement | null = null
let currentAudioUrl: string | null = null

/**
 * Checks if text-to-speech is supported
 */
export function isTTSSupported(): boolean {
  return typeof window !== 'undefined' && typeof Audio !== 'undefined'
}

/**
 * Gets available voices - returns empty array since Polly voices are server-side
 */
export function getVoices(): SpeechSynthesisVoice[] {
  return []
}

/**
 * Finds a voice matching the preferred gender - not used with Polly
 */
export function getVoiceByGender(
  gender: VoiceGender,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  lang: string = 'en-US'
): SpeechSynthesisVoice | null {
  return null
}

/**
 * Speaks text using Amazon Polly via backend API
 *
 * On iOS Safari, reuses a single Audio element to maintain the "unlocked" state
 * after the first user-initiated play. This prevents subsequent programmatic
 * plays from being blocked by autoplay policies.
 */
export async function speak(
  text: string,
  options: SpeechOptions = {}
): Promise<void> {
  if (!text || !text.trim()) {
    return
  }

  // Stop any ongoing speech
  stopSpeaking()

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  try {
    const response = await fetch(`${apiUrl}/api/speech/tts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: text,
        gender: options.gender || 'neutral',
      }),
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`TTS API error: ${response.status} - ${errorText}`)
    }

    // Get the audio blob
    const audioBlob = await response.blob()
    const audioUrl = URL.createObjectURL(audioBlob)

    // Clean up previous URL if exists
    if (currentAudioUrl) {
      URL.revokeObjectURL(currentAudioUrl)
    }
    currentAudioUrl = audioUrl

    // Play the audio - reuse existing element on iOS to maintain unlock state
    return new Promise((resolve, reject) => {
      // Create audio element once and reuse it
      if (!audioElement) {
        audioElement = new Audio()
      }
      const audio = audioElement

      // Set the new source
      audio.src = audioUrl
      audio.volume = options.volume ?? 1

      // Clean up handlers from any previous play
      const cleanup = () => {
        audio.onended = null
        audio.onerror = null
      }

      audio.onended = () => {
        cleanup()
        resolve()
      }

      audio.onerror = () => {
        cleanup()
        reject(new Error('Audio playback failed'))
      }

      // Load and play with retry logic for iOS
      audio.load()

      const playWithRetry = async (retriesLeft: number): Promise<void> => {
        try {
          await audio.play()
        } catch (error: unknown) {
          if (retriesLeft > 0) {
            await new Promise(r => setTimeout(r, 100))
            return playWithRetry(retriesLeft - 1)
          }
          cleanup()
          reject(new Error(`Failed to play audio: ${error instanceof Error ? error.message : 'Unknown error'}`))
        }
      }

      playWithRetry(2).catch(() => {
        // Error already handled in playWithRetry
      })
    })
  } catch (error) {
    console.error('TTS error:', error)
    throw error
  }
}

/**
 * Stops any ongoing speech
 */
export function stopSpeaking(): void {
  if (audioElement) {
    audioElement.pause()
    audioElement.currentTime = 0
    // Don't null out audioElement - keep it for reuse to maintain iOS unlock state
  }
}

/**
 * Waits for voices to be loaded - returns immediately since Polly voices are server-side
 */
export function waitForVoices(): Promise<SpeechSynthesisVoice[]> {
  return Promise.resolve([])
}
