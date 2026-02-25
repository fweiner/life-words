import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Life Words - Add Your Information',
  description: 'Help with memory recovery by adding your photo and information.',
}

export default function InviteLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-[var(--color-primary)]">
            Life Words
          </h1>
          <p className="text-gray-600 text-sm">Memory Rehabilitation Support</p>
        </div>
      </header>
      <main className="max-w-4xl mx-auto px-4 py-8">
        {children}
      </main>
      <footer className="bg-gray-50 border-t border-gray-200 mt-auto">
        <div className="max-w-4xl mx-auto px-4 py-6 text-center text-gray-500 text-sm">
          <p>Life Words</p>
          <p className="mt-1">Helping people recover, one memory at a time.</p>
        </div>
      </footer>
    </div>
  )
}
