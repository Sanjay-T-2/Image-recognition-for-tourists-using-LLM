import { useState } from 'react'

import type { DestinationInfo } from '../lib/types'

const TABS = ['History', 'Best places', 'Hotels', 'Emergency'] as const
type Tab = (typeof TABS)[number]

export function InfoPanel({ info }: { info: DestinationInfo }) {
  const [tab, setTab] = useState<Tab>('History')

  return (
    <section className="card">
      <h2>About {info.place.name}</h2>
      <div className="chips">
        {TABS.map((item) => (
          <button
            key={item}
            type="button"
            className={tab === item ? 'chip selected' : 'chip'}
            onClick={() => setTab(item)}
          >
            {item}
          </button>
        ))}
      </div>

      {tab === 'History' && (
        <div>
          <p>{info.history}</p>
          {info.history_url && (
            <a href={info.history_url} target="_blank" rel="noreferrer noopener">
              Read more
            </a>
          )}
        </div>
      )}

      {tab === 'Best places' && (
        <ul className="list">
          {info.attractions.length === 0 && <li className="muted">No attractions found nearby.</li>}
          {info.attractions.map((attraction) => (
            <li key={`${attraction.name}-${attraction.lat}`}>
              <span>
                <strong>{attraction.name}</strong> <span className="muted">{attraction.kind}</span>
              </span>
              <span className="muted">{attraction.distance_km} km</span>
            </li>
          ))}
        </ul>
      )}

      {tab === 'Hotels' && (
        <ul className="list">
          {info.hotels.length === 0 && <li className="muted">No stays found nearby.</li>}
          {info.hotels.map((hotel) => (
            <li key={`${hotel.name}-${hotel.lat}`}>
              <span>
                <strong>{hotel.name}</strong>{' '}
                <span className="muted">
                  {hotel.price_band}
                  {hotel.stars ? ` · ${hotel.stars}★` : ''} · {hotel.distance_km} km
                </span>
              </span>
              <a href={hotel.booking_url} target="_blank" rel="noreferrer noopener">
                Book
              </a>
            </li>
          ))}
        </ul>
      )}

      {tab === 'Emergency' && (
        <div>
          <div className="emergency">
            {Object.entries(info.emergency_numbers).map(([label, number]) => (
              <a key={label} className="emergency-number" href={`tel:${number}`}>
                <span>{label}</span>
                <strong>{number}</strong>
              </a>
            ))}
          </div>
          <h3>Nearby hospitals</h3>
          <ul className="list">
            {info.hospitals.length === 0 && <li className="muted">No hospitals found nearby.</li>}
            {info.hospitals.map((hospital) => (
              <li key={`${hospital.name}-${hospital.lat}`}>
                <span>
                  <strong>{hospital.name}</strong>{' '}
                  <span className="muted">
                    {hospital.distance_km} km{hospital.emergency ? ' · emergency care' : ''}
                  </span>
                </span>
                {hospital.phone ? (
                  <a href={`tel:${hospital.phone}`}>{hospital.phone}</a>
                ) : (
                  <a
                    href={`https://www.google.com/maps/search/?api=1&query=${hospital.lat},${hospital.lon}`}
                    target="_blank"
                    rel="noreferrer noopener"
                  >
                    Map
                  </a>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  )
}
