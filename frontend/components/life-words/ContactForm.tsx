'use client'

import { useState } from 'react'
import { PhotoUpload } from './PhotoUpload'

export interface ContactFormData {
  name: string
  nickname: string
  pronunciation: string  // How to pronounce the name (e.g., "Wyner" for "Weiner")
  relationship: string
  photo_url: string
  category: string
  description: string
  association: string
  location_context: string
  // Personal characteristics
  interests: string
  personality: string
  values: string
  social_behavior: string
}

interface ContactFormProps {
  initialData?: Partial<ContactFormData>
  onSubmit: (data: ContactFormData) => Promise<void>
  onCancel?: () => void
  submitLabel?: string
  isSubmitting?: boolean
}

const RELATIONSHIP_OPTIONS = [
  { value: 'spouse', label: 'Spouse' },
  { value: 'partner', label: 'Partner' },
  { value: 'son', label: 'Son' },
  { value: 'daughter', label: 'Daughter' },
  { value: 'grandson', label: 'Grandson' },
  { value: 'granddaughter', label: 'Granddaughter' },
  { value: 'mother', label: 'Mother' },
  { value: 'father', label: 'Father' },
  { value: 'brother', label: 'Brother' },
  { value: 'sister', label: 'Sister' },
  { value: 'friend', label: 'Friend' },
  { value: 'pet', label: 'Pet' },
  { value: 'caregiver', label: 'Caregiver' },
  { value: 'neighbor', label: 'Neighbor' },
  { value: 'other', label: 'Other' },
]

