import { getRandomPositiveFeedback } from '@/lib/utils/positiveFeedback'

describe('getRandomPositiveFeedback', () => {
  it('returns a string', () => {
    const result = getRandomPositiveFeedback()
    expect(typeof result).toBe('string')
  })

  it('returns a non-empty string', () => {
    const result = getRandomPositiveFeedback()
    expect(result.length).toBeGreaterThan(0)
  })

  it('returns one of the known positive messages', () => {
    const knownMessages = [
      'Excellent!',
      'Great job!',
      'Perfect!',
      'Well done!',
      "That's right!",
      'Fantastic!',
      'You got it!',
      'Nice work!',
      'Wonderful!',
      'Outstanding!',
      'Superb!',
      'Brilliant!',
      'Amazing!',
      'Terrific!',
      'Excellent work!',
    ]

    // Run multiple times to account for randomness
    for (let i = 0; i < 50; i++) {
      const result = getRandomPositiveFeedback()
      expect(knownMessages).toContain(result)
    }
  })

  it('produces varied results over many calls', () => {
    const results = new Set<string>()
    for (let i = 0; i < 100; i++) {
      results.add(getRandomPositiveFeedback())
    }
    // With 15 options and 100 calls, we should see at least 3 distinct values
    expect(results.size).toBeGreaterThanOrEqual(3)
  })
})
