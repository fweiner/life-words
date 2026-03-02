import Link from 'next/link'
import Image from 'next/image'
import VideoPlayer from '@/components/shared/VideoPlayer'

const FEATURES = [
  'Personalized name practice with photos',
  'Question-based memory recall',
  'Personal information practice',
  'Progress tracking and statistics',
  'Voice recognition with accommodations',
  'Messaging with family and caregivers',
  'Unlimited contacts and items',
]

const CONDITIONS = [
  {
    name: 'Aphasia',
    description: 'Language difficulties after stroke',
  },
  {
    name: 'Traumatic Brain Injury',
    description: 'Memory and word-finding challenges from TBI',
  },
  {
    name: "Alzheimer's & Dementia",
    description: 'Progressive memory and communication support',
  },
  {
    name: 'Neurological Conditions',
    description: 'Other conditions affecting memory and language',
  },
]

export default function HomePage() {
  return (
    <div className="min-h-screen bg-[var(--color-background)]">
      {/* Header */}
      <header className="bg-white border-b-2 border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <Link href="/" className="flex items-center space-x-2 sm:space-x-3">
              <Image
                src="/header.jpg"
                alt="Life Words Logo"
                width={50}
                height={50}
                className="object-contain w-10 h-10 sm:w-[50px] sm:h-[50px]"
              />
              <div className="text-xl sm:text-3xl font-bold text-[var(--color-primary)]">
                Life Words
              </div>
            </Link>
            <Link
              href="/login"
              className="text-[var(--color-primary)] hover:text-[var(--color-primary-hover)] font-semibold text-lg"
            >
              Sign In
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="bg-gradient-to-b from-blue-50 to-white py-16 sm:py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6 leading-tight">
            Rebuild Your Words,{' '}
            <span className="text-[var(--color-primary)]">Reclaim Your Life</span>
          </h1>
          <p className="text-xl sm:text-2xl text-gray-600 mb-10 max-w-3xl mx-auto leading-relaxed">
            A personalized platform for people with word-finding and memory
            difficulties. Practice with your own photos, people, and meaningful content
            &mdash; right from home.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/dashboard"
              className="bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-bold py-4 px-8 rounded-lg text-xl transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2"
              style={{ minHeight: '44px' }}
            >
              Start Practice
            </Link>
            <Link
              href="/signup"
              className="border-2 border-[var(--color-primary)] text-[var(--color-primary)] hover:bg-blue-50 font-bold py-4 px-8 rounded-lg text-xl transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2"
              style={{ minHeight: '44px' }}
            >
              Create an Account
            </Link>
          </div>
        </div>
      </section>

      {/* Video Section */}
      <section className="bg-gray-900 py-16 sm:py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
            See Life Words in Action
          </h2>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Watch how Life Words helps people practice recalling names, faces, and personal
            information from the comfort of home.
          </p>
          <VideoPlayer src="/videos/life-words.mp4" />
        </div>
      </section>

      {/* Who It's For Section */}
      <section id="who-its-for" className="py-16 sm:py-20 px-4 sm:px-6 lg:px-8 scroll-mt-20">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Who Life Words Is For
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Life Words is built for people who have difficulty recalling words, names, or
              personal information &mdash; and for the families and therapists who support them.
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {CONDITIONS.map((condition) => (
              <div
                key={condition.name}
                className="bg-white rounded-xl border-2 border-gray-200 p-6 sm:p-8"
              >
                <h3 className="text-xl font-bold text-gray-900 mb-2">{condition.name}</h3>
                <p className="text-lg text-gray-600">{condition.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* The Science Section */}
      <section className="bg-blue-50 py-16 sm:py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-10">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              The Science Behind It
            </h2>
          </div>
          <div className="bg-white rounded-2xl border-2 border-gray-200 p-8 sm:p-10">
            <div className="space-y-6 text-lg text-gray-700 leading-relaxed">
              <p>
                <strong className="text-gray-900">Your brain can adapt.</strong> After a stroke,
                brain injury, or during a neurological condition, the areas responsible for
                language and memory may be damaged &mdash; but the brain has a remarkable ability
                called <strong className="text-gray-900">neuroplasticity</strong>.
              </p>
              <p>
                Neuroplasticity means your brain can form new neural pathways to work around
                damaged areas. With consistent, targeted practice, healthy parts of the brain
                can take over functions that were lost.
              </p>
              <p>
                <strong className="text-gray-900">Life Words puts this science into action.</strong>{' '}
                By practicing with your own photos, real names, and personally meaningful
                content, you strengthen the connections that matter most to your daily life.
                Repeated practice with familiar faces and personal information builds stronger,
                more durable recall.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 sm:py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              How Life Words Helps
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Tools designed specifically for people with word-finding and memory difficulties.
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
              <div className="text-3xl mb-3" aria-hidden="true">&#128247;</div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Your Photos, Your Practice</h3>
              <p className="text-lg text-gray-600">
                Upload photos of the people and things in your life. Practice recalling their
                names with images that are meaningful to you.
              </p>
            </div>
            <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
              <div className="text-3xl mb-3" aria-hidden="true">&#128172;</div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Name &amp; Memory Recall</h3>
              <p className="text-lg text-gray-600">
                Practice recalling names, answering personal questions, and retrieving important
                information through guided exercises.
              </p>
            </div>
            <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
              <div className="text-3xl mb-3" aria-hidden="true">&#127908;</div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Voice Recognition</h3>
              <p className="text-lg text-gray-600">
                Speak your answers out loud. Our voice recognition is tuned to accommodate
                speech difficulties common in aphasia and brain injury.
              </p>
            </div>
            <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
              <div className="text-3xl mb-3" aria-hidden="true">&#128200;</div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Track Your Progress</h3>
              <p className="text-lg text-gray-600">
                See how your recall improves over time with clear progress tracking. Celebrate
                wins and identify areas for more practice.
              </p>
            </div>
            <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
              <div className="text-3xl mb-3" aria-hidden="true">&#128106;</div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Family Messaging</h3>
              <p className="text-lg text-gray-600">
                Stay connected with family and caregivers through built-in messaging. They can
                encourage you and follow your progress.
              </p>
            </div>
            <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
              <div className="text-3xl mb-3" aria-hidden="true">&#9989;</div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Built for Accessibility</h3>
              <p className="text-lg text-gray-600">
                Large text, simple navigation, and high contrast design. Made to be easy to use
                for people of all ages and abilities.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="bg-blue-50 py-16 sm:py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Simple, Affordable Pricing
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Personalized aphasia therapy tools designed for everyday practice.
            </p>
          </div>

          {/* Plan Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
            {/* Monthly Plan */}
            <div className="bg-white rounded-2xl shadow-lg border-2 border-gray-200 p-8 flex flex-col">
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Monthly</h3>
              <div className="mb-6">
                <span className="text-5xl font-bold text-gray-900">$9.95</span>
                <span className="text-xl text-gray-500">/month</span>
              </div>
              <ul className="space-y-3 mb-8 flex-1">
                {FEATURES.map((feature) => (
                  <li key={feature} className="flex items-start text-lg">
                    <span className="text-green-600 mr-3 mt-0.5 flex-shrink-0">&#10003;</span>
                    <span className="text-gray-700">{feature}</span>
                  </li>
                ))}
              </ul>
              <Link
                href="/dashboard/subscribe"
                className="block w-full text-center bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-bold py-4 px-6 rounded-lg text-xl transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                style={{ minHeight: '44px' }}
              >
                Purchase Subscription
              </Link>
            </div>

            {/* Yearly Plan */}
            <div className="bg-white rounded-2xl shadow-lg border-2 border-[var(--color-primary)] p-8 flex flex-col relative">
              <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-[var(--color-primary)] text-white text-sm font-bold py-1 px-4 rounded-full">
                Save ~$20/year
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Yearly</h3>
              <div className="mb-2">
                <span className="text-5xl font-bold text-gray-900">$99.95</span>
                <span className="text-xl text-gray-500">/year</span>
              </div>
              <p className="text-lg text-gray-500 mb-6">Just $8.33/month</p>
              <ul className="space-y-3 mb-8 flex-1">
                {FEATURES.map((feature) => (
                  <li key={feature} className="flex items-start text-lg">
                    <span className="text-green-600 mr-3 mt-0.5 flex-shrink-0">&#10003;</span>
                    <span className="text-gray-700">{feature}</span>
                  </li>
                ))}
              </ul>
              <Link
                href="/dashboard/subscribe"
                className="block w-full text-center bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-bold py-4 px-6 rounded-lg text-xl transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                style={{ minHeight: '44px' }}
              >
                Purchase Subscription
              </Link>
            </div>
          </div>

          <div className="text-center text-gray-500 text-lg">
            <p>Cancel anytime from your account settings.</p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-5xl mx-auto">
          <div className="flex flex-col sm:flex-row justify-between items-center gap-6">
            <div className="flex items-center space-x-3">
              <Image
                src="/header.jpg"
                alt="Life Words Logo"
                width={40}
                height={40}
                className="object-contain rounded"
              />
              <span className="text-xl font-bold">Life Words</span>
            </div>
            <nav className="flex items-center space-x-6">
              <Link href="/login" className="text-gray-300 hover:text-white text-lg transition-colors">
                Sign In
              </Link>
              <Link href="/pricing" className="text-gray-300 hover:text-white text-lg transition-colors">
                Pricing
              </Link>
              <Link href="/signup" className="text-gray-300 hover:text-white text-lg transition-colors">
                Create an Account
              </Link>
            </nav>
          </div>
          <div className="mt-8 pt-6 border-t border-gray-700 text-center text-gray-400">
            <p>Personalized therapy for word-finding and memory recovery.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
