'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient } from '@/lib/api/client'
import { ItemCard, Item } from '@/components/life-words/ItemCard'
import { QuickCompleteModal } from '@/components/life-words/QuickCompleteModal'
import Link from 'next/link'

export const dynamic = 'force-dynamic'

export default function ItemsListPage() {
  const router = useRouter()
  const [items, setItems] = useState<Item[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [quickCompleteItem, setQuickCompleteItem] = useState<Item | null>(null)

  useEffect(() => {
    loadItems()
  }, [])

  const loadItems = async () => {
    try {
      const data = await apiClient.get<Item[]>('/api/life-words/items')
      setItems(data)
    } catch (err: unknown) {
      const e = err as Record<string, unknown>
      setError((e.detail as string) || (e.message as string) || 'An error occurred')
      console.error('Error loading items:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteItem = async (itemId: string) => {
    try {
      await apiClient.delete(`/api/life-words/items/${itemId}`)
      setItems(prev => prev.filter(i => i.id !== itemId))
    } catch (err: unknown) {
      const e = err as Record<string, unknown>
      setError((e.detail as string) || (e.message as string) || 'Failed to delete item')
    }
  }

  const handleQuickComplete = async (data: { name: string }) => {
    if (!quickCompleteItem) return

    await apiClient.put(`/api/life-words/items/${quickCompleteItem.id}`, {
      name: data.name,
    })

    // Reload items to get updated data
    await loadItems()
  }

  const handleFullEdit = () => {
    if (quickCompleteItem) {
      router.push(`/dashboard/practice/items/${quickCompleteItem.id}/edit`)
    }
  }

  // Separate incomplete and complete items
  const incompleteItems = items.filter(i => i.is_complete === false)
  const completeItems = items.filter(i => i.is_complete !== false)

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
        <div className="flex flex-col-reverse sm:flex-row sm:items-center sm:justify-between gap-2 mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              My Stuff
            </h1>
            <p className="text-lg text-gray-600 mt-1">
              {items.length} item{items.length !== 1 ? 's' : ''} saved
            </p>
          </div>
          <Link
            href="/dashboard/practice"
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

        {/* Add new item buttons */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <Link
            href="/dashboard/practice/quick-add"
            className="flex-1 py-4 px-6 bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-semibold text-lg rounded-lg transition-colors block text-center flex items-center justify-center gap-2"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Quick Add Photos
          </Link>
          <Link
            href="/dashboard/practice/items/new"
            className="flex-1 py-4 px-6 bg-blue-50 hover:bg-blue-100 border-2 border-dashed border-blue-300 rounded-lg text-blue-600 font-semibold text-lg transition-colors block text-center"
          >
            + Add with Details
          </Link>
        </div>

        {/* Needs Details section - incomplete items */}
        {incompleteItems.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-4">
              <div className="bg-amber-100 text-amber-700 px-3 py-1 rounded-full text-sm font-semibold">
                {incompleteItems.length} photo{incompleteItems.length !== 1 ? 's' : ''} need{incompleteItems.length === 1 ? 's' : ''} details
              </div>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {incompleteItems.map(item => (
                <ItemCard
                  key={item.id}
                  item={item}
                  onDelete={handleDeleteItem}
                  onQuickComplete={setQuickCompleteItem}
                />
              ))}
            </div>
          </div>
        )}

        {/* Complete items section */}
        {completeItems.length > 0 && (
          <>
            {incompleteItems.length > 0 && (
              <h2 className="text-xl font-bold text-gray-700 mb-4">Ready for Practice</h2>
            )}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {completeItems.map(item => (
                <ItemCard
                  key={item.id}
                  item={item}
                  onDelete={handleDeleteItem}
                />
              ))}
            </div>
          </>
        )}

        {/* Empty state */}
        {items.length === 0 && (
          <div className="text-center py-12 bg-gray-50 rounded-lg">
            <div className="text-6xl mb-4">📦</div>
            <p className="text-xl text-gray-600 mb-4">No items yet</p>
            <p className="text-gray-500">Add your first item to get started!</p>
          </div>
        )}
      </div>

      {/* Quick Complete Modal */}
      {quickCompleteItem && (
        <QuickCompleteModal
          isOpen={true}
          onClose={() => setQuickCompleteItem(null)}
          onSave={handleQuickComplete}
          onFullEdit={handleFullEdit}
          photoUrl={quickCompleteItem.photo_url}
          type="item"
        />
      )}
    </div>
  )
}
