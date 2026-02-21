'use client'

import { useState } from 'react'

interface ShareLinkModalProps {
  isOpen: boolean
  onClose: () => void
  messagingUrl: string | null
  contactName: string
}

export function ShareLinkModal({ isOpen, onClose, messagingUrl, contactName }: ShareLinkModalProps) {
  const [copied, setCopied] = useState(false)
  const canShare = typeof navigator !== 'undefined' && typeof navigator.share === 'function'

  if (!isOpen) return null

  const handleCopy = async () => {
    if (!messagingUrl) return

    try {
      await navigator.clipboard.writeText(messagingUrl)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const handleShare = async () => {
    if (!messagingUrl) return

    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Send me a message',
          text: `Use this link to send me messages in Life Words`,
          url: messagingUrl
        })
      } catch (err) {
        if ((err as Error).name !== 'AbortError') {
          console.error('Share failed:', err)
        }
      }
    } else {
      handleCopy()
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">Share Messaging Link</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded-full"
          >
            <svg className="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <p className="text-gray-600 mb-4">
          Share this link with <span className="font-semibold">{contactName}</span> so they can send you messages.
        </p>

        {messagingUrl ? (
          <>
            <div className="bg-gray-50 rounded-lg p-3 mb-4">
              <p className="text-sm text-gray-600 break-all font-mono">{messagingUrl}</p>
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleCopy}
                className={`flex-1 py-3 px-4 rounded-lg font-semibold transition-colors ${
                  copied
                    ? 'bg-green-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {copied ? 'Copied!' : 'Copy Link'}
              </button>

              {canShare && (
                <button
                  onClick={handleShare}
                  className="flex-1 py-3 px-4 bg-blue-500 text-white rounded-lg font-semibold hover:bg-blue-600"
                >
                  Share
                </button>
              )}
            </div>
          </>
        ) : (
          <div className="flex items-center justify-center py-8">
            <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        <p className="text-sm text-gray-500 mt-4">
          This link is unique to {contactName} and can be used to send you messages anytime.
        </p>
      </div>
    </div>
  )
}
