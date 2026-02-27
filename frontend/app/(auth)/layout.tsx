import Image from 'next/image'
import Link from 'next/link'

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-[var(--color-background)]">
      <header className="bg-white border-b-2 border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-center items-center h-20">
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
          </div>
        </div>
      </header>
      <div className="flex items-center justify-center p-4 mt-8">
        <div className="w-full max-w-md">
          {children}
        </div>
      </div>
    </div>
  )
}
