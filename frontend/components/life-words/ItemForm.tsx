'use client'

import { useState } from 'react'
import { PhotoUpload } from './PhotoUpload'

export interface ItemFormData {
  name: string
  pronunciation: string  // How to pronounce the name
  photo_url: string
  purpose: string
  features: string
  category: string
  size: string
  shape: string
  color: string
  weight: string
  location: string
  associated_with: string
}

interface ItemFormProps {
  initialData?: Partial<ItemFormData>
  onSubmit: (data: ItemFormData) => Promise<void>
  onCancel?: () => void
  submitLabel?: string
  isSubmitting?: boolean
}

const CATEGORY_OPTIONS = [
  { value: 'household', label: 'Household Item' },
  { value: 'electronics', label: 'Electronics' },
  { value: 'clothing', label: 'Clothing' },
  { value: 'vehicle', label: 'Vehicle' },
  { value: 'tool', label: 'Tool' },
  { value: 'furniture', label: 'Furniture' },
  { value: 'appliance', label: 'Appliance' },
  { value: 'food', label: 'Food' },
  { value: 'personal', label: 'Personal Item' },
  { value: 'other', label: 'Other' },
]

export function ItemForm({
  initialData,
  onSubmit,
  onCancel,
  submitLabel = 'Save Item',
  isSubmitting = false
}: ItemFormProps) {
  const [formData, setFormData] = useState<ItemFormData>({
    name: initialData?.name || '',
    pronunciation: initialData?.pronunciation || '',
    photo_url: initialData?.photo_url || '',
    purpose: initialData?.purpose || '',
    features: initialData?.features || '',
    category: initialData?.category || '',
    size: initialData?.size || '',
    shape: initialData?.shape || '',
    color: initialData?.color || '',
    weight: initialData?.weight || '',
    location: initialData?.location || '',
    associated_with: initialData?.associated_with || '',
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
    if (!formData.photo_url) {
      setError('Please upload a photo')
      return
    }

    // Count how many description fields are filled
    const descriptionFields = [
      formData.purpose,
      formData.features,
      formData.category,
      formData.size,
      formData.shape,
      formData.color,
      formData.weight,
      formData.location,
      formData.associated_with,
    ]
    const filledDescriptions = descriptionFields.filter(field => field && field.trim()).length
    if (filledDescriptions < 6) {
      setError(`Please fill in at least 6 description fields. You've filled ${filledDescriptions} so far. These descriptions are used as hints during practice.`)
      return
    }

    try {
      await onSubmit(formData)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to save item')
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
          placeholder="e.g., Coffee Mug, Television, Car Keys"
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
          required
        />
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
          placeholder="e.g., Wy-ner (if spelled Weiner)"
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
        />
        <p className="text-sm text-gray-500 mt-1">How do you say this item&apos;s name? Leave blank if it&apos;s pronounced as spelled.</p>
      </div>

      {/* Description Fields Notice */}
      <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4">
        <p className="text-blue-800 font-semibold">
          Please fill in at least 6 of the description fields below. These are used as hints during practice.
        </p>
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
          <option value="">Select category...</option>
          {CATEGORY_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      </div>

      {/* Purpose */}
      <div>
        <label htmlFor="purpose" className="block text-lg font-semibold text-gray-700 mb-2">
          Purpose
        </label>
        <textarea
          id="purpose"
          name="purpose"
          value={formData.purpose}
          onChange={handleChange}
          placeholder="e.g., Used for drinking coffee in the morning"
          rows={2}
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none resize-none"
        />
        <p className="text-sm text-gray-500 mt-1">What is this item used for?</p>
      </div>

      {/* Features */}
      <div>
        <label htmlFor="features" className="block text-lg font-semibold text-gray-700 mb-2">
          Features
        </label>
        <textarea
          id="features"
          name="features"
          value={formData.features}
          onChange={handleChange}
          placeholder="e.g., Has a handle, holds hot liquids, microwave safe"
          rows={2}
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none resize-none"
        />
        <p className="text-sm text-gray-500 mt-1">Notable features or characteristics</p>
      </div>

      {/* Physical Properties Section */}
      <div className="border-t-2 border-gray-200 pt-6 mt-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Physical Properties</h3>
      </div>

      {/* Size */}
      <div>
        <label htmlFor="size" className="block text-lg font-semibold text-gray-700 mb-2">
          Size
        </label>
        <input
          type="text"
          id="size"
          name="size"
          value={formData.size}
          onChange={handleChange}
          placeholder="e.g., Small, Medium, Large, 12 inches"
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
        />
      </div>

      {/* Shape */}
      <div>
        <label htmlFor="shape" className="block text-lg font-semibold text-gray-700 mb-2">
          Shape
        </label>
        <input
          type="text"
          id="shape"
          name="shape"
          value={formData.shape}
          onChange={handleChange}
          placeholder="e.g., Round, Square, Rectangular, Cylindrical"
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
        />
      </div>

      {/* Color */}
      <div>
        <label htmlFor="color" className="block text-lg font-semibold text-gray-700 mb-2">
          Color
        </label>
        <input
          type="text"
          id="color"
          name="color"
          value={formData.color}
          onChange={handleChange}
          placeholder="e.g., Blue, Red and white, Silver"
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
        />
      </div>

      {/* Weight */}
      <div>
        <label htmlFor="weight" className="block text-lg font-semibold text-gray-700 mb-2">
          Weight
        </label>
        <input
          type="text"
          id="weight"
          name="weight"
          value={formData.weight}
          onChange={handleChange}
          placeholder="e.g., Light, Heavy, 2 pounds"
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
        />
      </div>

      {/* Location & Context Section */}
      <div className="border-t-2 border-gray-200 pt-6 mt-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Location & Context</h3>
      </div>

      {/* Location */}
      <div>
        <label htmlFor="location" className="block text-lg font-semibold text-gray-700 mb-2">
          Location
        </label>
        <input
          type="text"
          id="location"
          name="location"
          value={formData.location}
          onChange={handleChange}
          placeholder="e.g., Kitchen counter, Living room, Garage"
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
        />
        <p className="text-sm text-gray-500 mt-1">Where is this item usually found?</p>
      </div>

      {/* Associated With */}
      <div>
        <label htmlFor="associated_with" className="block text-lg font-semibold text-gray-700 mb-2">
          Associated With
        </label>
        <textarea
          id="associated_with"
          name="associated_with"
          value={formData.associated_with}
          onChange={handleChange}
          placeholder="e.g., Morning routine, My husband, Watching TV"
          rows={2}
          className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none resize-none"
        />
        <p className="text-sm text-gray-500 mt-1">People, activities, or memories connected to this item</p>
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
