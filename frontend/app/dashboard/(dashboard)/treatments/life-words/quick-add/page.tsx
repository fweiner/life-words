'use client'

import { useState, useRef, useCallback, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase'
import { apiClient } from '@/lib/api/client'
import Image from 'next/image'
import Link from 'next/link'

export const dynamic = 'force-dynamic'

interface AddedPhoto {
  id: string
  photoUrl: string
  type: 'contact' | 'item'
}

type Step = 'capture' | 'preview' | 'type-select'

export default function QuickAddPage() {
  const router = useRouter()
  const [step, setStep] = useState<Step>('capture')
  const [currentPhoto, setCurrentPhoto] = useState<string | null>(null)
  const [addedPhotos, setAddedPhotos] = useState<AddedPhoto[]>([])
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isMobile, setIsMobile] = useState(false)

  const fileInputRef = useRef<HTMLInputElement>(null)
  const cameraInputRef = useRef<HTMLInputElement>(null)
  const supabase = createClient()

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent))
    }
    checkMobile()
  }, [])

  const compressImage = useCallback(async (file: File): Promise<Blob> => {
    return new Promise((resolve, reject) => {
      const img = document.createElement('img')
      img.onload = () => {
        const canvas = document.createElement('canvas')
        const ctx = canvas.getContext('2d')
        if (!ctx) {
          reject(new Error('Could not get canvas context'))
          return
        }

        const maxWidth = 800
        const maxHeight = 800
        let { width, height } = img

        if (width > maxWidth || height > maxHeight) {
          const ratio = Math.min(maxWidth / width, maxHeight / height)
          width = Math.round(width * ratio)
          height = Math.round(height * ratio)
        }

        canvas.width = width
        canvas.height = height
        ctx.drawImage(img, 0, 0, width, height)

        canvas.toBlob(
          (blob) => {
            if (blob) {
              resolve(blob)
            } else {
              reject(new Error('Could not compress image'))
            }
          },
          'image/jpeg',
          0.8
        )
      }
      img.onerror = () => reject(new Error('Could not load image'))
      img.src = URL.createObjectURL(file)
    })
  }, [])

  const uploadPhoto = useCallback(async (blob: Blob): Promise<string> => {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) throw new Error('Not authenticated')

    const timestamp = Date.now()
    const fileName = `${user.id}/quick-add/${timestamp}.jpg`

    const { data, error: uploadError } = await supabase.storage
      .from('user-uploads')
      .upload(fileName, blob, {
        contentType: 'image/jpeg',
        upsert: true
      })

    if (uploadError) throw uploadError

    const { data: { publicUrl } } = supabase.storage
      .from('user-uploads')
      .getPublicUrl(data.path)

    return publicUrl
  }, [supabase])

  const processFile = useCallback(async (file: File) => {
    if (!file.type.startsWith('image/')) {
      setError('Please select an image file')
      return
    }

    if (file.size > 10 * 1024 * 1024) {
      setError('Image must be less than 10MB')
      return
    }

    setError(null)

    try {
      const previewUrl = URL.createObjectURL(file)
      setCurrentPhoto(previewUrl)
      setStep('preview')
    } catch (err) {
      console.error('Error processing file:', err)
      setError('Failed to process image')
    }
  }, [])

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      processFile(file)
    }
    // Reset input so same file can be selected again
    e.target.value = ''
  }, [processFile])

  const handleTakePhoto = useCallback(() => {
    cameraInputRef.current?.click()
  }, [])

  const handleChooseFromLibrary = useCallback(() => {
    fileInputRef.current?.click()
  }, [])

  const handleRetake = useCallback(() => {
    if (currentPhoto) {
      URL.revokeObjectURL(currentPhoto)
    }
    setCurrentPhoto(null)
    setStep('capture')
  }, [currentPhoto])

  const handleKeep = useCallback(() => {
    setStep('type-select')
  }, [])

  const handleTypeSelect = useCallback(async (type: 'contact' | 'item') => {
    if (!currentPhoto) return

    setIsSaving(true)
    setError(null)

    try {
      // Fetch the blob from the preview URL and compress it
      const response = await fetch(currentPhoto)
      const blob = await response.blob()
      const file = new File([blob], 'photo.jpg', { type: 'image/jpeg' })
      const compressedBlob = await compressImage(file)

      // Upload to storage
      const photoUrl = await uploadPhoto(compressedBlob)

      // Save to backend
      const path = type === 'contact'
        ? '/api/life-words/contacts/quick-add'
        : '/api/life-words/items/quick-add'

      const body = type === 'contact'
        ? { photo_url: photoUrl, category: 'family' }
        : { photo_url: photoUrl }

      const savedEntry = await apiClient.post<{ id: string }>(path, body)

      // Add to local state
      setAddedPhotos(prev => [...prev, {
        id: savedEntry.id,
        photoUrl: photoUrl,
        type: type,
      }])

      // Clean up and go back to capture
      URL.revokeObjectURL(currentPhoto)
      setCurrentPhoto(null)
      setStep('capture')

    } catch (err: unknown) {
      console.error('Error saving photo:', err)
      const e = err as Record<string, unknown>
      setError((e.message as string) || 'Failed to save photo')
    } finally {
      setIsSaving(false)
    }
  }, [currentPhoto, compressImage, uploadPhoto])

  const handleDone = useCallback(() => {
    router.push('/dashboard/treatments/life-words')
  }, [router])

  // Render capture step
  if (step === 'capture') {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col">
        {/* Header */}
        <div className="bg-white shadow-sm p-4">
          <div className="flex items-center justify-between mb-2">
            <Link
              href="/dashboard/treatments/life-words"
              className="text-[var(--color-primary)] font-semibold text-lg"
            >
              Cancel
            </Link>
            <button
              onClick={handleDone}
              className="text-[var(--color-primary)] font-semibold text-lg"
            >
              Done
            </button>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 text-center">Quick Add Photos</h1>
        </div>

        {/* Added photos gallery */}
        {addedPhotos.length > 0 && (
          <div className="bg-white border-b p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-green-600 font-bold text-lg">
                {addedPhotos.length} photo{addedPhotos.length !== 1 ? 's' : ''} added
              </span>
            </div>
            <div className="flex gap-2 overflow-x-auto pb-2">
              {addedPhotos.map((photo) => (
                <div
                  key={photo.id}
                  className="relative w-16 h-16 flex-shrink-0 rounded-lg overflow-hidden border-2 border-green-400"
                >
                  <Image
                    src={photo.photoUrl}
                    alt="Added"
                    fill
                    className="object-cover"
                  />
                  <div className={`absolute bottom-0 left-0 right-0 text-center text-xs font-bold py-0.5 ${
                    photo.type === 'contact' ? 'bg-blue-500 text-white' : 'bg-amber-500 text-white'
                  }`}>
                    {photo.type === 'contact' ? 'Person' : 'Thing'}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Main capture area */}
        <div className="flex-1 flex flex-col items-center justify-center p-6">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 w-full max-w-md">
              <p className="text-red-600 text-center">{error}</p>
            </div>
          )}

          <div className="text-center mb-8">
            <div className="text-6xl mb-4">
              {addedPhotos.length === 0 ? '📸' : '➕'}
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              {addedPhotos.length === 0 ? 'Add Your First Photo' : 'Add Another Photo'}
            </h2>
            <p className="text-lg text-gray-600">
              Take a photo or choose one from your library
            </p>
          </div>

          {/* Capture buttons */}
          <div className="flex flex-col gap-4 w-full max-w-sm">
            {isMobile && (
              <button
                onClick={handleTakePhoto}
                className="flex items-center justify-center gap-3 py-6 px-8 bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-bold text-xl rounded-xl transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                style={{ minHeight: '80px' }}
              >
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                Take Photo
              </button>
            )}

            <button
              onClick={handleChooseFromLibrary}
              className={`flex items-center justify-center gap-3 py-6 px-8 font-bold text-xl rounded-xl transition-colors focus:outline-none focus:ring-4 focus:ring-offset-2 ${
                isMobile
                  ? 'bg-white border-2 border-gray-300 hover:border-gray-400 text-gray-700 focus:ring-gray-300'
                  : 'bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white focus:ring-[var(--color-primary)]'
              }`}
              style={{ minHeight: '80px' }}
            >
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              Choose from Library
            </button>
          </div>

          {/* Hidden file inputs */}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
          />
          <input
            ref={cameraInputRef}
            type="file"
            accept="image/*"
            capture="environment"
            onChange={handleFileSelect}
            className="hidden"
          />
        </div>

        {/* Bottom info */}
        <div className="bg-blue-50 border-t border-blue-200 p-4">
          <p className="text-blue-800 text-center text-sm">
            Photos are saved as drafts. You can add names and details later.
          </p>
        </div>
      </div>
    )
  }

  // Render preview step
  if (step === 'preview') {
    return (
      <div className="min-h-screen bg-black flex flex-col">
        {/* Photo preview */}
        <div className="flex-1 relative">
          {currentPhoto && (
            <Image
              src={currentPhoto}
              alt="Preview"
              fill
              className="object-contain"
            />
          )}
        </div>

        {/* Action buttons */}
        <div className="bg-black/80 p-6">
          <div className="flex gap-4 max-w-md mx-auto">
            <button
              onClick={handleRetake}
              className="flex-1 py-4 px-6 bg-gray-700 hover:bg-gray-600 text-white font-bold text-lg rounded-xl transition-colors"
            >
              {isMobile ? 'Retake' : 'Choose Different'}
            </button>
            <button
              onClick={handleKeep}
              className="flex-1 py-4 px-6 bg-green-600 hover:bg-green-700 text-white font-bold text-lg rounded-xl transition-colors"
            >
              Keep
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Render type selection step
  if (step === 'type-select') {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col">
        {/* Header with photo */}
        <div className="relative h-48 bg-gray-200">
          {currentPhoto && (
            <Image
              src={currentPhoto}
              alt="Selected"
              fill
              className="object-cover"
            />
          )}
          <div className="absolute inset-0 bg-black/30 flex items-center justify-center">
            <h2 className="text-2xl font-bold text-white drop-shadow-lg">
              What is this?
            </h2>
          </div>
        </div>

        {/* Type selection */}
        <div className="flex-1 flex flex-col items-center justify-center p-6">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 w-full max-w-md">
              <p className="text-red-600 text-center">{error}</p>
            </div>
          )}

          <div className="flex flex-col gap-4 w-full max-w-sm">
            <button
              onClick={() => handleTypeSelect('contact')}
              disabled={isSaving}
              className="flex items-center justify-center gap-3 py-8 px-8 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold text-xl rounded-xl transition-colors focus:outline-none focus:ring-4 focus:ring-blue-300 focus:ring-offset-2"
            >
              <span className="text-3xl">👤</span>
              Person or Pet
            </button>

            <button
              onClick={() => handleTypeSelect('item')}
              disabled={isSaving}
              className="flex items-center justify-center gap-3 py-8 px-8 bg-amber-500 hover:bg-amber-600 disabled:bg-gray-400 text-white font-bold text-xl rounded-xl transition-colors focus:outline-none focus:ring-4 focus:ring-amber-300 focus:ring-offset-2"
            >
              <span className="text-3xl">📦</span>
              Thing
            </button>
          </div>

          {isSaving && (
            <div className="mt-6 flex items-center gap-2 text-gray-600">
              <div className="w-5 h-5 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
              <span>Saving...</span>
            </div>
          )}

          <button
            onClick={handleRetake}
            disabled={isSaving}
            className="mt-8 text-gray-500 hover:text-gray-700 underline"
          >
            Go Back
          </button>
        </div>
      </div>
    )
  }

  return null
}
