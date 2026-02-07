'use client'

import { useState, useRef } from 'react'
import { apiClient } from '@/lib/api/client'
import { VoiceRecorder } from './VoiceRecorder'

interface MessageInputProps {
  onSend: (content: {
    text_content?: string
    photo_url?: string
    voice_url?: string
    voice_duration_seconds?: number
  }) => Promise<void>
  isSending?: boolean
  isPublic?: boolean
}

export function MessageInput({ onSend, isSending = false, isPublic = false }: MessageInputProps) {
  const [text, setText] = useState('')
  const [photoUrl, setPhotoUrl] = useState<string | null>(null)
  const [photoPreview, setPhotoPreview] = useState<string | null>(null)
  const [isUploadingPhoto, setIsUploadingPhoto] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleSend = async () => {
    if (isSending) return

    const hasContent = text.trim() || photoUrl
    if (!hasContent) return

    await onSend({
      text_content: text.trim() || undefined,
      photo_url: photoUrl || undefined
    })

    setText('')
    setPhotoUrl(null)
    setPhotoPreview(null)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleVoiceRecording = async (url: string, duration: number) => {
    await onSend({
      voice_url: url,
      voice_duration_seconds: duration
    })
  }

  const handlePhotoSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Check file type
    if (!file.type.startsWith('image/')) {
      alert('Please select an image file')
      return
    }

    // Check file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('Image must be less than 5MB')
      return
    }

    // Create preview
    const reader = new FileReader()
    reader.onload = (e) => {
      setPhotoPreview(e.target?.result as string)
    }
    reader.readAsDataURL(file)

    // Upload
    setIsUploadingPhoto(true)
    try {
      const formData = new FormData()
      formData.append('file', file)

      const uploadPath = isPublic
        ? '/api/life-words/messaging/public/upload-media?media_type=photo'
        : '/api/life-words/messaging/upload-media?media_type=photo'

      const data = await apiClient.postFormData<{ url: string }>(
        uploadPath,
        formData,
        !isPublic
      )
      setPhotoUrl(data.url)
    } catch (err) {
      console.error('Error uploading photo:', err)
      alert('Failed to upload photo')
      setPhotoPreview(null)
    } finally {
      setIsUploadingPhoto(false)
    }
  }

  const removePhoto = () => {
    setPhotoUrl(null)
    setPhotoPreview(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="border-t bg-white p-4">
      {/* Photo preview */}
      {photoPreview && (
        <div className="mb-3 relative inline-block">
          <img
            src={photoPreview}
            alt="Photo preview"
            className="h-20 rounded-lg object-cover"
          />
          {isUploadingPhoto && (
            <div className="absolute inset-0 bg-black bg-opacity-50 rounded-lg flex items-center justify-center">
              <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
            </div>
          )}
          <button
            onClick={removePhoto}
            className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
          </button>
        </div>
      )}

      <div className="flex items-end gap-2">
        {/* Photo button */}
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploadingPhoto}
          className="p-2 bg-gray-100 text-gray-600 rounded-full hover:bg-gray-200 disabled:opacity-50"
          title="Attach photo"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handlePhotoSelect}
          className="hidden"
        />

        {/* Voice recorder */}
        <VoiceRecorder
          onRecordingComplete={handleVoiceRecording}
          isPublic={isPublic}
        />

        {/* Text input */}
        <div className="flex-1 relative">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message..."
            rows={1}
            className="w-full px-4 py-2 border border-gray-300 rounded-2xl resize-none focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            style={{ maxHeight: '120px' }}
            disabled={isSending}
          />
        </div>

        {/* Send button */}
        <button
          onClick={handleSend}
          disabled={isSending || (!text.trim() && !photoUrl)}
          className="p-2 bg-blue-500 text-white rounded-full hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          title="Send message"
        >
          {isSending ? (
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
          )}
        </button>
      </div>
    </div>
  )
}
