'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api/client'
import { ContactForm, ContactFormData } from '@/components/life-words/ContactForm'
import { ContactCard, Contact } from '@/components/life-words/ContactCard'
import Link from 'next/link'

export const dynamic = 'force-dynamic'

const MIN_CONTACTS = 2

export default function LifeWordsSetupPage() {
  const [contacts, setContacts] = useState<Contact[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadContacts()
  }, [])

  const loadContacts = async () => {
    try {
      const data = await apiClient.get<Contact[]>('/api/life-words/contacts')
      setContacts(data)

      // Show form automatically if no contacts yet
      if (data.length === 0) {
        setShowForm(true)
      }
    } catch (err: unknown) {
      const e = err as Record<string, unknown>
      setError((e.message as string) || 'An error occurred')
      console.error('Error loading contacts:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleAddContact = async (formData: ContactFormData) => {
    setIsSaving(true)
    setError(null)

    try {
      const newContact = await apiClient.post<Contact>('/api/life-words/contacts', formData)
      setContacts(prev => [newContact, ...prev])
      setShowForm(false)
    } catch (err: unknown) {
      const e = err as Record<string, unknown>
      setError((e.message as string) || 'Failed to add contact')
      throw err
    } finally {
      setIsSaving(false)
    }
  }

  const handleDeleteContact = async (contactId: string) => {
    try {
      await apiClient.delete(`/api/life-words/contacts/${contactId}`)
      setContacts(prev => prev.filter(c => c.id !== contactId))
    } catch (err: unknown) {
      const e = err as Record<string, unknown>
      setError((e.message as string) || 'Failed to delete contact')
    }
  }

  const canStartPractice = contacts.length >= MIN_CONTACTS

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

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Set Up Your Life Words and Memory
            </h1>
            <p className="text-lg text-gray-600 mt-1">
              Add the people and things that matter most to you.
            </p>
          </div>
          <Link
            href="/dashboard/treatments/life-words"
            className="text-[var(--color-primary)] hover:underline"
          >
            ← Back
          </Link>
        </div>

        {/* Progress indicator */}
        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-lg font-semibold text-gray-700">
              {contacts.length} of {MIN_CONTACTS} contacts added
            </span>
            {canStartPractice ? (
              <span className="text-green-600 font-semibold">Ready to practice!</span>
            ) : (
              <span className="text-amber-600 font-semibold">
                Add {MIN_CONTACTS - contacts.length} more to start
              </span>
            )}
          </div>
          <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
            <div
              className={`h-full transition-all duration-300 ${canStartPractice ? 'bg-green-500' : 'bg-amber-500'}`}
              style={{ width: `${Math.min(100, (contacts.length / MIN_CONTACTS) * 100)}%` }}
            />
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4 mb-6">
            <p className="text-red-700 font-semibold">{error}</p>
          </div>
        )}

        {/* Add new contact form */}
        {showForm ? (
          <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-6 mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Add a New Contact
            </h2>
            <ContactForm
              onSubmit={handleAddContact}
              onCancel={() => setShowForm(false)}
              submitLabel="Add Contact"
              isSubmitting={isSaving}
            />
          </div>
        ) : (
          <button
            onClick={() => setShowForm(true)}
            className="w-full py-4 px-6 bg-blue-50 hover:bg-blue-100 border-2 border-dashed border-blue-300 rounded-lg text-blue-600 font-semibold text-lg transition-colors mb-6"
          >
            + Add Another Contact
          </button>
        )}

        {/* Existing contacts */}
        {contacts.length > 0 && (
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Your Contacts ({contacts.length})
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {contacts.map(contact => (
                <ContactCard
                  key={contact.id}
                  contact={contact}
                  onDelete={handleDeleteContact}
                />
              ))}
            </div>
          </div>
        )}

        {/* Action buttons */}
        <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
          {canStartPractice && (
            <Link
              href="/dashboard/treatments/life-words"
              className="bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-bold py-4 px-8 rounded-lg text-xl transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2 text-center"
            >
              Done - Start Practicing!
            </Link>
          )}
        </div>
      </div>
    </div>
  )
}
