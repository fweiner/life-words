import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'How It Works',
  description:
    'See how Life Words helps people with aphasia and memory difficulties practice recalling names, faces, and personal information with personalized exercises.',
}

export default function InformationLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return children
}
