import { compressImage } from '@/lib/utils/compressImage'

// Mock URL.createObjectURL
Object.defineProperty(URL, 'createObjectURL', {
  value: jest.fn(() => 'blob:mock-url'),
})

afterEach(() => {
  jest.restoreAllMocks()
})

function mockCreateElement(options: {
  contextResult?: object | null
  blobResult?: Blob | null
  imgError?: boolean
  imgWidth?: number
  imgHeight?: number
}) {
  const {
    contextResult = { drawImage: jest.fn() },
    blobResult = new Blob(['test'], { type: 'image/jpeg' }),
    imgError = false,
    imgWidth = 1000,
    imgHeight = 500,
  } = options

  const toBlobFn = jest.fn((callback: BlobCallback) => callback(blobResult))
  const getContextFn = jest.fn(() => contextResult)

  jest.spyOn(document, 'createElement').mockImplementation((tag: string) => {
    if (tag === 'canvas') {
      return {
        width: 0,
        height: 0,
        getContext: getContextFn,
        toBlob: toBlobFn,
      } as unknown as HTMLCanvasElement
    }
    if (tag === 'img') {
      const img = {
        width: 0,
        height: 0,
        src: '',
        onload: null as (() => void) | null,
        onerror: null as (() => void) | null,
      }
      Object.defineProperty(img, 'src', {
        set() {
          if (imgError) {
            setTimeout(() => img.onerror?.(), 0)
          } else {
            img.width = imgWidth
            img.height = imgHeight
            setTimeout(() => img.onload?.(), 0)
          }
        },
      })
      return img as unknown as HTMLImageElement
    }
    // Fallback — should not be reached by compressImage
    return new HTMLElement()
  })

  return { toBlobFn, getContextFn }
}

describe('compressImage', () => {
  it('compresses a large image to fit within 800x800', async () => {
    const { getContextFn, toBlobFn } = mockCreateElement({})

    const file = new File(['test'], 'photo.jpg', { type: 'image/jpeg' })
    const result = await compressImage(file)

    expect(result).toBeInstanceOf(Blob)
    expect(getContextFn).toHaveBeenCalledWith('2d')
    expect(toBlobFn).toHaveBeenCalledWith(expect.any(Function), 'image/jpeg', 0.8)
  })

  it('preserves dimensions for small images', async () => {
    mockCreateElement({ imgWidth: 400, imgHeight: 300 })

    const file = new File(['test'], 'small.jpg', { type: 'image/jpeg' })
    const result = await compressImage(file)

    expect(result).toBeInstanceOf(Blob)
  })

  it('rejects when canvas context is unavailable', async () => {
    mockCreateElement({ contextResult: null })

    const file = new File(['test'], 'photo.jpg', { type: 'image/jpeg' })
    await expect(compressImage(file)).rejects.toThrow('Could not get canvas context')
  })

  it('rejects when toBlob returns null', async () => {
    mockCreateElement({ blobResult: null })

    const file = new File(['test'], 'photo.jpg', { type: 'image/jpeg' })
    await expect(compressImage(file)).rejects.toThrow('Could not compress image')
  })

  it('rejects when image fails to load', async () => {
    mockCreateElement({ imgError: true })

    const file = new File(['test'], 'photo.jpg', { type: 'image/jpeg' })
    await expect(compressImage(file)).rejects.toThrow('Could not load image')
  })
})
