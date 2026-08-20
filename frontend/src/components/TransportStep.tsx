import { HUB_LABEL, MODE_ICON, duration, money } from '../lib/format'
import type { Preference, RouteResponse, TransportOption } from '../lib/types'

const PREFERENCES: { value: Preference; label: string }[] = [
  { value: 'balanced', label: 'Balanced' },
  { value: 'low_cost', label: 'Low cost' },
  { value: 'high_comfort', label: 'High comfort' },
  { value: 'fewer_days', label: 'Fewer days on the road' },
  { value: 'more_days', label: 'More days / scenic' },
]

interface Props {
  route: RouteResponse
  originName: string
  destinationName: string
  preference: Preference
  selected: TransportOption | null
  loading: boolean
  onPreference: (preference: Preference) => void
  onSelect: (option: TransportOption) => void
}

export function TransportStep({
  route,
  originName,
  destinationName,
  preference,
  selected,
  loading,
  onPreference,
  onSelect,
}: Props) {
  const originHubs = route.hubs.filter((hub) => hub.side === 'origin')
  const destinationHubs = route.hubs.filter((hub) => hub.side === 'destination')

  return (
    <section className="card">
      <h2>
        {originName} → {destinationName}
      </h2>
      <div className="stats">
        <div>
          <span className="stat">{route.straight_line_km.toLocaleString()} km</span>
          <span className="muted">straight-line distance</span>
        </div>
        {route.road_km !== null && (
          <div>
            <span className="stat">{route.road_km.toLocaleString()} km</span>
            <span className="muted">by road</span>
          </div>
        )}
        {route.road_duration_hours !== null && (
          <div>
            <span className="stat">{duration(route.road_duration_hours)}</span>
            <span className="muted">driving time</span>
          </div>
        )}
      </div>

      <div className="chips">
        {PREFERENCES.map((item) => (
          <button
            key={item.value}
            type="button"
            className={preference === item.value ? 'chip selected' : 'chip'}
            onClick={() => onPreference(item.value)}
          >
            {item.label}
          </button>
        ))}
      </div>

      {loading && <p className="muted">Recalculating options…</p>}

      <div className="options">
        {route.options.map((option) => (
          <article
            key={option.mode}
            className={
              selected?.mode === option.mode ? 'option selected' : 'option'
            }
          >
            <header>
              <span className="mode">
                {MODE_ICON[option.mode]} {option.label}
              </span>
              {option.recommended && <span className="badge">Recommended</span>}
            </header>
            <div className="option-grid">
              <div>
                <strong>{money(option.cost_min, option.currency)}</strong>–
                {money(option.cost_max, option.currency)}
                <span className="muted"> per person</span>
              </div>
              <div>{duration(option.duration_hours)}</div>
              <div>{option.distance_km.toLocaleString()} km</div>
              <div>{'★'.repeat(option.comfort)}</div>
            </div>
            <p className="muted">{option.notes}</p>
            <button type="button" className="secondary" onClick={() => onSelect(option)}>
              {selected?.mode === option.mode ? 'Selected' : `Choose ${option.label.toLowerCase()}`}
            </button>
          </article>
        ))}
      </div>

      <div className="hubs">
        <div>
          <h3>Departure points near {originName}</h3>
          <HubList hubs={originHubs} />
        </div>
        <div>
          <h3>Arrival points near {destinationName}</h3>
          <HubList hubs={destinationHubs} />
        </div>
      </div>
    </section>
  )
}

function HubList({ hubs }: { hubs: RouteResponse['hubs'] }) {
  if (hubs.length === 0) {
    return <p className="muted">No stations found nearby (or the map service is unavailable).</p>
  }
  return (
    <ul className="list">
      {hubs.map((hub) => (
        <li key={`${hub.kind}-${hub.name}-${hub.lat}`}>
          <span>
            <strong>{hub.name}</strong> <span className="muted">{HUB_LABEL[hub.kind]}</span>
          </span>
          <span className="muted">{hub.distance_km} km</span>
        </li>
      ))}
    </ul>
  )
}
