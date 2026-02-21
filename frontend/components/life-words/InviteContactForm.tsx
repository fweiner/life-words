'use client'

import { useState } from 'react'
import { PublicPhotoUpload } from './PublicPhotoUpload'

export interface InviteFormData {
  name: string
  nickname: string
  relationship: string
  photo_url: string
  category: string
  description: string
  association: string
  location_context: string
  interests: string
  personality: string
  values: string
  social_behavior: string
}

interface InviteContactFormProps {
  initialName?: string
  onSubmit: (data: InviteFormData) => Promise<void>
  isSubmitting?: boolean
}

const RELATIONSHIP_OPTIONS = [
  { value: 'spouse', label: 'Spouse/Partner' },
  { value: 'child', label: 'Son/Daughter' },
  { value: 'grandchild', label: 'Grandchild' },
  { value: 'parent', label: 'Parent' },
  { value: 'sibling', label: 'Brother/Sister' },
  { value: 'friend', label: 'Friend' },
  { value: 'pet', label: 'Pet' },
  { value: 'caregiver', label: 'Caregiver' },
  { value: 'neighbor', label: 'Neighbor' },
  { value: 'other', label: 'Other' },
]

const PERSONALITY_OPTIONS = [
  { value: 'outgoing', label: 'Outgoing' },
  { value: 'reserved', label: 'Reserved' },
  { value: 'optimistic', label: 'Optimistic' },
  { value: 'cautious', label: 'Cautious' },
  { value: 'friendly', label: 'Friendly' },
  { value: 'quiet', label: 'Quiet' },
  { value: 'energetic', label: 'Energetic' },
  { value: 'calm', label: 'Calm' },
]

