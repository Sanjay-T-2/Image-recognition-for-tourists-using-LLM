import { useRef, useState } from 'react'

interface Props {
  loading: boolean
  onSubmit: (input: {
    query?: string
    image_base64?: string
    origin?: string
    origin_coords?: { lat: number; lon: number }
  }) => void
}

function toBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result).split(',')[1] ?? '')
    reader.onerror = () => reject(new Error('Could not read the image'))
    reader.readAsDataURL(file)
  })
}

export function DestinationInput({ loading, onSubmit }: Props) {
  const [query, setQuery] = useState('')
  const [origin, setOrigin] = useState('')
  const [coords, setCoords] = useState<{ lat: number; lon: number } | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [imageBase64, setImageBase64] = useState<string | null>(null)
  const [locating, setLocating] = useState(false)
  const fileInput = useRef<HTMLInputElement>(null)

  async function handleFile(file: File | undefined) {
    if (!file) return
    const base64 = await toBase64(file)
    setImageBase64(base64)
    setPreview(URL.createObjectURL(file))
  }

  function useMyLocation() {
    setLocating(true)
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setCoords({ lat: position.coords.latitude, lon: position.coords.longitude })
        setOrigin('')
        setLocating(false)
      },
      () => setLocating(false),
      { timeout: 10000 },
    )
  }

  return (
    <section className="card hero">
      <h1>Where do you want to go?</h1>
      <p className="muted">
        Type a place name or upload a photo of a tourist spot. We work out the distance, the best
        way to get there, what the trip costs and everything you need on the ground.
      </p>

      <div className="field">
        <label htmlFor="place">Destination</label>
        <input
          id="place"
          placeholder="e.g. Taj Mahal, Munnar, Eiffel Tower"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
      </div>

      <div className="field">
        <label htmlFor="photo">…or a photo of the place</label>
        <input
          id="photo"
          ref={fileInput}
          type="file"
          accept="image/*"
          onChange={(event) => handleFile(event.target.files?.[0])}
        />
        {preview && <img className="preview" src={preview} alt="Selected place" />}
        {preview && query.trim() && (
          <p className="muted">The typed destination is used — clear it to plan from the photo.</p>
        )}
      </div>

      <div className="field">
        <label htmlFor="origin">Starting from</label>
        <div className="row">
          <input
            id="origin"
            placeholder="Your city"
            value={coords ? `${coords.lat.toFixed(3)}, ${coords.lon.toFixed(3)}` : origin}
            onChange={(event) => {
              setCoords(null)
              setOrigin(event.target.value)
            }}
          />
          <button type="button" className="ghost" onClick={useMyLocation} disabled={locating}>
            {locating ? 'Locating…' : 'Use my location'}
          </button>
        </div>
      </div>

      <button
        className="primary"
        disabled={loading || (!query.trim() && !imageBase64)}
        onClick={() =>
          onSubmit({
            query: query.trim() || undefined,
            image_base64: imageBase64 ?? undefined,
            origin: coords ? undefined : origin.trim() || undefined,
            origin_coords: coords ?? undefined,
          })
        }
      >
        {loading ? 'Analysing…' : 'Plan my trip'}
      </button>
    </section>
  )
}