const CATEGORY_OPTIONS = [
  { value: 'family', label: 'Family' },
  { value: 'friend', label: 'Friend' },
  { value: 'pet', label: 'Pet' },
  { value: 'place', label: 'Place' },
  { value: 'object', label: 'Object' },
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

export function ContactForm({
  initialData,
  onSubmit,
  onCancel,
  submitLabel = 'Save Contact',
  isSubmitting = false
}: ContactFormProps) {
  const [formData, setFormData] = useState<ContactFormData>({
    name: initialData?.name || '',
    nickname: initialData?.nickname || '',
    pronunciation: initialData?.pronunciation || '',
    relationship: initialData?.relationship || '',
    photo_url: initialData?.photo_url || '',
    category: initialData?.category || 'family',
    description: initialData?.description || '',
    association: initialData?.association || '',
    location_context: initialData?.location_context || '',
    // Personal characteristics
    interests: initialData?.interests || '',
    personality: initialData?.personality || '',
    values: initialData?.values || '',
    social_behavior: initialData?.social_behavior || '',
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
      setError('Name is required')
      return
    }
    if (!formData.relationship) {
      setError('Relationship is required')
      return
    }
    if (!formData.photo_url) {
      setError('Please upload a photo')
      return
    }

    try {
      await onSubmit(formData)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to save contact')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Photo Upload */}
      <div className="flex justify-center">
        <PhotoUpload
          onUploadComplete={handlePhotoUpload}
          currentPhotoUrl={formData.photo_url}
        />
      </div>

      {/* Name */}
      <div>
        <label htmlFor="name" className="block text-lg font-semibold text-gray-700 mb-2">
          Name <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          placeholder="e.g., Barbara"
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
          required
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
          placeholder="e.g., Barb, Mom"
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
        />
        <p className="text-sm text-gray-500 mt-1">What do you usually call them?</p>
      </div>

      {/* Pronunciation */}
      <div>
        <label htmlFor="pronunciation" className="block text-lg font-semibold text-gray-700 mb-2">
          Pronunciation (optional)
        </label>
        <input
          type="text"
          id="pronunciation"
          name="pronunciation"
          value={formData.pronunciation}
          onChange={handleChange}
          placeholder="e.g., Wyner (if spelled Weiner)"
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
        />
        <p className="text-sm text-gray-500 mt-1">How do you say their name? Leave blank if it&apos;s pronounced as spelled.</p>
      </div>

      {/* Relationship */}
      <div>
        <label htmlFor="relationship" className="block text-lg font-semibold text-gray-700 mb-2">
          Relationship <span className="text-red-500">*</span>
        </label>
        <select
          id="relationship"
          name="relationship"
          value={formData.relationship}
          onChange={handleChange}
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
          required
        >
          <option value="">Select relationship...</option>
          {RELATIONSHIP_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      </div>

      {/* Category */}
      <div>
        <label htmlFor="category" className="block text-lg font-semibold text-gray-700 mb-2">
          Category
        </label>
        <select
          id="category"
          name="category"
          value={formData.category}
          onChange={handleChange}
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
        >
          {CATEGORY_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      </div>

      {/* Description */}
      <div>
        <label htmlFor="description" className="block text-lg font-semibold text-gray-700 mb-2">
          Description (optional)
        </label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          placeholder="e.g., My wife of 42 years"
          rows={2}
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none resize-none"
        />
        <p className="text-sm text-gray-500 mt-1">A brief description to help you remember</p>
      </div>

      {/* Association */}
      <div>
        <label htmlFor="association" className="block text-lg font-semibold text-gray-700 mb-2">
          What do you associate with them? (optional)
        </label>
        <textarea
          id="association"
          name="association"
          value={formData.association}
          onChange={handleChange}
          placeholder="e.g., Makes the best apple pie"
          rows={2}
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none resize-none"
        />
        <p className="text-sm text-gray-500 mt-1">A memory or trait that helps you remember them</p>
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
          placeholder="e.g., Lives with me, Visits on Sundays"
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
        />
      </div>

      {/* Section Divider - Personal Characteristics */}
      <div className="border-t-2 border-gray-200 pt-6 mt-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Personal Characteristics</h3>
        <p className="text-gray-600 mb-4">These details can help provide more meaningful hints during practice.</p>
      </div>

      {/* Interests */}
      <div>
        <label htmlFor="interests" className="block text-lg font-semibold text-gray-700 mb-2">
          What are their interests? (optional)
        </label>
        <textarea
          id="interests"
          name="interests"
          value={formData.interests}
          onChange={handleChange}
          placeholder="e.g., Gardening, reading mystery novels, watching baseball"
          rows={2}
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none resize-none"
        />
        <p className="text-sm text-gray-500 mt-1">Hobbies or activities they enjoy</p>
      </div>

      {/* Personality */}
      <div>
        <label htmlFor="personality" className="block text-lg font-semibold text-gray-700 mb-2">
          What type of personality do they have? (optional)
        </label>
        <select
          id="personality"
          name="personality"
          value={formData.personality}
          onChange={handleChange}
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
        >
          <option value="">Select personality type...</option>
          {PERSONALITY_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
        <p className="text-sm text-gray-500 mt-1">Their general demeanor</p>
      </div>

      {/* Values */}
      <div>
        <label htmlFor="values" className="block text-lg font-semibold text-gray-700 mb-2">
          What do they value? (optional)
        </label>
        <textarea
          id="values"
          name="values"
          value={formData.values}
          onChange={handleChange}
          placeholder="e.g., Family time, helping others, staying active"
          rows={2}
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none resize-none"
        />
        <p className="text-sm text-gray-500 mt-1">Things that are important to them</p>
      </div>

      {/* Social Behavior */}
      <div>
        <label htmlFor="social_behavior" className="block text-lg font-semibold text-gray-700 mb-2">
          How do they behave in social situations? (optional)
        </label>
        <textarea
          id="social_behavior"
          name="social_behavior"
          value={formData.social_behavior}
          onChange={handleChange}
          placeholder="e.g., Loves to tell jokes, always asks about your day, great listener"
          rows={2}
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none resize-none"
        />
        <p className="text-sm text-gray-500 mt-1">How they interact with others</p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4">
          <p className="text-red-700 font-semibold">{error}</p>
        </div>
      )}

      {/* Buttons */}
      <div className="flex gap-4 pt-4">
        <button
          type="submit"
          disabled={isSubmitting}
          className="flex-1 bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] disabled:bg-gray-400 text-white font-bold py-4 px-6 rounded-lg text-xl transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2"
        >
          {isSubmitting ? 'Saving...' : submitLabel}
        </button>

        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={isSubmitting}
            className="px-6 py-4 bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold rounded-lg text-xl transition-colors focus:outline-none focus:ring-4 focus:ring-gray-300 focus:ring-offset-2"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  )
}
