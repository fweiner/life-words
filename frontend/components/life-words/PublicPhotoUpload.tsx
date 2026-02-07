'use client'

import { useState, useRef, useCallback } from 'react'
import Image from 'next/image'
import { apiClient } from '@/lib/api/client'
import { compressImage } from '@/lib/utils/compressImage'

interface PublicPhotoUploadProps {
  onUploadComplete: (url: string) => void
  currentPhotoUrl?: string
  className?: string
}

/**
 * Photo upload component for public invite forms.
 * Uses the backend API endpoint instead of direct Supabase client auth.
 */
export function PublicPhotoUpload({ onUploadComplete, currentPhotoUrl, className = '' }: PublicPhotoUploadProps) {
  const [preview, setPreview] = useState<string | null>(currentPhotoUrl || null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const processFile = useCallback(async (file: File) => {
    // Validate file type
    if (!file.type.startsWith('image/')) {
      setError('Please select an image file')
      return
    }

    // Validate file size (max 10MB before compression)
    if (file.size > 10 * 1024 * 1024) {
      setError('Image must be less than 10MB')
      return
    }

    setError(null)
    setUploading(true)

    try {
      // Create preview
      const previewUrl = URL.createObjectURL(file)
      setPreview(previewUrl)

      // Compress image
      const compressedBlob = await compressImage(file)

      // Create FormData for upload
      const formData = new FormData()
      formData.append('file', compressedBlob, 'photo.jpg')

      // Upload via public API endpoint (unauthenticated)
      const data = await apiClient.postFormData<{ photo_url: string }>(
        '/api/life-words/invites/upload-photo',
        formData,
        false
      )
      onUploadComplete(data.photo_url)
    } catch (err) {
      console.error('Upload error:', err)
      setError(err instanceof Error ? err.message : 'Failed to upload image')
      setPreview(currentPhotoUrl || null)
    } finally {
      setUploading(false)
    }
  }, [currentPhotoUrl, onUploadComplete])

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      processFile(file)
    }
  }, [processFile])

  const handleClick = useCallback(() => {
    fileInputRef.current?.click()
  }, [])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const file = e.dataTransfer.files?.[0]
    if (file) {
      processFile(file)
    }
  }, [processFile])

  return (
    <div className={`flex flex-col items-center gap-4 ${className}`}>
      <button
        type="button"
        onClick={handleClick}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        disabled={uploading}
        className={`relative w-40 h-40 border-2 border-dashed rounded-lg overflow-hidden focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
          isDragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-blue-500'
        }`}
      >
        {preview ? (
          <Image
            src={preview}
            alt="Photo preview"
            fill
            className="object-cover"
          />
        ) : (
          <div className={`flex flex-col items-center justify-center h-full ${isDragging ? 'text-blue-500' : 'text-gray-500'}`}>
            <svg
              className="w-12 h-12 mb-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            <span className="text-sm text-center px-2">
              {isDragging ? 'Drop image here' : 'Click or drag image'}
            </span>
          </div>
        )}
        {uploading && (
          <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
            <div className="w-8 h-8 border-2 border-white border-t-transparent rounded-full animate-spin" />
          </div>
        )}
      </button>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileSelect}
        className="hidden"
      />

      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}

      <p className="text-xs text-gray-500 text-center">
        Upload a clear photo of yourself.<br />
        JPG or PNG, max 10MB.
      </p>
    </div>
  )
}
