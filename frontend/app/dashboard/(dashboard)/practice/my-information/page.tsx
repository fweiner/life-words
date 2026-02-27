'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api/client'
import Link from 'next/link'

export const dynamic = 'force-dynamic'

interface ProfileData {
  id: string
  email: string
  full_name: string | null
  full_name_pronunciation: string | null
  date_of_birth: string | null
  gender: string | null
  height: string | null
  weight: string | null
  hair_color: string | null
  eye_color: string | null
  job: string | null
  phone_number: string | null
  address_city: string | null
  address_state: string | null
  address_zip: string | null
  marital_status: string | null
  number_of_children: number | null
  favorite_food: string | null
  favorite_music: string | null
}

const GENDER_OPTIONS = [
  { value: '', label: 'Select...' },
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
  { value: 'non-binary', label: 'Non-binary' },
  { value: 'other', label: 'Other' },
  { value: 'prefer-not-to-say', label: 'Prefer not to say' },
]

const MARITAL_STATUS_OPTIONS = [
  { value: '', label: 'Select...' },
  { value: 'single', label: 'Single' },
  { value: 'married', label: 'Married' },
  { value: 'divorced', label: 'Divorced' },
  { value: 'widowed', label: 'Widowed' },
  { value: 'partnered', label: 'Partnered' },
]

function calculateAge(dateOfBirth: string | null): number | null {
  if (!dateOfBirth) return null
  const today = new Date()
  const birthDate = new Date(dateOfBirth)
  let age = today.getFullYear() - birthDate.getFullYear()
  const monthDiff = today.getMonth() - birthDate.getMonth()
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--
  }
  return age
}

