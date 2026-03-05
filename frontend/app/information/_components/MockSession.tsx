/* eslint-disable @next/next/no-img-element */
import { PhoneMockup } from "./PhoneMockup";

export function MockSession() {
  return (
    <PhoneMockup>
      <div className="relative" style={{ minHeight: 340 }}>
        {/* Shared question prompt */}
        <div className="mb-6">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">
            Name this person
          </p>
          <div className="flex justify-center">
            <img
              src="/images/sarah.jpg"
              alt=""
              className="w-20 h-20 rounded-full object-cover"
            />
          </div>
          <p className="text-center text-sm text-gray-500 mt-2">
            Your daughter
          </p>
        </div>

        {/* Phase 1: Idle */}
        <div className="absolute inset-x-0 bottom-0 flex flex-col items-center promo-session-idle">
          <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center mb-2">
            <svg
              className="w-8 h-8 text-blue-600"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
              <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
            </svg>
          </div>
          <p className="text-sm font-medium text-blue-600">Tap to speak</p>
        </div>

        {/* Phase 2: Listening */}
        <div className="absolute inset-x-0 bottom-0 flex flex-col items-center promo-session-listening">
          <div className="w-16 h-16 rounded-full bg-green-500 flex items-center justify-center mb-2 promo-mic-pulse">
            <svg
              className="w-8 h-8 text-white"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
              <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
            </svg>
          </div>
          <p className="text-sm font-medium text-green-600">Listening...</p>
        </div>

        {/* Phase 3: Success */}
        <div className="absolute inset-x-0 bottom-0 flex flex-col items-center promo-session-success">
          <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mb-2">
            <svg
              className="w-8 h-8 text-green-600"
              fill="none"
              stroke="currentColor"
              strokeWidth={3}
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
          <p className="text-sm font-bold text-green-700">
            You said: &quot;Sarah&quot;
          </p>
          <p className="text-xs text-green-600 mt-1">Correct!</p>
        </div>
      </div>
    </PhoneMockup>
  );
}
