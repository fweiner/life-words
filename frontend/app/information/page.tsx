"use client";

import Link from "next/link";
import "./promo.css";
import { AnimatedSection } from "./_components/AnimatedSection";
import { MockDashboard } from "./_components/MockDashboard";
import { MockPracticeHub } from "./_components/MockPracticeHub";
import { MockContacts } from "./_components/MockContacts";
import { MockSession } from "./_components/MockSession";
import { MockProgress } from "./_components/MockProgress";

const features = [
  {
    icon: "🗣️",
    title: "Voice-Powered Practice",
    description:
      "Speak your answers and get instant feedback with speech recognition technology.",
  },
  {
    icon: "❤️",
    title: "Personalized Content",
    description:
      "Practice with the people, places, and things that matter most in your life.",
  },
  {
    icon: "📈",
    title: "Track Your Progress",
    description:
      "See your improvement over time with detailed accuracy and session tracking.",
  },
];

export default function InformationPage() {
  return (
    <div className="min-h-screen bg-[var(--color-background)]">
      {/* Header */}
      <header className="bg-white border-b-2 border-gray-200 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
          <Link
            href="/"
            className="text-xl font-bold text-[var(--color-primary)]"
          >
            Life Words
          </Link>
          <div className="flex gap-3">
            <Link
              href="/login"
              className="text-sm font-medium text-gray-600 hover:text-gray-900 py-2 px-3"
            >
              Sign In
            </Link>
            <Link
              href="/login"
              className="text-sm font-medium text-white bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] py-2 px-4 rounded-lg transition-colors"
              style={{ minHeight: 44 }}
            >
              Get Started
            </Link>
          </div>
        </div>
      </header>

      {/* Section 1: Hero */}
      <section className="py-20 sm:py-28 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-blue-50 via-white to-purple-50 text-center">
        <AnimatedSection>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
            See How Life Words Works
          </h1>
          <p className="text-xl sm:text-2xl text-gray-600 max-w-2xl mx-auto mb-10">
            A personalized aphasia therapy app that helps you practice speaking
            with the words that matter most.
          </p>
          <div className="promo-bounce inline-block text-gray-400">
            <svg
              className="w-8 h-8"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M19 14l-7 7m0 0l-7-7m7 7V3"
              />
            </svg>
          </div>
        </AnimatedSection>
      </section>

      {/* Section 2: Dashboard */}
      <section className="py-16 sm:py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-5xl mx-auto flex flex-col lg:flex-row items-center gap-10 lg:gap-16">
          <AnimatedSection className="flex-1 text-center lg:text-left">
            <span className="inline-block text-sm font-semibold text-blue-600 bg-blue-100 px-3 py-1 rounded-full mb-4">
              Step 1
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Start with your personal dashboard
            </h2>
            <p className="text-lg text-gray-600">
              Your home base shows recent activity, quick practice shortcuts, and
              progress at a glance. Everything is designed for clarity and ease
              of use.
            </p>
          </AnimatedSection>
          <AnimatedSection animation="promo-slide-right">
            <MockDashboard />
          </AnimatedSection>
        </div>
      </section>

      {/* Section 3: Practice Hub */}
      <section className="py-16 sm:py-24 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="max-w-5xl mx-auto flex flex-col-reverse lg:flex-row items-center gap-10 lg:gap-16">
          <AnimatedSection animation="promo-slide-left">
            <MockPracticeHub />
          </AnimatedSection>
          <AnimatedSection className="flex-1 text-center lg:text-left">
            <span className="inline-block text-sm font-semibold text-purple-600 bg-purple-100 px-3 py-1 rounded-full mb-4">
              Step 2
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Choose your practice type
            </h2>
            <p className="text-lg text-gray-600">
              Pick from naming practice, word finding, or Life Words sessions.
              Each mode targets different language skills with personalized
              content.
            </p>
          </AnimatedSection>
        </div>
      </section>

      {/* Section 4: Contacts */}
      <section className="py-16 sm:py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-5xl mx-auto flex flex-col lg:flex-row items-center gap-10 lg:gap-16">
          <AnimatedSection className="flex-1 text-center lg:text-left">
            <span className="inline-block text-sm font-semibold text-green-600 bg-green-100 px-3 py-1 rounded-full mb-4">
              Step 3
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Add the people and things that matter
            </h2>
            <p className="text-lg text-gray-600">
              Upload photos of family, friends, pets, and favorite things. Your
              practice sessions use these personal connections to make therapy
              meaningful.
            </p>
          </AnimatedSection>
          <AnimatedSection animation="promo-fade-up">
            <MockContacts />
          </AnimatedSection>
        </div>
      </section>

      {/* Section 5: Practice Session (star section) */}
      <section className="py-16 sm:py-24 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-blue-50 to-green-50">
        <div className="max-w-3xl mx-auto text-center">
          <AnimatedSection>
            <span className="inline-block text-sm font-semibold text-blue-600 bg-blue-100 px-3 py-1 rounded-full mb-4">
              Step 4
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Speak your answer
            </h2>
            <p className="text-lg text-gray-600 mb-10">
              Tap the microphone, say the name, and get instant feedback.
              The app listens, evaluates your response, and celebrates your
              success.
            </p>
          </AnimatedSection>
          <AnimatedSection animation="promo-fade-up" delay="0.2s">
            <div className="flex justify-center">
              <MockSession />
            </div>
          </AnimatedSection>
        </div>
      </section>

      {/* Section 6: Progress */}
      <section className="py-16 sm:py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-5xl mx-auto flex flex-col lg:flex-row items-center gap-10 lg:gap-16">
          <AnimatedSection animation="promo-slide-left">
            <MockProgress />
          </AnimatedSection>
          <AnimatedSection className="flex-1 text-center lg:text-left">
            <span className="inline-block text-sm font-semibold text-amber-600 bg-amber-100 px-3 py-1 rounded-full mb-4">
              Step 5
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Track your improvement over time
            </h2>
            <p className="text-lg text-gray-600">
              Watch your accuracy climb, maintain practice streaks, and see how
              many items you&apos;ve mastered. Share progress with your therapist
              to guide treatment.
            </p>
          </AnimatedSection>
        </div>
      </section>

      {/* Section 7: Feature Summary */}
      <section className="py-16 sm:py-24 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="max-w-5xl mx-auto">
          <AnimatedSection className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Why Life Words?
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Built specifically for people with aphasia, by speech-language
              pathology experts.
            </p>
          </AnimatedSection>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            {features.map((f, i) => (
              <AnimatedSection key={f.title} delay={`${i * 0.15}s`}>
                <div className="bg-white rounded-2xl border-2 border-gray-200 p-6 text-center h-full">
                  <span className="text-4xl block mb-4">{f.icon}</span>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">
                    {f.title}
                  </h3>
                  <p className="text-gray-600">{f.description}</p>
                </div>
              </AnimatedSection>
            ))}
          </div>
        </div>
      </section>

      {/* Section 8: CTA */}
      <section className="py-20 sm:py-28 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-blue-600 to-blue-800 text-center">
        <AnimatedSection>
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
            Ready to start your journey?
          </h2>
          <p className="text-lg text-blue-100 max-w-xl mx-auto mb-8">
            Join families and therapists already using Life Words to make
            aphasia therapy personal and effective.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/login"
              className="inline-flex items-center justify-center text-lg font-semibold bg-white text-blue-700 hover:bg-blue-50 py-3 px-8 rounded-xl transition-colors"
              style={{ minHeight: 44 }}
            >
              Sign In
            </Link>
            <Link
              href="/pricing"
              className="inline-flex items-center justify-center text-lg font-semibold border-2 border-white text-white hover:bg-white/10 py-3 px-8 rounded-xl transition-colors"
              style={{ minHeight: 44 }}
            >
              Learn More
            </Link>
          </div>
        </AnimatedSection>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-sm text-gray-400">
            &copy; {new Date().getFullYear()} Parrot Software. All rights
            reserved.
          </p>
          <div className="flex gap-6">
            <Link
              href="/"
              className="text-sm text-gray-400 hover:text-white transition-colors"
            >
              Home
            </Link>
            <Link
              href="/pricing"
              className="text-sm text-gray-400 hover:text-white transition-colors"
            >
              Pricing
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
