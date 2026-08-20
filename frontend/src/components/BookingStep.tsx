import { MODE_ICON, duration, money } from '../lib/format'
import type { TransportOption } from '../lib/types'

interface Props {
  option: TransportOption
  originName: string
  destinationName: string
  startDate: string
  travellers: number
  onBack: () => void
}

export function BookingStep({
  option,
  originName,
  destinationName,
  startDate,
  travellers,
  onBack,
}: Props) {
  return (
    <section className="card">
      <h2>
        {MODE_ICON[option.mode]} Book your {option.label.toLowerCase()}
      </h2>
      <p className="muted">
        {originName} → {destinationName} · {startDate || 'date not set'} · {travellers} traveller(s)
        · {duration(option.duration_hours)} · {money(option.cost_min, option.currency)}–
        {money(option.cost_max, option.currency)} per person
      </p>
      <div className="providers">
        {option.booking.map((link) => (
          <a
            key={link.provider}
            className="provider"
            href={link.url}
            target="_blank"
            rel="noreferrer noopener"
          >
            {link.provider}
            <span className="muted">Search live availability →</span>
          </a>
        ))}
      </div>
      <p className="muted small">
        Fares shown in this app are estimates. Final prices and seat availability come from the
        booking provider.
      </p>
      <button type="button" className="ghost" onClick={onBack}>
        Back to the plan
      </button>
    </section>
  )
}
