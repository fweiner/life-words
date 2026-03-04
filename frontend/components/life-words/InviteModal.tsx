'use client'

import { useState } from 'react'
import { apiClient } from '@/lib/api/client'

interface InviteModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess?: () => void
}

const NAME_PLACEHOLDER = "--insert user's name--"

function getDefaultMessage(): string {
  return `As you are probably aware, ${NAME_PLACEHOLDER} is being treated for speech and memory. As part of treatment we are talking about friends, relatives, pets, and objects in the environment. We would appreciate that you click this link that will take you to a page where you can add a photo of yourself and answer a few basic questions. This information will be added to ${NAME_PLACEHOLDER}'s contact list to help with rehabilitation.`
}

export function InviteModal({ isOpen, onClose, onSuccess }: InviteModalProps) {
  const [recipientName, setRecipientName] = useState('')
  const [recipientEmail, setRecipientEmail] = useState('')
  const [customMessage, setCustomMessage] = useState(getDefaultMessage)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)

    try {
      await apiClient.post('/api/life-words/invites', {
        recipient_name: recipientName,
        recipient_email: recipientEmail,
        custom_message: customMessage
      })

      setSuccess(true)
      onSuccess?.()

      // Reset form after a delay and close
      setTimeout(() => {
        setRecipientName('')
        setRecipientEmail('')
        setCustomMessage(getDefaultMessage())
        setSuccess(false)
        onClose()
      }, 2000)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to send invite')
    } finally {
      setIsLoading(false)
    }
  }

  const handleClose = () => {
    if (!isLoading) {
      setRecipientName('')
      setRecipientEmail('')
      setCustomMessage(getDefaultMessage())
      setError(null)
      setSuccess(false)
      onClose()
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">
              Invite Someone to Help
            </h2>
            <button
              onClick={handleClose}
              disabled={isLoading}
              className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
            >
              &times;
            </button>
          </div>

          {success ? (
            <div className="text-center py-8">
              <div className="text-5xl mb-4">&#x2709;</div>
              <h3 className="text-xl font-semibold text-green-600 mb-2">
                Invite Sent!
              </h3>
              <p className="text-gray-600">
                We&apos;ve sent an email to {recipientName} at {recipientEmail}.
                They&apos;ll receive instructions to add their photo and information.
              </p>
            </div>
          ) : (
            <>
              <p className="text-gray-600 mb-6">
                Send an email invitation to someone you know. They&apos;ll be able to add their
                photo and information directly, which will be added to your contacts list.
              </p>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label htmlFor="recipientName" className="block text-lg font-semibold text-gray-700 mb-2">
                    Their Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    id="recipientName"
                    value={recipientName}
                    onChange={(e) => setRecipientName(e.target.value)}
                    placeholder="e.g., Barbara Smith"
                    className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
                    required
                    disabled={isLoading}
                  />
                </div>

                <div>
                  <label htmlFor="recipientEmail" className="block text-lg font-semibold text-gray-700 mb-2">
                    Their Email <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="email"
                    id="recipientEmail"
                    value={recipientEmail}
                    onChange={(e) => setRecipientEmail(e.target.value)}
                    placeholder="e.g., barbara@email.com"
                    className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
                    required
                    disabled={isLoading}
                  />
                </div>

                <div>
                  <label htmlFor="customMessage" className="block text-lg font-semibold text-gray-700 mb-2">
                    Personal Message <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    id="customMessage"
                    value={customMessage}
                    onChange={(e) => setCustomMessage(e.target.value)}
                    placeholder="Add a personal note to your invitation..."
                    rows={6}
                    className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none resize-none"
                    disabled={isLoading}
                    required
                  />
                  <p className="text-sm text-red-500 mt-1">
                    Make sure you replace --insert user&apos;s name-- with the name of the user.
                  </p>
                </div>

                {error && (
                  <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4">
                    <p className="text-red-700 font-semibold">{error}</p>
                  </div>
                )}

                <div className="flex gap-4 pt-4">
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="flex-1 bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] disabled:bg-gray-400 text-white font-bold py-4 px-6 rounded-lg text-xl transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                  >
                    {isLoading ? 'Sending...' : 'Send Invite'}
                  </button>
                  <button
                    type="button"
                    onClick={handleClose}
                    disabled={isLoading}
                    className="px-6 py-4 bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold rounded-lg text-xl transition-colors focus:outline-none focus:ring-4 focus:ring-gray-300 focus:ring-offset-2"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
