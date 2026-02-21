'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient } from '@/lib/api/client'
import { ItemForm, ItemFormData } from '@/components/life-words/ItemForm'
import Link from 'next/link'

export const dynamic = 'force-dynamic'

export default function NewItemPage() {
  const router = useRouter()
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (formData: ItemFormData) => {
    setIsSaving(true)
    setError(null)

    try {
      await apiClient.post('/api/life-words/items', formData)

      // Redirect back to items list
      router.push('/dashboard/treatments/life-words/items')
    } catch (err: unknown) {
      const e = err as Record<string, unknown>
      setError((e.detail as string) || (e.message as string) || 'Failed to add item')
      throw err
    } finally {
      setIsSaving(false)
    }
  }

  const handleCancel = () => {
    router.push('/dashboard/treatments/life-words/items')
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Add New Item
            </h1>
            <p className="text-lg text-gray-600 mt-1">
              Add a new item to practice naming.
            </p>
          </div>
          <Link
            href="/dashboard/treatments/life-words/items"
            className="text-[var(--color-primary)] hover:underline"
          >
            ← Back to My Stuff
          </Link>
        </div>

        {error && (
          <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4 mb-6">
            <p className="text-red-700 font-semibold">{error}</p>
          </div>
        )}

        <div className="max-w-xl mx-auto">
          <ItemForm
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            submitLabel="Add Item"
            isSubmitting={isSaving}
          />
        </div>
      </div>
    </div>
  )
}
