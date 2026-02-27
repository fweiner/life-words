'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { apiClient, ApiError } from '@/lib/api/client'
import { ContactForm, ContactFormData } from '@/components/life-words/ContactForm'
import Link from 'next/link'

export const dynamic = 'force-dynamic'

interface ContactData {
  id: string
  name: string
  nickname?: string
  pronunciation?: string
  relationship: string
  photo_url: string
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

export default function EditContactPage() {
  const router = useRouter()
  const params = useParams()
  const contactId = params.id as string

  const [contact, setContact] = useState<ContactData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadContact = useCallback(async () => {
    try {
      const data = await apiClient.get<ContactData>(`/api/life-words/contacts/${contactId}`)
      setContact(data)
    } catch (err: unknown) {
      if (err instanceof ApiError && err.status === 404) {
        setError('Contact not found')
      } else {
        const e = err as Record<string, unknown>
        setError((e.detail as string) || (e.message as string) || 'An error occurred')
      }
      console.error('Error loading contact:', err)
    } finally {
      setIsLoading(false)
    }
  }, [contactId])

  useEffect(() => {
    loadContact()
  }, [loadContact])

  const handleSubmit = async (formData: ContactFormData) => {
    setIsSaving(true)
    setError(null)

    try {
      await apiClient.put(`/api/life-words/contacts/${contactId}`, formData)

      // Redirect back to contacts list
      router.push('/dashboard/practice/contacts')
    } catch (err: unknown) {
      const e = err as Record<string, unknown>
      setError((e.detail as string) || (e.message as string) || 'Failed to update contact')
      throw err
    } finally {
      setIsSaving(false)
    }
  }

  const handleCancel = () => {
    router.push('/dashboard/practice/contacts')
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-xl text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (!contact) {
    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow-md p-8">
          <div className="text-center py-12">
            <div className="text-6xl mb-4">❌</div>
            <p className="text-xl text-gray-600 mb-4">{error || 'Contact not found'}</p>
            <Link
              href="/dashboard/practice/contacts"
              className="text-[var(--color-primary)] hover:underline"
            >
              ← Back to Contacts
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Edit Contact
            </h1>
            <p className="text-lg text-gray-600 mt-1">
              Update {contact.name}&apos;s information.
            </p>
          </div>
          <Link
            href="/dashboard/practice/contacts"
            className="text-[var(--color-primary)] hover:underline"
          >
            ← Back to Contacts
          </Link>
        </div>

        {error && (
          <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4 mb-6">
            <p className="text-red-700 font-semibold">{error}</p>
          </div>
        )}

        <div className="max-w-xl mx-auto">
          <ContactForm
            initialData={{
              name: contact.name,
              nickname: contact.nickname || '',
              pronunciation: contact.pronunciation || '',
              relationship: contact.relationship,
              photo_url: contact.photo_url,
              category: contact.category || 'family',
              description: contact.description || '',
              association: contact.association || '',
              location_context: contact.location_context || '',
              // Personal characteristics
              interests: contact.interests || '',
              personality: contact.personality || '',
              values: contact.values || '',
              social_behavior: contact.social_behavior || '',
            }}
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            submitLabel="Save Changes"
            isSubmitting={isSaving}
          />
        </div>
      </div>
    </div>
  )
}
