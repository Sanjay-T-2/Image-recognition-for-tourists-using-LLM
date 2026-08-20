import { useCallback, useEffect, useState } from 'react'

import { BookingStep } from './components/BookingStep'
import { DestinationInput } from './components/DestinationInput'
import { InfoPanel } from './components/InfoPanel'
import { QuestionsStep } from './components/QuestionsStep'
import { StayStep } from './components/StayStep'
import { TransportStep } from './components/TransportStep'
import * as api from './lib/api'
import { isValidDate } from './lib/format'
import type {
  DestinationInfo,
  IdentifyResponse,
  Preference,
  RouteResponse,
  StayEstimateResponse,
  TransportOption,
} from './lib/types'

type Step = 'input' | 'questions' | 'plan' | 'booking'
type Style = 'budget' | 'standard' | 'premium'

const PRIORITY_TO_PREFERENCE: Record<string, Preference> = {
  'Lowest cost': 'low_cost',
  'Fastest route': 'fewer_days',
  'Most comfortable': 'high_comfort',
  'Scenic / more days on the way': 'more_days',
}

const TRAVELLER_COUNT: Record<string, number> = {
  Solo: 1,
  Couple: 2,
  'Family with kids': 4,
  'Friends group': 4,
}

function today(): string {
  return new Date().toISOString().slice(0, 10)
}

export default function App() {
  const [step, setStep] = useState<Step>('input')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const [identified, setIdentified] = useState<IdentifyResponse | null>(null)
  const [answers, setAnswers] = useState<Record<string, string>>({})

  const [preference, setPreference] = useState<Preference>('balanced')
  const [currency, setCurrency] = useState('INR')
  const [route, setRoute] = useState<RouteResponse | null>(null)
  const [routeLoading, setRouteLoading] = useState(false)
  const [selected, setSelected] = useState<TransportOption | null>(null)

  const [days, setDays] = useState(3)
  const [travellers, setTravellers] = useState(1)
  const [startDate, setStartDate] = useState(today())
  const [style, setStyle] = useState<Style>('standard')
  const [estimate, setEstimate] = useState<StayEstimateResponse | null>(null)
  const [estimateLoading, setEstimateLoading] = useState(false)

  const [info, setInfo] = useState<DestinationInfo | null>(null)

  async function handleIdentify(input: Parameters<typeof api.identify>[0]) {
    setBusy(true)
    setError(null)
    try {
      const result = await api.identify(input)
      if (!result.origin) {
        setError('Tell us where you are starting from so we can measure the distance.')
        return
      }
      setIdentified(result)
      setStep('questions')
      const detected = await api
        .currencyFor(result.destination.lat, result.destination.lon)
        .catch(() => null)
      if (detected?.currency) setCurrency(detected.currency)
      api.destinationInfo(result.destination).then(setInfo).catch(() => setInfo(null))
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Something went wrong')
    } finally {
      setBusy(false)
    }
  }

  const loadRoute = useCallback(
    async (nextPreference: Preference) => {
      if (!identified?.origin) return
      setRouteLoading(true)
      try {
        const result = await api.route({
          origin: { lat: identified.origin.lat, lon: identified.origin.lon },
          destination: {
            lat: identified.destination.lat,
            lon: identified.destination.lon,
          },
          origin_label: identified.origin.name,
          destination_label: identified.destination.name,
          preference: nextPreference,
          currency,
        })
        setRoute(result)
        setSelected(
          (current) =>
            result.options.find((option) => option.mode === current?.mode) ??
            result.options.find((option) => option.recommended) ??
            result.options[0] ??
            null,
        )
      } catch (caught) {
        setError(caught instanceof Error ? caught.message : 'Could not build the route')
      } finally {
        setRouteLoading(false)
      }
    },
    [identified, currency],
  )

  useEffect(() => {
    if (step === 'plan') void loadRoute(preference)
  }, [step, preference, loadRoute])

  useEffect(() => {
    if (step !== 'plan' || !identified) return
    const timer = setTimeout(async () => {
      setEstimateLoading(true)
      try {
        setEstimate(
          await api.stayEstimate({
            destination: {
              lat: identified.destination.lat,
              lon: identified.destination.lon,
            },
            destination_label: identified.destination.name,
            days,
            travellers,
            start_date: isValidDate(startDate) ? startDate : null,
            style,
            transport_cost: selected?.cost_min ?? 0,
            currency,
          }),
        )
      } catch {
        setEstimate(null)
      } finally {
        setEstimateLoading(false)
      }
    }, 250)
    return () => clearTimeout(timer)
  }, [step, identified, days, travellers, startDate, style, selected, currency])

  function startPlanning() {
    const priority = answers.priority
    if (priority && PRIORITY_TO_PREFERENCE[priority]) {
      setPreference(PRIORITY_TO_PREFERENCE[priority])
    }
    if (answers.travellers) setTravellers(TRAVELLER_COUNT[answers.travellers] ?? 1)
    if (answers.style) setStyle(answers.style.toLowerCase() as Style)
    setStep('plan')
  }

  return (
    <main className="app">
      <header className="topbar">
        <span className="logo">🧭 AI Tourist Guide</span>
        {identified && (
          <button
            type="button"
            className="ghost"
            onClick={() => {
              setStep('input')
              setIdentified(null)
              setRoute(null)
              setEstimate(null)
              setInfo(null)
              setSelected(null)
              setAnswers({})
            }}
          >
            New trip
          </button>
        )}
      </header>

      {error && <div className="error">{error}</div>}

      {step === 'input' && <DestinationInput loading={busy} onSubmit={handleIdentify} />}

      {step === 'questions' && identified && (
        <>
          <section className="card">
            <h2>{identified.destination.display_name}</h2>
            <p className="muted">
              Identified from {identified.source === 'image' ? 'your photo' : 'your text'} ·
              confidence {Math.round(identified.confidence * 100)}%
            </p>
            <p>{identified.summary}</p>
          </section>
          <QuestionsStep
            questions={identified.questions}
            answers={answers}
            onAnswer={(id, value) => setAnswers((current) => ({ ...current, [id]: value }))}
            onContinue={startPlanning}
          />
        </>
      )}

      {step === 'plan' && identified && (
        <>
          {route && (
            <TransportStep
              route={route}
              originName={identified.origin?.name ?? 'Your location'}
              destinationName={identified.destination.name}
              preference={preference}
              selected={selected}
              loading={routeLoading}
              onPreference={setPreference}
              onSelect={setSelected}
            />
          )}
          {!route && routeLoading && <section className="card">Building your options…</section>}
          <StayStep
            days={days}
            travellers={travellers}
            startDate={startDate}
            style={style}
            estimate={estimate}
            selectedTransport={selected}
            loading={estimateLoading}
            onChange={(patch) => {
              if (patch.days !== undefined) setDays(patch.days)
              if (patch.travellers !== undefined) setTravellers(patch.travellers)
              if (patch.startDate !== undefined) setStartDate(patch.startDate)
              if (patch.style !== undefined) setStyle(patch.style)
            }}
            onBook={() => setStep('booking')}
          />
          {info && <InfoPanel info={info} />}
        </>
      )}

      {step === 'booking' && selected && identified && (
        <>
          <BookingStep
            option={selected}
            originName={identified.origin?.name ?? 'Your location'}
            destinationName={identified.destination.name}
            startDate={isValidDate(startDate) ? startDate : ''}
            travellers={travellers}
            onBack={() => setStep('plan')}
          />
          {info && <InfoPanel info={info} />}
        </>
      )}
    </main>
  )
}
