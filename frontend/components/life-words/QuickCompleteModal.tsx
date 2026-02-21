'use client'

import { useState } from 'react'
import Image from 'next/image'

interface QuickCompleteModalProps {
  isOpen: boolean
  onClose: () => void
  onSave: (data: { name: string; relationship?: string }) => Promise<void>
  onFullEdit: () => void
  photoUrl: string
  type: 'contact' | 'item'
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

export function QuickCompleteModal({
  isOpen,
  onClose,
  onSave,
  onFullEdit,
  photoUrl,
  type,
}: QuickCompleteModalProps) {
  const [name, setName] = useState('')
  const [relationship, setRelationship] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (!isOpen) return null

  const handleSave = async () => {
    // Validate
    if (!name.trim()) {
      setError('Please enter a name')
      return
    }
    if (type === 'contact' && !relationship) {
      setError('Please select a relationship')
      return
    }

    setError(null)
    setIsSaving(true)

    try {
      await onSave({
        name: name.trim(),
        relationship: type === 'contact' ? relationship : undefined,
      })
      // Reset state
      setName('')
      setRelationship('')
      onClose()
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to save')
    } finally {
      setIsSaving(false)
    }
  }

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      onClick={handleBackdropClick}
    >
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-md overflow-hidden">
        {/* Header with photo */}
        <div className="relative h-40 bg-gray-100">
          <Image
            src={photoUrl}
            alt="Photo"
            fill
            className="object-cover"
          />
          <button
            onClick={onClose}
            className="absolute top-3 right-3 w-10 h-10 bg-white/90 hover:bg-white rounded-full flex items-center justify-center shadow-md transition-colors"
            aria-label="Close"
          >
            <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Form content */}
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            {type === 'contact' ? 'Add Name & Relationship' : 'Add Item Name'}
          </h2>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}

          <div className="space-y-4">
            {/* Name input */}
            <div>
              <label
                htmlFor="quick-name"
                className="block text-lg font-semibold text-gray-700 mb-2"
              >
                Name
              </label>
              <input
                id="quick-name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder={type === 'contact' ? "e.g., Sarah" : "e.g., Reading Glasses"}
                className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
                autoFocus
              />
            </div>

            {/* Relationship dropdown (contacts only) */}
            {type === 'contact' && (
              <div>
                <label
                  htmlFor="quick-relationship"
                  className="block text-lg font-semibold text-gray-700 mb-2"
                >
                  Relationship
                </label>
                <select
                  id="quick-relationship"
                  value={relationship}
                  onChange={(e) => setRelationship(e.target.value)}
                  className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white"
                >
                  <option value="">Select relationship...</option>
                  {RELATIONSHIP_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>

          {/* Action buttons */}
          <div className="flex flex-col gap-3 mt-6">
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="w-full py-4 bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] disabled:bg-gray-400 text-white font-bold text-lg rounded-lg transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2"
            >
              {isSaving ? 'Saving...' : 'Save'}
            </button>

            <button
              onClick={onFullEdit}
              disabled={isSaving}
              className="w-full py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold rounded-lg transition-colors"
            >
              Add More Details
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
