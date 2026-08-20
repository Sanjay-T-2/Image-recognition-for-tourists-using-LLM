export function money(amount: number, currency: string): string {
  try {
    return new Intl.NumberFormat(undefined, {
      style: 'currency',
      currency,
      maximumFractionDigits: 0,
    }).format(amount)
  } catch {
    return `${currency} ${Math.round(amount)}`
  }
}

export function duration(hours: number): string {
  const whole = Math.floor(hours)
  const minutes = Math.round((hours - whole) * 60)
  if (whole >= 24) {
    const days = Math.floor(whole / 24)
    return `${days}d ${whole % 24}h`
  }
  return minutes ? `${whole}h ${minutes}m` : `${whole}h`
}

export function addDays(iso: string, days: number): string {
  const date = new Date(iso)
  date.setDate(date.getDate() + days)
  return date.toISOString().slice(0, 10)
}

export const MODE_ICON: Record<string, string> = {
  flight: '✈️',
  train: '🚆',
  bus: '🚌',
  car: '🚗',
  ferry: '⛴️',
}

export const HUB_LABEL: Record<string, string> = {
  airport: 'Airport',
  railway_station: 'Railway station',
  bus_station: 'Bus stand',
  ferry_terminal: 'Ferry terminal',
}
