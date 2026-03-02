'use client'

import Image from 'next/image'
import Link from 'next/link'
import { IncompleteEntryBadge } from './IncompleteEntryBadge'

export interface Item {
  id: string
  name: string
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
  is_active: boolean
  is_complete?: boolean
}

interface ItemCardProps {
  item: Item
  onDelete?: (id: string) => void
  showActions?: boolean
  onQuickComplete?: (item: Item) => void
}

export function ItemCard({ item, onDelete, showActions = true, onQuickComplete }: ItemCardProps) {
  const isIncomplete = item.is_complete === false

  const handleDelete = () => {
    if (onDelete && confirm(`Are you sure you want to remove ${item.name || 'this item'}?`)) {
      onDelete(item.id)
    }
  }

  const handleCardClick = () => {
    if (isIncomplete && onQuickComplete) {
      onQuickComplete(item)
    }
  }

  return (
    <div
      className={`bg-white rounded-lg shadow-md overflow-hidden border-2 transition-colors ${
        isIncomplete
          ? 'border-amber-300 hover:border-amber-400 cursor-pointer'
          : 'border-gray-100 hover:border-blue-200'
      }`}
      onClick={isIncomplete ? handleCardClick : undefined}
    >
      <div className="relative w-full h-48">
        <Image
          src={item.photo_url}
          alt={item.name || 'Photo'}
          fill
          className="object-cover"
        />
        {isIncomplete && (
          <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
            <span className="bg-white text-gray-800 font-semibold px-4 py-2 rounded-lg text-lg shadow-lg">
              Tap to add name
            </span>
          </div>
        )}
      </div>

      <div className="p-4">
        {isIncomplete ? (
          <>
            <IncompleteEntryBadge className="mb-2" />
            <p className="text-gray-500 text-base">
              This item needs a name to be used in practice sessions.
            </p>
          </>
        ) : (
          <>
            <h3 className="text-xl font-bold text-gray-900">{item.name}</h3>

            {item.category && (
              <p className="text-[var(--color-primary)] font-semibold mt-1">
                {item.category}
              </p>
            )}

            {item.purpose && (
              <p className="text-gray-500 text-base mt-2 line-clamp-2">{item.purpose}</p>
            )}
          </>
        )}

        {showActions && (
          <div className="flex gap-2 mt-4">
            <Link
              href={`/dashboard/practice/items/${item.id}/edit`}
              className={`flex-1 text-center py-3 px-3 font-semibold rounded-lg text-base transition-colors ${
                isIncomplete
                  ? 'bg-amber-100 hover:bg-amber-200 text-amber-700'
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
              }`}
              onClick={(e) => e.stopPropagation()}
            >
              {isIncomplete ? 'Add Details' : 'Edit'}
            </Link>
            <button
              onClick={(e) => {
                e.stopPropagation()
                handleDelete()
              }}
              className="py-3 px-3 bg-red-50 hover:bg-red-100 text-red-600 font-semibold rounded-lg text-base transition-colors"
            >
              Remove
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
