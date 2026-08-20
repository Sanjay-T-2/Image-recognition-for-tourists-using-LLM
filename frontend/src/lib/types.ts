export type TransportMode = 'flight' | 'train' | 'bus' | 'car' | 'ferry'

export type Preference =
  | 'low_cost'
  | 'high_comfort'
  | 'fewer_days'
  | 'more_days'
  | 'balanced'

export interface Place {
  name: string
  display_name: string
  lat: number
  lon: number
  country?: string | null
  country_code?: string | null
  category?: string | null
}

export interface FollowUpQuestion {
  id: string
  question: string
  options: string[]
  multi: boolean
}

export interface IdentifyResponse {
  destination: Place
  origin: Place | null
  source: 'text' | 'image'
  confidence: number
  summary: string
  questions: FollowUpQuestion[]
}

export interface BookingLink {
  provider: string
  url: string
}

export interface TransportOption {
  mode: TransportMode
  label: string
  distance_km: number
  duration_hours: number
  cost_min: number
  cost_max: number
  currency: string
  comfort: number
  notes: string
  recommended: boolean
  booking: BookingLink[]
}

export interface TransportHub {
  name: string
  kind: 'bus_station' | 'railway_station' | 'airport' | 'ferry_terminal'
  lat: number
  lon: number
  distance_km: number
  side: 'origin' | 'destination'
}

export interface RouteResponse {
  straight_line_km: number
  road_km: number | null
  road_duration_hours: number | null
  preference: Preference
  options: TransportOption[]
  hubs: TransportHub[]
}

export interface CostLine {
  label: string
  amount: number
  detail: string
}

export interface StayEstimateResponse {
  currency: string
  days: number
  travellers: number
  start_date: string | null
  end_date: string | null
  minimum_total: number
  comfortable_total: number
  per_day_minimum: number
  breakdown: CostLine[]
  tips: string[]
}

export interface Hospital {
  name: string
  lat: number
  lon: number
  distance_km: number
  phone: string | null
  emergency: boolean
}

export interface Hotel {
  name: string
  lat: number
  lon: number
  distance_km: number
  stars: string | null
  price_band: string
  booking_url: string
}

export interface Attraction {
  name: string
  kind: string
  lat: number
  lon: number
  distance_km: number
}

export interface DestinationInfo {
  place: Place
  history: string
  history_url: string | null
  attractions: Attraction[]
  hotels: Hotel[]
  hospitals: Hospital[]
  emergency_numbers: Record<string, string>
}
