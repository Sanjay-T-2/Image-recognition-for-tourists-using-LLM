import { addDays, isValidDate, money } from '../lib/format'
import type { StayEstimateResponse, TransportOption } from '../lib/types'

interface Props {
  days: number
  travellers: number
  startDate: string
  style: 'budget' | 'standard' | 'premium'
  estimate: StayEstimateResponse | null
  selectedTransport: TransportOption | null
  loading: boolean
  onChange: (patch: {
    days?: number
    travellers?: number
    startDate?: string
    style?: 'budget' | 'standard' | 'premium'
  }) => void
  onBook: () => void
}

export function StayStep({
  days,
  travellers,
  startDate,
  style,
  estimate,
  selectedTransport,
  loading,
  onChange,
  onBook,
}: Props) {
  const dateValid = isValidDate(startDate)
  return (
    <section className="card">
      <h2>How long are you staying?</h2>
      <div className="row wrap">
        <div className="field">
          <label htmlFor="days">Days at the destination</label>
          <input
            id="days"
            type="number"
            min={1}
            max={60}
            value={days}
            onChange={(event) => onChange({ days: Number(event.target.value) })}
          />
        </div>
        <div className="field">
          <label htmlFor="travellers">Travellers</label>
          <input
            id="travellers"
            type="number"
            min={1}
            max={20}
            value={travellers}
            onChange={(event) => onChange({ travellers: Number(event.target.value) })}
          />
        </div>
        <div className="field">
          <label htmlFor="start">Start date</label>
          <input
            id="start"
            type="date"
            min="1900-01-01"
            max="2100-12-31"
            value={startDate}
            onChange={(event) => onChange({ startDate: event.target.value })}
          />
        </div>
        <div className="field">
          <label htmlFor="style">Spending style</label>
          <select
            id="style"
            value={style}
            onChange={(event) =>
              onChange({ style: event.target.value as 'budget' | 'standard' | 'premium' })
            }
          >
            <option value="budget">Budget</option>
            <option value="standard">Standard</option>
            <option value="premium">Premium</option>
          </select>
        </div>
      </div>
      {dateValid && (
        <p className="muted">
          Trip window: {startDate} → {addDays(startDate, days - 1)}
        </p>
      )}
      {startDate && !dateValid && (
        <p className="warning">
          Enter a start date between 1900 and 2100 — the costs below ignore the date until then.
        </p>
      )}

      {loading && <p className="muted">Estimating costs…</p>}

      {estimate && (
        <>
          <div className="stats">
            <div>
              <span className="stat">{money(estimate.minimum_total, estimate.currency)}</span>
              <span className="muted">approximate minimum for the whole trip</span>
            </div>
            <div>
              <span className="stat">{money(estimate.per_day_minimum, estimate.currency)}</span>
              <span className="muted">per day</span>
            </div>
            <div>
              <span className="stat">
                {money(estimate.comfortable_total, estimate.currency)}
              </span>
              <span className="muted">comfortable budget</span>
            </div>
          </div>
          <ul className="list">
            {estimate.breakdown.map((line) => (
              <li key={line.label}>
                <span>
                  <strong>{line.label}</strong>
                  <br />
                  <span className="muted">{line.detail}</span>
                </span>
                <span>{money(line.amount, estimate.currency)}</span>
              </li>
            ))}
          </ul>
          <ul className="tips">
            {estimate.tips.map((tip) => (
              <li key={tip}>{tip}</li>
            ))}
          </ul>
        </>
      )}

      <button className="primary" disabled={!selectedTransport} onClick={onBook}>
        {selectedTransport
          ? `Continue to ${selectedTransport.label.toLowerCase()} booking`
          : 'Pick a transport mode first'}
      </button>
    </section>
  )
}