export default function MyInformationPage() {
  const [profile, setProfile] = useState<ProfileData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  // Form state
  const [fullName, setFullName] = useState('')
  const [fullNamePronunciation, setFullNamePronunciation] = useState('')
  const [dateOfBirth, setDateOfBirth] = useState('')
  const [gender, setGender] = useState('')
  const [height, setHeight] = useState('')
  const [weight, setWeight] = useState('')
  const [hairColor, setHairColor] = useState('')
  const [eyeColor, setEyeColor] = useState('')
  const [job, setJob] = useState('')
  const [phoneNumber, setPhoneNumber] = useState('')
  const [addressCity, setAddressCity] = useState('')
  const [addressState, setAddressState] = useState('')
  const [addressZip, setAddressZip] = useState('')
  const [maritalStatus, setMaritalStatus] = useState('')
  const [numberOfChildren, setNumberOfChildren] = useState('')
  const [favoriteFood, setFavoriteFood] = useState('')
  const [favoriteMusic, setFavoriteMusic] = useState('')

  useEffect(() => {
    loadProfile()
  }, [])

  const loadProfile = async () => {
    try {
      const data = await apiClient.get<ProfileData>('/api/profile')
      setProfile(data)

      // Populate form
      setFullName(data.full_name || '')
      setFullNamePronunciation(data.full_name_pronunciation || '')
      setDateOfBirth(data.date_of_birth || '')
      setGender(data.gender || '')
      setHeight(data.height || '')
      setWeight(data.weight || '')
      setHairColor(data.hair_color || '')
      setEyeColor(data.eye_color || '')
      setJob(data.job || '')
      setPhoneNumber(data.phone_number || '')
      setAddressCity(data.address_city || '')
      setAddressState(data.address_state || '')
      setAddressZip(data.address_zip || '')
      setMaritalStatus(data.marital_status || '')
      setNumberOfChildren(data.number_of_children?.toString() || '')
      setFavoriteFood(data.favorite_food || '')
      setFavoriteMusic(data.favorite_music || '')
    } catch (err: unknown) {
      const e = err as Record<string, unknown>
      setError((e.message as string) || 'An error occurred')
      console.error('Error loading profile:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSaving(true)
    setError(null)
    setSuccess(null)

    try {
      const updateData = {
        full_name: fullName || null,
        full_name_pronunciation: fullNamePronunciation || null,
        date_of_birth: dateOfBirth || null,
        gender: gender || null,
        height: height || null,
        weight: weight || null,
        hair_color: hairColor || null,
        eye_color: eyeColor || null,
        job: job || null,
        phone_number: phoneNumber || null,
        address_city: addressCity || null,
        address_state: addressState || null,
        address_zip: addressZip || null,
        marital_status: maritalStatus || null,
        number_of_children: numberOfChildren ? parseInt(numberOfChildren, 10) : null,
        favorite_food: favoriteFood || null,
        favorite_music: favoriteMusic || null,
      }

      await apiClient.patch('/api/profile', updateData)

      setSuccess('Your information has been saved!')

      // Scroll to top to show success message
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } catch (err: unknown) {
      const e = err as Record<string, unknown>
      setError((e.message as string) || 'Failed to save information')
    } finally {
      setIsSaving(false)
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

  const age = calculateAge(dateOfBirth)

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-[var(--color-primary)]">
              My Information
            </h1>
            <p className="text-lg text-gray-600 mt-1">
              This information will be used to generate practice questions.
            </p>
          </div>
          <Link
            href="/dashboard/practice"
            className="text-[var(--color-primary)] hover:underline"
          >
            ← Back to Life Words and Memory
          </Link>
        </div>

        {error && (
          <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4 mb-6">
            <p className="text-red-700 font-semibold">{error}</p>
          </div>
        )}

        {success && (
          <div className="bg-green-50 border-2 border-green-300 rounded-lg p-4 mb-6">
            <p className="text-green-700 font-semibold">{success}</p>
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-8 max-w-2xl">
          {/* Basic Info Section */}
          <div className="bg-gray-50 rounded-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Basic Information</h2>
            <div className="space-y-4">
              <div>
                <label htmlFor="fullName" className="block text-lg font-medium mb-2">
                  Full Name
                </label>
                <input
                  id="fullName"
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-[var(--color-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                  placeholder="Your full name"
                />
              </div>

              <div>
                <label htmlFor="fullNamePronunciation" className="block text-lg font-medium mb-2">
                  Name Pronunciation <span className="text-gray-500 font-normal">(optional)</span>
                </label>
                <input
                  id="fullNamePronunciation"
                  type="text"
                  value={fullNamePronunciation}
                  onChange={(e) => setFullNamePronunciation(e.target.value)}
                  className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-[var(--color-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                  placeholder="e.g., 'Wyner' for 'Weiner'"
                />
                <p className="mt-1 text-sm text-gray-500">
                  If your name is often mispronounced, enter how it should be spoken
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="dateOfBirth" className="block text-lg font-medium mb-2">
                    Date of Birth
                  </label>
                  <input
                    id="dateOfBirth"
                    type="date"
                    value={dateOfBirth}
                    onChange={(e) => setDateOfBirth(e.target.value)}
                    className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-[var(--color-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                  />
                  {age !== null && (
                    <p className="mt-2 text-gray-600">Age: {age} years old</p>
                  )}
                </div>

                <div>
                  <label htmlFor="gender" className="block text-lg font-medium mb-2">
                    Gender
                  </label>
                  <select
                    id="gender"
                    value={gender}
                    onChange={(e) => setGender(e.target.value)}
                    className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-[var(--color-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:ring-offset-2 bg-white"
                  >
                    {GENDER_OPTIONS.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* Physical Section */}
          <div className="bg-gray-50 rounded-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Physical Characteristics</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="height" className="block text-lg font-medium mb-2">
                  Height
                </label>
                <input
                  id="height"
                  type="text"
                  value={height}
                  onChange={(e) => setHeight(e.target.value)}
                  className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-[var(--color-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                  placeholder="e.g., 5'10&quot; or 178 cm"
                />
              </div>

              <div>
                <label htmlFor="weight" className="block text-lg font-medium mb-2">
                  Weight
                </label>
                <input
                  id="weight"
                  type="text"
                  value={weight}
                  onChange={(e) => setWeight(e.target.value)}
                  className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-[var(--color-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                  placeholder="e.g., 160 lbs or 73 kg"
                />
              </div>

              <div>
                <label htmlFor="hairColor" className="block text-lg font-medium mb-2">
                  Hair Color
                </label>
                <input
                  id="hairColor"
                  type="text"
                  value={hairColor}
                  onChange={(e) => setHairColor(e.target.value)}
                  className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-[var(--color-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                  placeholder="e.g., Brown, Gray, Blonde"
                />
              </div>

              <div>
                <label htmlFor="eyeColor" className="block text-lg font-medium mb-2">
                  Eye Color
                </label>
                <input
                  id="eyeColor"
                  type="text"
                  value={eyeColor}
                  onChange={(e) => setEyeColor(e.target.value)}
                  className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-[var(--color-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                  placeholder="e.g., Blue, Brown, Green"
                />
              </div>
            </div>
          </div>

          {/* Contact & Work Section */}
          <div className="bg-gray-50 rounded-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Contact & Work</h2>
            <div className="space-y-4">
              <div>
                <label htmlFor="email" className="block text-lg font-medium mb-2">
                  Email Address
                </label>
                <input
                  id="email"
                  type="email"
                  value={profile?.email || ''}
                  disabled
                  className="w-full px-4 py-3 text-lg border-2 border-gray-200 rounded-lg bg-gray-100 text-gray-600"
                />
                <p className="mt-1 text-sm text-gray-500">Email cannot be changed</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="phoneNumber" className="block text-lg font-medium mb-2">
                    Phone Number
                  </label>
                  <input
                    id="phoneNumber"
                    type="tel"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-[var(--color-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                    placeholder="e.g., (555) 123-4567"
                  />
                </div>

                <div>
                  <label htmlFor="job" className="block text-lg font-medium mb-2">
                    Job / Occupation
                  </label>
                  <input
                    id="job"
                    type="text"
                    value={job}
                    onChange={(e) => setJob(e.target.value)}
                    className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-[var(--color-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                    placeholder="e.g., Teacher, Engineer, Retired"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Address Section */}
          <div className="bg-gray-50 rounded-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Address</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label htmlFor="addressCity" className="block text-lg font-medium mb-2">
                  City
                </label>
                <input
                  id="addressCity"
                  type="text"
                  value={addressCity}
                  onChange={(e) => setAddressCity(e.target.value)}
                  className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-[var(--color-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                  placeholder="City"
                />
              </div>

              <div>
                <label htmlFor="addressState" className="block text-lg font-medium mb-2">
                  State
                </label>
                <input
                  id="addressState"
                  type="text"
                  value={addressState}
                  onChange={(e) => setAddressState(e.target.value)}
                  className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-[var(--color-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                  placeholder="State"
                />
              </div>

              <div>
                <label htmlFor="addressZip" className="block text-lg font-medium mb-2">
                  Zip Code
                </label>
                <input
                  id="addressZip"
                  type="text"
                  value={addressZip}
                  onChange={(e) => setAddressZip(e.target.value)}
                  className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-[var(--color-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                  placeholder="Zip Code"
                />
              </div>
            </div>
          </div>

          {/* Personal Section */}
          <div className="bg-gray-50 rounded-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Personal</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="maritalStatus" className="block text-lg font-medium mb-2">
                  Marital Status
                </label>
                <select
                  id="maritalStatus"
                  value={maritalStatus}
                  onChange={(e) => setMaritalStatus(e.target.value)}
                  className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-[var(--color-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:ring-offset-2 bg-white"
                >
                  {MARITAL_STATUS_OPTIONS.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="numberOfChildren" className="block text-lg font-medium mb-2">
                  Number of Children
                </label>
                <input
                  id="numberOfChildren"
                  type="number"
                  min="0"
                  value={numberOfChildren}
                  onChange={(e) => setNumberOfChildren(e.target.value)}
                  className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-[var(--color-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                  placeholder="0"
                />
              </div>
            </div>
          </div>

          {/* Favorites Section */}
          <div className="bg-gray-50 rounded-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Favorites</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="favoriteFood" className="block text-lg font-medium mb-2">
                  Favorite Food
                </label>
                <input
                  id="favoriteFood"
                  type="text"
                  value={favoriteFood}
                  onChange={(e) => setFavoriteFood(e.target.value)}
                  className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-[var(--color-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                  placeholder="e.g., Pizza, Sushi, Tacos"
                />
              </div>

              <div>
                <label htmlFor="favoriteMusic" className="block text-lg font-medium mb-2">
                  Favorite Type of Music
                </label>
                <input
                  id="favoriteMusic"
                  type="text"
                  value={favoriteMusic}
                  onChange={(e) => setFavoriteMusic(e.target.value)}
                  className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-[var(--color-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                  placeholder="e.g., Country, Jazz, Classical"
                />
              </div>
            </div>
          </div>

          {/* Save Button */}
          <div className="flex gap-4">
            <button
              type="submit"
              disabled={isSaving}
              className="bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] disabled:bg-gray-400 text-white font-bold py-4 px-8 rounded-lg text-lg transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2"
              style={{ minHeight: '44px' }}
            >
              {isSaving ? 'Saving...' : 'Save Information'}
            </button>

            <Link
              href="/dashboard/practice"
              className="bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold py-4 px-8 rounded-lg text-lg transition-colors focus:outline-none focus:ring-4 focus:ring-gray-300 focus:ring-offset-2 inline-flex items-center"
              style={{ minHeight: '44px' }}
            >
              Cancel
            </Link>
          </div>
        </form>
      </div>
    </div>
  )
}
