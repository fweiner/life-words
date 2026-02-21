'use client'

import { useState, useEffect, useCallback } from 'react'
import { useParams } from 'next/navigation'
import { apiClient } from '@/lib/api/client'
import { InviteContactForm, InviteFormData } from '@/components/life-words/InviteContactForm'

interface InviteStatus {
  valid: boolean
  status: 'pending' | 'completed' | 'expired' | 'not_found'
  inviter_name?: string
  recipient_name?: string
  contact_name?: string
}

export default function InvitePage() {
  const params = useParams()
  const token = params.token as string

  const [inviteStatus, setInviteStatus] = useState<InviteStatus | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isComplete, setIsComplete] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const verifyToken = useCallback(async () => {
    try {
      const data = await apiClient.getPublic<InviteStatus>(
        `/api/life-words/invites/verify/${token}`
      )
      setInviteStatus(data)
    } catch (err: unknown) {
      console.error('Error verifying invite:', err)
      setInviteStatus({
        valid: false,
        status: 'not_found'
      })
    } finally {
      setIsLoading(false)
    }
  }, [token])

  useEffect(() => {
    verifyToken()
  }, [verifyToken])

  const handleSubmit = async (formData: InviteFormData) => {
    setIsSubmitting(true)
    setError(null)

    try {
      await apiClient.postPublic(
        `/api/life-words/invites/submit/${token}`,
        formData
      )

      setIsComplete(true)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to submit form')
      throw err
    } finally {
      setIsSubmitting(false)
    }
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

  // Not found
  if (!inviteStatus || inviteStatus.status === 'not_found') {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <div className="text-6xl mb-4">&#x1F50D;</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Invite Not Found</h2>
        <p className="text-lg text-gray-600">
          This invite link doesn&apos;t exist or may have been removed.
          Please check with the person who sent you this link.
        </p>
      </div>
    )
  }

  // Expired
  if (inviteStatus.status === 'expired') {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <div className="text-6xl mb-4">&#x23F0;</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Invite Expired</h2>
        <p className="text-lg text-gray-600">
          This invite link has expired. Please contact{' '}
          {inviteStatus.inviter_name || 'the person who sent you this link'}{' '}
          to request a new invite.
        </p>
      </div>
    )
  }

  // Already completed
  if (inviteStatus.status === 'completed') {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <div className="text-6xl mb-4">&#x2705;</div>
        <h2 className="text-2xl font-bold text-green-600 mb-4">Already Submitted</h2>
        <p className="text-lg text-gray-600 mb-4">
          Your information has already been submitted and added to{' '}
          {inviteStatus.inviter_name ? `${inviteStatus.inviter_name}&apos;s` : 'their'} contact list.
        </p>
        {inviteStatus.contact_name && (
          <p className="text-gray-500">
            Contact name: <strong>{inviteStatus.contact_name}</strong>
          </p>
        )}
        <p className="text-gray-500 mt-4">
          Thank you for your support in their memory recovery journey!
        </p>
      </div>
    )
  }

  // Success - just submitted
  if (isComplete) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <div className="text-6xl mb-4">&#x1F389;</div>
        <h2 className="text-2xl font-bold text-green-600 mb-4">Thank You!</h2>
        <p className="text-lg text-gray-600 mb-4">
          Your information has been successfully added to{' '}
          {inviteStatus.inviter_name ? `${inviteStatus.inviter_name}'s` : 'their'} contact list.
        </p>
        <p className="text-gray-500">
          You should receive a confirmation email shortly.
        </p>
        <div className="mt-8 p-6 bg-blue-50 rounded-lg">
          <p className="text-blue-800">
            Your support means so much. By helping with memory practice,
            you&apos;re making a real difference in their rehabilitation journey.
          </p>
        </div>
      </div>
    )
  }

  // Valid invite - show form
  const inviterFirstName = inviteStatus.inviter_name?.split(' ')[0] || 'someone'

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Help {inviterFirstName} with Memory Recovery
          </h2>
          <p className="text-lg text-gray-600">
            {inviteStatus.inviter_name || 'Someone'} has asked you to help with their memory rehabilitation.
            By adding your photo and information, you&apos;ll become part of their practice exercises.
          </p>
        </div>

        <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-8">
          <p className="text-blue-800">
            <strong>Why this matters:</strong> Memory rehabilitation works best with familiar faces.
            Your information will help {inviterFirstName} practice recognizing and naming
            the important people in their life.
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4 mb-6">
            <p className="text-red-700 font-semibold">{error}</p>
          </div>
        )}

        <InviteContactForm
          initialName={inviteStatus.recipient_name || ''}
          onSubmit={handleSubmit}
          isSubmitting={isSubmitting}
        />
      </div>
    </div>
  )
}
