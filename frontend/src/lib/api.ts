import type {
  DestinationInfo,
  IdentifyResponse,
  Place,
  Preference,
  RouteResponse,
  StayEstimateResponse,
} from './types'

const BASE = import.meta.env.VITE_API_BASE ?? '/api'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!response.ok) {
    const detail = await response.json().catch(() => null)
    throw new Error(detail?.detail ?? `Request failed (${response.status})`)
  }
  return response.json() as Promise<T>
}

export function identify(body: {
  query?: string
  image_base64?: string
  origin?: string
  origin_coords?: { lat: number; lon: number }
}): Promise<IdentifyResponse> {
  return request<IdentifyResponse>('/identify', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export function route(body: {
  origin: { lat: number; lon: number }
  destination: { lat: number; lon: number }
  origin_label: string
  destination_label: string
  preference: Preference
  currency: string
}): Promise<RouteResponse> {
  return request<RouteResponse>('/route', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export function stayEstimate(body: {
  destination: { lat: number; lon: number }
  destination_label: string
  days: number
  travellers: number
  start_date?: string | null
  style: 'budget' | 'standard' | 'premium'
  transport_cost: number
  currency: string
}): Promise<StayEstimateResponse> {
  return request<StayEstimateResponse>('/stay-estimate', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export function destinationInfo(
  place: Pick<Place, 'lat' | 'lon' | 'name'>,
): Promise<DestinationInfo> {
  const params = new URLSearchParams({
    lat: String(place.lat),
    lon: String(place.lon),
    name: place.name,
  })
  return request<DestinationInfo>(`/destination-info?${params.toString()}`)
}

export function currencyFor(
  lat: number,
  lon: number,
): Promise<{ currency: string; country_code: string }> {
  return request(`/currency?lat=${lat}&lon=${lon}`)
}
