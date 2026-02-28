'use client'

import Link from 'next/link'

export default function PreparationPage() {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="flex flex-col-reverse sm:flex-row sm:items-center sm:justify-between gap-2 mb-6">
          <h1 className="text-4xl font-bold text-[var(--color-primary)]">
            Preparation
          </h1>
          <Link
            href="/dashboard"
            className="text-[var(--color-primary)] hover:underline text-lg whitespace-nowrap"
          >
            &larr; Back to Dashboard
          </Link>
        </div>

        {/* Overview */}
        <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-6 mb-8">
          <h2 className="text-2xl font-bold mb-3 text-gray-900">
            Before You Begin
          </h2>
          <p className="text-lg text-gray-700">
            Follow these steps to set up Life Words with the people and things that matter most.
            A caregiver, family member, or speech-language pathologist can help with setup.
          </p>
        </div>

        {/* Phase 1: Getting Started */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4 text-gray-900 flex items-center">
            <span className="bg-blue-600 text-white rounded-full w-10 h-10 flex items-center justify-center mr-3 flex-shrink-0 text-lg font-bold">1</span>
            Getting Started
          </h2>
          <div className="bg-blue-50 rounded-lg p-6 ml-13">
            <div className="space-y-4">
              <div className="bg-white border-2 border-blue-300 rounded-lg p-4">
                <div className="flex items-start">
                  <span className="bg-blue-600 text-white rounded-full w-7 h-7 flex items-center justify-center mr-3 flex-shrink-0 text-sm font-bold mt-0.5">1</span>
                  <div>
                    <p className="text-lg text-gray-700 font-semibold">Gather email addresses</p>
                    <p className="text-gray-600 mt-1">
                      Collect the email addresses of family members and close friends you&apos;d like to include.
                      They&apos;ll be invited to add their own photo and answer a few questions about themselves.
                    </p>
                  </div>
                </div>
              </div>
              <div className="bg-white border-2 border-blue-300 rounded-lg p-4">
                <div className="flex items-start">
                  <span className="bg-blue-600 text-white rounded-full w-7 h-7 flex items-center justify-center mr-3 flex-shrink-0 text-sm font-bold mt-0.5">2</span>
                  <div>
                    <p className="text-lg text-gray-700 font-semibold">Click &quot;Start Now&quot; on the dashboard</p>
                    <p className="text-gray-600 mt-1">
                      This takes you to the Life Words main page where you can manage your people, items, and practice sessions.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Phase 2: Add Your People */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4 text-gray-900 flex items-center">
            <span className="bg-green-600 text-white rounded-full w-10 h-10 flex items-center justify-center mr-3 flex-shrink-0 text-lg font-bold">2</span>
            Add Your People
          </h2>
          <div className="bg-green-50 rounded-lg p-6 ml-13">
            <p className="text-lg text-gray-700 mb-4">
              The easiest way to add people is by sending them an email invitation.
              They&apos;ll upload their own photo and fill in details about themselves.
            </p>
            <div className="space-y-4">
              <div className="bg-white border-2 border-green-300 rounded-lg p-4">
                <div className="flex items-start">
                  <span className="bg-green-600 text-white rounded-full w-7 h-7 flex items-center justify-center mr-3 flex-shrink-0 text-sm font-bold mt-0.5">3</span>
                  <div>
                    <p className="text-lg text-gray-700 font-semibold">Open My People</p>
                    <p className="text-gray-600 mt-1">
                      On the Life Words main page, find the icon grid at the bottom and click the{' '}
                      <span className="inline-flex items-center bg-gray-100 border border-gray-300 rounded px-2 py-0.5 mx-1">
                        <span className="text-lg mr-1">👥</span> My People
                      </span>{' '}
                      button.
                    </p>
                  </div>
                </div>
              </div>
              <div className="bg-white border-2 border-green-300 rounded-lg p-4">
                <div className="flex items-start">
                  <span className="bg-green-600 text-white rounded-full w-7 h-7 flex items-center justify-center mr-3 flex-shrink-0 text-sm font-bold mt-0.5">4</span>
                  <div>
                    <p className="text-lg text-gray-700 font-semibold">Click &quot;Invite via Email&quot;</p>
                    <p className="text-gray-600 mt-1">
                      Look for the light green box titled{' '}
                      <span className="inline-flex items-center bg-green-100 border border-green-300 rounded px-2 py-0.5 mx-1 font-semibold text-green-800">
                        Invite via Email
                      </span>.
                    </p>
                  </div>
                </div>
              </div>
              <div className="bg-white border-2 border-green-300 rounded-lg p-4">
                <div className="flex items-start">
                  <span className="bg-green-600 text-white rounded-full w-7 h-7 flex items-center justify-center mr-3 flex-shrink-0 text-sm font-bold mt-0.5">5</span>
                  <div>
                    <p className="text-lg text-gray-700 font-semibold">Enter their name and email</p>
                    <p className="text-gray-600 mt-1">
                      Type the person&apos;s name and their email address into the form fields.
                    </p>
                  </div>
                </div>
              </div>
              <div className="bg-white border-2 border-green-300 rounded-lg p-4">
                <div className="flex items-start">
                  <span className="bg-green-600 text-white rounded-full w-7 h-7 flex items-center justify-center mr-3 flex-shrink-0 text-sm font-bold mt-0.5">6</span>
                  <div>
                    <p className="text-lg text-gray-700 font-semibold">Review the personal message</p>
                    <p className="text-gray-600 mt-1">
                      Check that the message included in the invitation is appropriate and welcoming.
                      You can customize it if you&apos;d like.
                    </p>
                  </div>
                </div>
              </div>
              <div className="bg-white border-2 border-green-300 rounded-lg p-4">
                <div className="flex items-start">
                  <span className="bg-green-600 text-white rounded-full w-7 h-7 flex items-center justify-center mr-3 flex-shrink-0 text-sm font-bold mt-0.5">7</span>
                  <div>
                    <p className="text-lg text-gray-700 font-semibold">Click &quot;Send Invite&quot;</p>
                    <p className="text-gray-600 mt-1">
                      Send the invitation. Repeat this process for each person you want to add.
                    </p>
                  </div>
                </div>
              </div>
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                <div className="flex items-start">
                  <span className="bg-amber-500 text-white rounded-full w-7 h-7 flex items-center justify-center mr-3 flex-shrink-0 text-sm font-bold mt-0.5">8</span>
                  <div>
                    <p className="text-lg text-gray-700 font-semibold">What happens next</p>
                    <p className="text-gray-600 mt-1">
                      Each person will receive an email asking them to add their picture and answer a few questions.
                      Their photo and responses will be automatically imported into your Life Words account.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Phase 3: Add Manually */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4 text-gray-900 flex items-center">
            <span className="bg-amber-500 text-white rounded-full w-10 h-10 flex items-center justify-center mr-3 flex-shrink-0 text-lg font-bold">3</span>
            Add Manually (Alternative)
          </h2>
          <div className="bg-amber-50 rounded-lg p-6 ml-13">
            <div className="bg-white border-2 border-amber-300 rounded-lg p-4">
              <div className="flex items-start">
                <span className="bg-amber-500 text-white rounded-full w-7 h-7 flex items-center justify-center mr-3 flex-shrink-0 text-sm font-bold mt-0.5">9</span>
                <div>
                  <p className="text-lg text-gray-700 font-semibold">Add with Details</p>
                  <p className="text-gray-600 mt-1">
                    If you&apos;d rather not send an email invitation, you can fill in the information yourself.
                    Click{' '}
                    <span className="inline-flex items-center bg-[var(--color-primary)] text-white rounded px-3 py-0.5 mx-1 text-sm font-semibold">
                      + Add a New Person
                    </span>{' '}
                    then choose &quot;Add with Details&quot; to upload a photo and answer the questions on their behalf.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Phase 4: Add from Photos */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4 text-gray-900 flex items-center">
            <span className="bg-teal-600 text-white rounded-full w-10 h-10 flex items-center justify-center mr-3 flex-shrink-0 text-lg font-bold">4</span>
            Add from Photos
          </h2>
          <div className="bg-teal-50 rounded-lg p-6 ml-13">
            <div className="bg-white border-2 border-teal-300 rounded-lg p-4">
              <div className="flex items-start">
                <span className="bg-teal-600 text-white rounded-full w-7 h-7 flex items-center justify-center mr-3 flex-shrink-0 text-sm font-bold mt-0.5">10</span>
                <div>
                  <p className="text-lg text-gray-700 font-semibold">Import from your phone</p>
                  <p className="text-gray-600 mt-1">
                    If you&apos;re using a phone or tablet with photos, you can easily import them into your Life Words account.
                    When adding a person or item, tap the photo upload area to select a picture from your device&apos;s photo library.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Phase 5: Add Your Stuff */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4 text-gray-900 flex items-center">
            <span className="bg-blue-600 text-white rounded-full w-10 h-10 flex items-center justify-center mr-3 flex-shrink-0 text-lg font-bold">5</span>
            Add Your Stuff
          </h2>
          <div className="bg-blue-50 rounded-lg p-6 ml-13">
            <p className="text-lg text-gray-700 mb-4">
              In addition to people, you can practice naming everyday objects around the house.
            </p>
            <div className="space-y-4">
              <div className="bg-white border-2 border-blue-300 rounded-lg p-4">
                <div className="flex items-start">
                  <span className="bg-blue-600 text-white rounded-full w-7 h-7 flex items-center justify-center mr-3 flex-shrink-0 text-sm font-bold mt-0.5">11</span>
                  <div>
                    <p className="text-lg text-gray-700 font-semibold">Open My Stuff</p>
                    <p className="text-gray-600 mt-1">
                      On the Life Words main page, click the{' '}
                      <span className="inline-flex items-center bg-gray-100 border border-gray-300 rounded px-2 py-0.5 mx-1">
                        <span className="text-lg mr-1">📦</span> My Stuff
                      </span>{' '}
                      button in the icon grid.
                    </p>
                  </div>
                </div>
              </div>
              <div className="bg-white border-2 border-blue-300 rounded-lg p-4">
                <div className="flex items-start">
                  <span className="bg-blue-600 text-white rounded-full w-7 h-7 flex items-center justify-center mr-3 flex-shrink-0 text-sm font-bold mt-0.5">12</span>
                  <div>
                    <p className="text-lg text-gray-700 font-semibold">Take photos of familiar objects</p>
                    <p className="text-gray-600 mt-1">
                      Use your phone or tablet to photograph things around the house that are easily recognizable &mdash;
                      a favorite mug, the TV remote, a pet&apos;s bed, kitchen items, and more.
                    </p>
                  </div>
                </div>
              </div>
              <div className="bg-white border-2 border-blue-300 rounded-lg p-4">
                <div className="flex items-start">
                  <span className="bg-blue-600 text-white rounded-full w-7 h-7 flex items-center justify-center mr-3 flex-shrink-0 text-sm font-bold mt-0.5">13</span>
                  <div>
                    <p className="text-lg text-gray-700 font-semibold">Add details for each item</p>
                    <p className="text-gray-600 mt-1">
                      Click{' '}
                      <span className="inline-flex items-center bg-[var(--color-primary)] text-white rounded px-3 py-0.5 mx-1 text-sm font-semibold">
                        + Add a New Item
                      </span>{' '}
                      then upload the photo and answer the questions about the object. The more details you add, the better the practice hints will be.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Phase 6: You're Ready */}
        <div className="mb-8">
          <div className="bg-green-50 border-2 border-green-200 rounded-lg p-6">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 flex items-center">
              <span className="bg-green-600 text-white rounded-full w-10 h-10 flex items-center justify-center mr-3 flex-shrink-0 text-lg font-bold">✓</span>
              You&apos;re Ready!
            </h2>
            <div className="flex items-start">
              <span className="bg-green-600 text-white rounded-full w-7 h-7 flex items-center justify-center mr-3 flex-shrink-0 text-sm font-bold mt-0.5">14</span>
              <p className="text-lg text-gray-700">
                You&apos;re all set to use Life Words! Head back to the dashboard and click <strong>&quot;Start Now&quot;</strong> to
                begin practicing. Regular practice &mdash; even just a few minutes a day &mdash; can make a real difference
                in helping your loved one improve through experience.
              </p>
            </div>
          </div>
        </div>

        {/* Start Now CTA */}
        <div className="text-center pt-4">
          <Link
            href="/dashboard/practice"
            className="inline-block bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-bold py-4 px-8 rounded-lg text-xl transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2"
          >
            Start Now →
          </Link>
        </div>
      </div>
    </div>
  )
}