export function InviteContactForm({
  initialName = '',
  onSubmit,
  isSubmitting = false
}: InviteContactFormProps) {
  const [formData, setFormData] = useState<InviteFormData>({
    name: initialName,
    nickname: '',
    relationship: '',
    photo_url: '',
    category: 'family',
    description: '',
    association: '',
    location_context: '',
    interests: '',
    personality: '',
    values: '',
    social_behavior: '',
  })
  const [error, setError] = useState<string | null>(null)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handlePhotoUpload = (url: string) => {
    setFormData(prev => ({ ...prev, photo_url: url }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    // Validate required fields
    if (!formData.name.trim()) {
      setError('Your name is required')
      return
    }
    if (!formData.relationship) {
      setError('Please select your relationship')
      return
    }
    if (!formData.photo_url) {
      setError('Please upload a photo')
      return
    }

    try {
      await onSubmit(formData)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to submit form')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Photo Upload */}
      <div className="flex flex-col items-center">
        <h3 className="text-lg font-semibold text-gray-700 mb-4">
          Your Photo <span className="text-red-500">*</span>
        </h3>
        <PublicPhotoUpload
          onUploadComplete={handlePhotoUpload}
          currentPhotoUrl={formData.photo_url}
        />
      </div>

      {/* Name */}
      <div>
        <label htmlFor="name" className="block text-lg font-semibold text-gray-700 mb-2">
          Your Name <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          placeholder="e.g., Barbara Smith"
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
          required
          disabled={isSubmitting}
        />
      </div>

      {/* Nickname */}
      <div>
        <label htmlFor="nickname" className="block text-lg font-semibold text-gray-700 mb-2">
          Nickname (optional)
        </label>
        <input
          type="text"
          id="nickname"
          name="nickname"
          value={formData.nickname}
          onChange={handleChange}
          placeholder="e.g., Barb, Mom, Grandma"
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
          disabled={isSubmitting}
        />
        <p className="text-sm text-gray-500 mt-1">What do they usually call you?</p>
      </div>

      {/* Relationship */}
      <div>
        <label htmlFor="relationship" className="block text-lg font-semibold text-gray-700 mb-2">
          Your Relationship <span className="text-red-500">*</span>
        </label>
        <select
          id="relationship"
          name="relationship"
          value={formData.relationship}
          onChange={handleChange}
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
          required
          disabled={isSubmitting}
        >
          <option value="">Select your relationship...</option>
          {RELATIONSHIP_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
        <p className="text-sm text-gray-500 mt-1">How are you related to them?</p>
      </div>

      {/* Description */}
      <div>
        <label htmlFor="description" className="block text-lg font-semibold text-gray-700 mb-2">
          Brief Description (optional)
        </label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          placeholder="e.g., Their daughter who lives in Chicago"
          rows={2}
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none resize-none"
          disabled={isSubmitting}
        />
      </div>

      {/* Association */}
      <div>
        <label htmlFor="association" className="block text-lg font-semibold text-gray-700 mb-2">
          What might they associate with you? (optional)
        </label>
        <textarea
          id="association"
          name="association"
          value={formData.association}
          onChange={handleChange}
          placeholder="e.g., We always go fishing together, I bring apple pie"
          rows={2}
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none resize-none"
          disabled={isSubmitting}
        />
        <p className="text-sm text-gray-500 mt-1">A memory or activity that connects you</p>
      </div>

      {/* Location Context */}
      <div>
        <label htmlFor="location_context" className="block text-lg font-semibold text-gray-700 mb-2">
          Where do you usually see them? (optional)
        </label>
        <input
          type="text"
          id="location_context"
          name="location_context"
          value={formData.location_context}
          onChange={handleChange}
          placeholder="e.g., Visit on weekends, Live next door"
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
          disabled={isSubmitting}
        />
      </div>

      {/* Section Divider - Personal Characteristics */}
      <div className="border-t-2 border-gray-200 pt-6 mt-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">About You</h3>
        <p className="text-gray-600 mb-4">These details help provide meaningful hints during practice sessions.</p>
      </div>

      {/* Interests */}
      <div>
        <label htmlFor="interests" className="block text-lg font-semibold text-gray-700 mb-2">
          What are your interests? (optional)
        </label>
        <textarea
          id="interests"
          name="interests"
          value={formData.interests}
          onChange={handleChange}
          placeholder="e.g., Gardening, reading, cooking Italian food"
          rows={2}
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none resize-none"
          disabled={isSubmitting}
        />
      </div>

      {/* Personality */}
      <div>
        <label htmlFor="personality" className="block text-lg font-semibold text-gray-700 mb-2">
          How would you describe your personality? (optional)
        </label>
        <select
          id="personality"
          name="personality"
          value={formData.personality}
          onChange={handleChange}
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
          disabled={isSubmitting}
        >
          <option value="">Select personality type...</option>
          {PERSONALITY_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      </div>

      {/* Values */}
      <div>
        <label htmlFor="values" className="block text-lg font-semibold text-gray-700 mb-2">
          What do you value most? (optional)
        </label>
        <textarea
          id="values"
          name="values"
          value={formData.values}
          onChange={handleChange}
          placeholder="e.g., Family time, helping others, honesty"
          rows={2}
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none resize-none"
          disabled={isSubmitting}
        />
      </div>

      {/* Social Behavior */}
      <div>
        <label htmlFor="social_behavior" className="block text-lg font-semibold text-gray-700 mb-2">
          How do you behave around them? (optional)
        </label>
        <textarea
          id="social_behavior"
          name="social_behavior"
          value={formData.social_behavior}
          onChange={handleChange}
          placeholder="e.g., I always make them laugh, I love to cook for them"
          rows={2}
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none resize-none"
          disabled={isSubmitting}
        />
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4">
          <p className="text-red-700 font-semibold">{error}</p>
        </div>
      )}

      {/* Submit Button */}
      <div className="pt-4">
        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] disabled:bg-gray-400 text-white font-bold py-4 px-6 rounded-lg text-xl transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2"
        >
          {isSubmitting ? 'Submitting...' : 'Submit My Information'}
        </button>
      </div>
    </form>
  )
}
