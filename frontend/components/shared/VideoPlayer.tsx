'use client'

import { useRef, useState } from 'react'

export default function VideoPlayer({ src }: { src: string }) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [started, setStarted] = useState(false)

  function handlePlay() {
    const video = videoRef.current
    if (!video) return

    setStarted(true)
    // play() returns a promise — catch failures gracefully so the
    // native controls are still shown and the user can tap play again.
    video.play().catch(() => {
      // Browser blocked autoplay or video isn't ready yet.
      // Controls are now visible so the user can tap the native play button.
    })
  }

  return (
    <div className="relative rounded-xl overflow-hidden shadow-2xl ring-1 ring-white/10">
      <video
        ref={videoRef}
        className="w-full block"
        controls={started}
        preload="metadata"
        playsInline
      >
        <source src={src} type="video/mp4" />
        Your browser does not support the video tag.
      </video>

      {!started && (
        <button
          onClick={handlePlay}
          className="absolute inset-0 flex flex-col items-center justify-center bg-gray-900/80 cursor-pointer transition-colors hover:bg-gray-900/70 active:bg-gray-900/60"
          aria-label="Play video"
          type="button"
        >
          <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-full bg-white/90 flex items-center justify-center shadow-lg transition-transform hover:scale-110 active:scale-95">
            <svg
              className="w-10 h-10 sm:w-12 sm:h-12 text-gray-900 ml-1"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M8 5v14l11-7z" />
            </svg>
          </div>
          <span className="mt-4 text-white/80 text-lg font-medium">Watch the demo</span>
        </button>
      )}
    </div>
  )
}
