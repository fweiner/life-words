import '@testing-library/jest-dom'

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
    back: jest.fn(),
  }),
  useSearchParams: () => ({
    get: jest.fn(),
  }),
  usePathname: () => '',
  useParams: () => ({}),
  notFound: jest.fn(),
}))

// Mock next/image (render as plain <img>)
jest.mock('next/image', () => ({
  __esModule: true,
  default: (props) => {
    // eslint-disable-next-line @next/next/no-img-element, jsx-a11y/alt-text
    return <img {...props} />
  },
}))

// Mock window.speechSynthesis
Object.defineProperty(window, 'speechSynthesis', {
  value: {
    speak: jest.fn(),
    cancel: jest.fn(),
    getVoices: jest.fn(() => []),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
  },
  writable: true,
})

// Mock SpeechSynthesisUtterance
global.SpeechSynthesisUtterance = jest.fn().mockImplementation(() => ({
  rate: 1,
  pitch: 1,
  volume: 1,
}))

// Mock navigator.mediaDevices.getUserMedia
Object.defineProperty(navigator, 'mediaDevices', {
  value: {
    getUserMedia: jest.fn().mockResolvedValue({
      getTracks: () => [],
    }),
    enumerateDevices: jest.fn().mockResolvedValue([]),
  },
  writable: true,
})

// Suppress ReactDOM.render warnings
const originalError = console.error
beforeAll(() => {
  console.error = (...args) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Warning: ReactDOM.render')
    ) {
      return
    }
    originalError.call(console, ...args)
  }
})

afterAll(() => {
  console.error = originalError
})
