'use client'

import Link from 'next/link'

export default function HowItWorksPage() {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-4xl font-bold text-[var(--color-primary)]">
            How It Works
          </h1>
          <Link
            href="/dashboard/practice"
            className="text-[var(--color-primary)] hover:underline text-lg"
          >
            ← Back
          </Link>
        </div>

        {/* Overview Section */}
        <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-6 mb-8">
          <h2 className="text-2xl font-bold mb-3 text-gray-900">
            What is Life Words and Memory?
          </h2>
          <p className="text-lg text-gray-700">
            This tool helps you practice remembering the names of people, pets, and things
            that matter most to you. By using photos and personal information from your own life,
            the practice is more meaningful and effective than generic exercises.
          </p>
        </div>

        {/* Getting Started */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4 text-gray-900 flex items-center">
            <span className="text-3xl mr-3">1️⃣</span>
            Getting Started - Adding Contacts
          </h2>
          <div className="bg-gray-50 rounded-lg p-6 ml-12">
            <p className="text-lg text-gray-700 mb-4">
              Before you can practice, you need to add people to your contact list.
            </p>

            {/* Navigation Instructions */}
            <div className="bg-white border-2 border-blue-300 rounded-lg p-4 mb-4">
              <h4 className="font-bold text-blue-900 mb-3">How to get there:</h4>
              <ol className="space-y-3 text-gray-700">
                <li className="flex items-start">
                  <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center mr-3 flex-shrink-0 text-sm font-bold">1</span>
                  <span>From the Life Words main page, find the icon grid at the bottom</span>
                </li>
                <li className="flex items-start">
                  <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center mr-3 flex-shrink-0 text-sm font-bold">2</span>
                  <div>
                    <span>Click the </span>
                    <span className="inline-flex items-center bg-gray-100 border border-gray-300 rounded px-2 py-1 mx-1">
                      <span className="text-lg mr-1">👥</span> My People
                    </span>
                    <span> button</span>
                  </div>
                </li>
                <li className="flex items-start">
                  <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center mr-3 flex-shrink-0 text-sm font-bold">3</span>
                  <div>
                    <span>Click the </span>
                    <span className="inline-flex items-center bg-[var(--color-primary)] text-white rounded px-3 py-1 mx-1 text-sm font-semibold">
                      + Add a New Person
                    </span>
                    <span> button</span>
                  </div>
                </li>
              </ol>
            </div>

            {/* What you'll see */}
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-4">
              <h4 className="font-bold text-amber-900 mb-2">What you&apos;ll see:</h4>
              <p className="text-gray-700 mb-2">A form to fill out with:</p>
              <ul className="space-y-1 text-gray-700 ml-4">
                <li>• <strong>Photo upload area</strong> - Add a clear picture of the person</li>
                <li>• <strong>Name field</strong> - Enter their full name</li>
                <li>• <strong>Nickname field</strong> - What you usually call them</li>
                <li>• <strong>Relationship dropdown</strong> - Select how they&apos;re connected to you</li>
                <li>• <strong>Personal details</strong> - Their interests, personality, where you see them</li>
              </ul>
            </div>

            <p className="text-gray-600 italic">
              You need at least 2 contacts to start practicing. The more details you add, the better hints you&apos;ll get!
            </p>
          </div>
        </div>

        {/* Name Practice */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4 text-gray-900 flex items-center">
            <span className="text-3xl mr-3">2️⃣</span>
            Name Practice
          </h2>
          <div className="bg-green-50 rounded-lg p-6 ml-12">
            <p className="text-lg text-gray-700 mb-4">
              Practice recognizing people by looking at their photo and saying their name.
            </p>

            {/* Navigation Instructions */}
            <div className="bg-white border-2 border-green-300 rounded-lg p-4 mb-4">
              <h4 className="font-bold text-green-900 mb-3">How to get there:</h4>
              <ol className="space-y-3 text-gray-700">
                <li className="flex items-start">
                  <span className="bg-green-600 text-white rounded-full w-6 h-6 flex items-center justify-center mr-3 flex-shrink-0 text-sm font-bold">1</span>
                  <span>Go to the Life Words main page</span>
                </li>
                <li className="flex items-start">
                  <span className="bg-green-600 text-white rounded-full w-6 h-6 flex items-center justify-center mr-3 flex-shrink-0 text-sm font-bold">2</span>
                  <div>
                    <span>Click the big </span>
                    <span className="inline-flex items-center bg-[var(--color-primary)] text-white rounded px-3 py-1 mx-1 text-sm font-semibold">
                      Name Practice
                    </span>
                    <span> button</span>
                  </div>
                </li>
              </ol>
            </div>

            {/* What you'll see */}
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-4">
              <h4 className="font-bold text-amber-900 mb-2">What you&apos;ll see:</h4>
              <ul className="space-y-2 text-gray-700">
                <li className="flex items-start">
                  <span className="text-green-600 mr-2">•</span>
                  <span>A large photo of one of your contacts</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-600 mr-2">•</span>
                  <span>A microphone button to record your answer</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-600 mr-2">•</span>
                  <span>A &quot;Get Hint&quot; button if you need help</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-600 mr-2">•</span>
                  <span>A &quot;Done for now&quot; button when you want to stop</span>
                </li>
              </ul>
            </div>

            {/* How it works */}
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <h4 className="font-bold text-gray-900 mb-2">How to play:</h4>
              <ol className="space-y-2 text-gray-700">
                <li><span className="font-bold text-[var(--color-primary)]">1.</span> Look at the photo that appears</li>
                <li><span className="font-bold text-[var(--color-primary)]">2.</span> Click the microphone button</li>
                <li><span className="font-bold text-[var(--color-primary)]">3.</span> Say the person&apos;s name out loud</li>
                <li><span className="font-bold text-[var(--color-primary)]">4.</span> The app will tell you if you&apos;re correct</li>
                <li><span className="font-bold text-[var(--color-primary)]">5.</span> If you need help, you&apos;ll get a hint to try again</li>
              </ol>
            </div>
          </div>
        </div>

        {/* Question Practice */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4 text-gray-900 flex items-center">
            <span className="text-3xl mr-3">3️⃣</span>
            Question Practice
          </h2>
          <div className="bg-purple-50 rounded-lg p-6 ml-12">
            <p className="text-lg text-gray-700 mb-4">
              Answer questions about the people in your life to strengthen your memory.
            </p>

            {/* Navigation Instructions */}
            <div className="bg-white border-2 border-purple-300 rounded-lg p-4 mb-4">
              <h4 className="font-bold text-purple-900 mb-3">How to get there:</h4>
              <ol className="space-y-3 text-gray-700">
                <li className="flex items-start">
                  <span className="bg-purple-600 text-white rounded-full w-6 h-6 flex items-center justify-center mr-3 flex-shrink-0 text-sm font-bold">1</span>
                  <span>Go to the Life Words main page</span>
                </li>
                <li className="flex items-start">
                  <span className="bg-purple-600 text-white rounded-full w-6 h-6 flex items-center justify-center mr-3 flex-shrink-0 text-sm font-bold">2</span>
                  <div>
                    <span>Click the big </span>
                    <span className="inline-flex items-center bg-purple-600 text-white rounded px-3 py-1 mx-1 text-sm font-semibold">
                      Question Practice
                    </span>
                    <span> button</span>
                  </div>
                </li>
              </ol>
            </div>

            {/* What you'll see */}
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-4">
              <h4 className="font-bold text-amber-900 mb-2">What you&apos;ll see:</h4>
              <ul className="space-y-2 text-gray-700">
                <li className="flex items-start">
                  <span className="text-purple-600 mr-2">•</span>
                  <span>A question about one of your contacts (with or without their photo)</span>
                </li>
                <li className="flex items-start">
                  <span className="text-purple-600 mr-2">•</span>
                  <span>A microphone button to record your answer</span>
                </li>
                <li className="flex items-start">
                  <span className="text-purple-600 mr-2">•</span>
                  <span>Progress indicator showing which question you&apos;re on</span>
                </li>
              </ul>
            </div>

            {/* Types of questions */}
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <h4 className="font-bold text-gray-900 mb-2">Types of questions you&apos;ll be asked:</h4>
              <ul className="space-y-2 text-gray-700 ml-4">
                <li><span className="text-purple-600 font-bold">•</span> &quot;What is [Name]&apos;s relationship to you?&quot;</li>
                <li><span className="text-purple-600 font-bold">•</span> &quot;Where do you usually see [Name]?&quot;</li>
                <li><span className="text-purple-600 font-bold">•</span> &quot;What does [Name] enjoy doing?&quot;</li>
                <li><span className="text-purple-600 font-bold">•</span> &quot;How would you describe [Name]&apos;s personality?&quot;</li>
                <li><span className="text-purple-600 font-bold">•</span> &quot;Who is your [relationship] who [hint]?&quot;</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Hints and Cues */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4 text-gray-900 flex items-center">
            <span className="text-3xl mr-3">💡</span>
            Hints When You&apos;re Stuck
          </h2>
          <div className="bg-amber-50 rounded-lg p-6 ml-12">
            <p className="text-lg text-gray-700 mb-4">
              If you need a little help, the app gives you hints to help you remember:
            </p>

            <div className="bg-white border border-amber-200 rounded-lg p-4 mb-4">
              <div className="space-y-4">
                <div className="flex items-start">
                  <span className="bg-amber-500 text-white rounded-full w-8 h-8 flex items-center justify-center mr-3 flex-shrink-0 font-bold">1</span>
                  <div>
                    <p className="font-bold text-gray-900">First try → First hint</p>
                    <p className="text-gray-600 text-sm">A contextual clue based on the question type</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <span className="bg-amber-500 text-white rounded-full w-8 h-8 flex items-center justify-center mr-3 flex-shrink-0 font-bold">2</span>
                  <div>
                    <p className="font-bold text-gray-900">Second try → Another hint</p>
                    <p className="text-gray-600 text-sm">Another helpful detail from their profile</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <span className="bg-green-500 text-white rounded-full w-8 h-8 flex items-center justify-center mr-3 flex-shrink-0 font-bold">✓</span>
                  <div>
                    <p className="font-bold text-gray-900">After 2 hints → Answer revealed</p>
                    <p className="text-gray-600 text-sm">The correct answer is shown so you can learn it</p>
                  </div>
                </div>
              </div>
            </div>

            <p className="text-gray-600 italic">
              The hints use information you&apos;ve entered about each person - their personality,
              interests, or where you typically see them. More details = better hints!
            </p>
          </div>
        </div>

        {/* Progress Tracking */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4 text-gray-900 flex items-center">
            <span className="text-3xl mr-3">📊</span>
            Tracking Your Progress
          </h2>
          <div className="bg-gray-50 rounded-lg p-6 ml-12">
            {/* Navigation Instructions */}
            <div className="bg-white border-2 border-green-300 rounded-lg p-4 mb-4">
              <h4 className="font-bold text-green-900 mb-3">How to get there:</h4>
              <ol className="space-y-3 text-gray-700">
                <li className="flex items-start">
                  <span className="bg-green-600 text-white rounded-full w-6 h-6 flex items-center justify-center mr-3 flex-shrink-0 text-sm font-bold">1</span>
                  <span>From the Life Words main page, find the icon grid</span>
                </li>
                <li className="flex items-start">
                  <span className="bg-green-600 text-white rounded-full w-6 h-6 flex items-center justify-center mr-3 flex-shrink-0 text-sm font-bold">2</span>
                  <div>
                    <span>Click the </span>
                    <span className="inline-flex items-center bg-gray-100 border border-gray-300 rounded px-2 py-1 mx-1">
                      <span className="text-lg mr-1">📊</span> Progress
                    </span>
                    <span> button</span>
                  </div>
                </li>
              </ol>
            </div>

            {/* What you'll see */}
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
              <h4 className="font-bold text-amber-900 mb-2">What you&apos;ll see:</h4>
              <ul className="space-y-2 text-gray-700">
                <li className="flex items-start">
                  <span className="text-green-600 mr-2">•</span>
                  <span><strong>Accuracy:</strong> How often you answer correctly (shown as a percentage)</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-600 mr-2">•</span>
                  <span><strong>Response Time:</strong> How quickly you respond to questions</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-600 mr-2">•</span>
                  <span><strong>Speech Clarity:</strong> How clearly the app understands you</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-600 mr-2">•</span>
                  <span><strong>Session History:</strong> A list of your recent practice sessions</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Answer Matching Settings */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4 text-gray-900 flex items-center">
            <span className="text-3xl mr-3">⚙️</span>
            Answer Matching Settings
          </h2>
          <div className="bg-gray-50 rounded-lg p-6 ml-12">
            {/* Navigation Instructions */}
            <div className="bg-white border-2 border-blue-300 rounded-lg p-4 mb-4">
              <h4 className="font-bold text-blue-900 mb-3">How to get there:</h4>
              <ol className="space-y-3 text-gray-700">
                <li className="flex items-start">
                  <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center mr-3 flex-shrink-0 text-sm font-bold">1</span>
                  <div>
                    <span>Click </span>
                    <span className="inline-flex items-center bg-gray-100 border border-gray-300 rounded px-2 py-1 mx-1">
                      <span className="text-lg mr-1">⚙️</span> Settings
                    </span>
                    <span> on the Life Words home page</span>
                  </div>
                </li>
                <li className="flex items-start">
                  <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center mr-3 flex-shrink-0 text-sm font-bold">2</span>
                  <span>Scroll down to the &quot;Answer Matching&quot; section</span>
                </li>
              </ol>
            </div>

            {/* What you'll see */}
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-4">
              <h4 className="font-bold text-amber-900 mb-2">What you can adjust:</h4>
              <ul className="space-y-2 text-gray-700">
                <li className="flex items-start">
                  <span className="text-blue-600 mr-2">☑️</span>
                  <span><strong>Synonym Matching:</strong> Accept similar words (e.g., &quot;kind&quot; for &quot;nice&quot;)</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-600 mr-2">☑️</span>
                  <span><strong>Partial Matching:</strong> Accept answers that partially match</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-600 mr-2">☑️</span>
                  <span><strong>Word Overlap:</strong> Accept answers with similar words</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-600 mr-2">☑️</span>
                  <span><strong>First Name Only:</strong> Accept just the first name for full names</span>
                </li>
              </ul>
            </div>

            <p className="text-gray-600 italic">
              Start with all options checked (easier), then uncheck them as your recall improves for a greater challenge.
            </p>
          </div>
        </div>

        {/* Tips */}
        <div className="bg-green-50 border-2 border-green-200 rounded-lg p-6 mb-6">
          <h2 className="text-2xl font-bold mb-4 text-gray-900">
            Tips for Success
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-gray-700">
            <div className="flex items-start">
              <span className="text-green-600 mr-2 text-xl">✓</span>
              <span>Practice in a quiet room for better speech recognition</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 mr-2 text-xl">✓</span>
              <span>Speak clearly and at a natural pace</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 mr-2 text-xl">✓</span>
              <span>Add detailed information about each contact for better hints</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 mr-2 text-xl">✓</span>
              <span>Practice regularly - even a few minutes helps</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 mr-2 text-xl">✓</span>
              <span>Use clear, well-lit photos for each contact</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 mr-2 text-xl">✓</span>
              <span>Click &quot;Done for now&quot; when you need a break</span>
            </div>
          </div>
        </div>

        {/* Quick Reference - Icon Grid */}
        <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-6 mb-6">
          <h2 className="text-2xl font-bold mb-4 text-gray-900">
            Quick Reference: Icon Grid
          </h2>
          <p className="text-gray-700 mb-4">
            On the Life Words main page, you&apos;ll see these icons at the bottom:
          </p>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-lg p-3 border border-gray-200">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-2xl">❓</span>
                <span className="font-bold">Instructions</span>
              </div>
              <p className="text-sm text-gray-600">This guide you&apos;re reading now</p>
            </div>
            <div className="bg-white rounded-lg p-3 border border-gray-200">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-2xl">📊</span>
                <span className="font-bold">Progress</span>
              </div>
              <p className="text-sm text-gray-600">See your practice statistics</p>
            </div>
            <div className="bg-white rounded-lg p-3 border border-gray-200">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-2xl">💬</span>
                <span className="font-bold">Messages</span>
              </div>
              <p className="text-sm text-gray-600">Messages from family/caregivers</p>
            </div>
            <div className="bg-white rounded-lg p-3 border border-gray-200">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-2xl">👥</span>
                <span className="font-bold">My People</span>
              </div>
              <p className="text-sm text-gray-600">Add or edit your people</p>
            </div>
            <div className="bg-white rounded-lg p-3 border border-gray-200">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-2xl">ℹ️</span>
                <span className="font-bold">My Info</span>
              </div>
              <p className="text-sm text-gray-600">Your personal information</p>
            </div>
            <div className="bg-white rounded-lg p-3 border border-gray-200">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-2xl">📦</span>
                <span className="font-bold">My Stuff</span>
              </div>
              <p className="text-sm text-gray-600">Items and belongings</p>
            </div>
            <div className="bg-white rounded-lg p-3 border border-gray-200">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-2xl">⚙️</span>
                <span className="font-bold">Settings</span>
              </div>
              <p className="text-sm text-gray-600">Voice and answer matching settings</p>
            </div>
          </div>
        </div>

        {/* Back Button */}
        <div className="text-center pt-4">
          <Link
            href="/dashboard/practice"
            className="inline-block bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-bold py-4 px-8 rounded-lg text-xl transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2"
          >
            Start Practicing
          </Link>
        </div>
      </div>
    </div>
  )
}
