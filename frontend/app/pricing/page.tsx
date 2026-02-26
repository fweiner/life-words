import Link from 'next/link'
import Image from 'next/image'

const FEATURES = [
  'Personalized name practice with photos',
  'Question-based memory recall',
  'Personal information practice',
  'Progress tracking and statistics',
  'Voice recognition with accommodations',
  'Messaging with family and caregivers',
  'Unlimited contacts and items',
]

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-[var(--color-background)]">
      {/* Header */}
      <header className="bg-white border-b-2 border-gray-200">
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

      {/* Pricing Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">
            Simple, Affordable Pricing
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Personalized aphasia therapy tools designed for everyday practice.
          </p>
        </div>

        {/* Plan Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
          {/* Monthly Plan */}
          <div className="bg-white rounded-2xl shadow-lg border-2 border-gray-200 p-8 flex flex-col">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Monthly</h2>
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
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Yearly</h2>
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

        {/* Footer note */}
        <div className="text-center text-gray-500 text-lg">
          <p>Secure payment powered by Stripe. Cancel anytime from your account settings.</p>
        </div>
      </div>
    </div>
  )
}
