'use client'

import Image from 'next/image'
import Link from 'next/link'
import { IncompleteEntryBadge } from './IncompleteEntryBadge'

export interface Contact {
  id: string
  name: string
  nickname?: string
  relationship: string
  photo_url: string
  category?: string
  description?: string
  is_active: boolean
  is_complete?: boolean
}

interface ContactCardProps {
  contact: Contact
  onDelete?: (id: string) => void
  showActions?: boolean
  onQuickComplete?: (contact: Contact) => void
}

const RELATIONSHIP_LABELS: Record<string, string> = {
  spouse: 'Spouse/Partner',
  child: 'Son/Daughter',
  grandchild: 'Grandchild',
  parent: 'Parent',
  sibling: 'Brother/Sister',
  friend: 'Friend',
  pet: 'Pet',
  caregiver: 'Caregiver',
  neighbor: 'Neighbor',
  other: 'Other',
}

export function ContactCard({ contact, onDelete, showActions = true, onQuickComplete }: ContactCardProps) {
  const isIncomplete = contact.is_complete === false

  const handleDelete = () => {
    if (onDelete && confirm(`Are you sure you want to remove ${contact.name || 'this photo'}?`)) {
      onDelete(contact.id)
    }
  }

  const handleCardClick = () => {
    if (isIncomplete && onQuickComplete) {
      onQuickComplete(contact)
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
          src={contact.photo_url}
          alt={contact.name || 'Photo'}
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
            <p className="text-gray-500 text-sm">
              This photo needs a name and relationship to be used in practice sessions.
            </p>
          </>
        ) : (
          <>
            <h3 className="text-xl font-bold text-gray-900">{contact.name}</h3>

            {contact.nickname && (
              <p className="text-gray-600 text-sm">&quot;{contact.nickname}&quot;</p>
            )}

            <p className="text-[var(--color-primary)] font-semibold mt-1">
              {RELATIONSHIP_LABELS[contact.relationship] || contact.relationship}
            </p>

            {contact.description && (
              <p className="text-gray-500 text-sm mt-2 line-clamp-2">{contact.description}</p>
            )}
          </>
        )}

        {showActions && (
          <div className="flex gap-2 mt-4">
            <Link
              href={`/dashboard/practice/contacts/${contact.id}/edit`}
              className={`flex-1 text-center py-2 px-3 font-semibold rounded-lg text-sm transition-colors ${
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
              className="py-2 px-3 bg-red-50 hover:bg-red-100 text-red-600 font-semibold rounded-lg text-sm transition-colors"
            >
              Remove
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
