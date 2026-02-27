'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { apiClient, ApiError } from '@/lib/api/client'
import { ItemForm, ItemFormData } from '@/components/life-words/ItemForm'
import Link from 'next/link'

export const dynamic = 'force-dynamic'

interface ItemData {
  id: string
  name: string
  pronunciation?: string
  photo_url: string
  purpose?: string
  features?: string
  category?: string
  size?: string
  shape?: string
  color?: string
  weight?: string
  location?: string
  associated_with?: string
}

export default function EditItemPage() {
  const router = useRouter()
  const params = useParams()
  const itemId = params.id as string

  const [item, setItem] = useState<ItemData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadItem = useCallback(async () => {
    try {
      const data = await apiClient.get<ItemData>(`/api/life-words/items/${itemId}`)
      setItem(data)
    } catch (err: unknown) {
      if (err instanceof ApiError && err.status === 404) {
        setError('Item not found')
      } else {
        const e = err as Record<string, unknown>
        setError((e.detail as string) || (e.message as string) || 'An error occurred')
      }
      console.error('Error loading item:', err)
    } finally {
      setIsLoading(false)
    }
  }, [itemId])

  useEffect(() => {
    loadItem()
  }, [loadItem])

  const handleSubmit = async (formData: ItemFormData) => {
    setIsSaving(true)
    setError(null)

    try {
      await apiClient.put(`/api/life-words/items/${itemId}`, formData)

      // Redirect back to items list
      router.push('/dashboard/practice/items')
    } catch (err: unknown) {
      const e = err as Record<string, unknown>
      setError((e.detail as string) || (e.message as string) || 'Failed to update item')
      throw err
    } finally {
      setIsSaving(false)
    }
  }

  const handleCancel = () => {
    router.push('/dashboard/practice/items')
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

  if (!item) {
    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow-md p-8">
          <div className="text-center py-12">
            <div className="text-6xl mb-4">❌</div>
            <p className="text-xl text-gray-600 mb-4">{error || 'Item not found'}</p>
            <Link
              href="/dashboard/practice/items"
              className="text-[var(--color-primary)] hover:underline"
            >
              ← Back to My Stuff
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="flex flex-col-reverse sm:flex-row sm:items-center sm:justify-between gap-2 mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Edit Item
            </h1>
            <p className="text-lg text-gray-600 mt-1">
              Update {item.name}&apos;s information.
            </p>
          </div>
          <Link
            href="/dashboard/practice/items"
            className="text-[var(--color-primary)] hover:underline whitespace-nowrap"
          >
            ← Back
          </Link>
        </div>

        {error && (
          <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4 mb-6">
            <p className="text-red-700 font-semibold">{error}</p>
          </div>
        )}

        <div className="max-w-xl mx-auto">
          <ItemForm
            initialData={{
              name: item.name,
              pronunciation: item.pronunciation || '',
              photo_url: item.photo_url,
              purpose: item.purpose || '',
              features: item.features || '',
              category: item.category || '',
              size: item.size || '',
              shape: item.shape || '',
              color: item.color || '',
              weight: item.weight || '',
              location: item.location || '',
              associated_with: item.associated_with || '',
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
