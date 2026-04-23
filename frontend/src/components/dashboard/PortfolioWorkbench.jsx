import { useMemo, useState } from 'react'
import BridgeDetailCard from '../portfolio/BridgeDetailCard'
import BridgeRankingList from '../portfolio/BridgeRankingList'
import BridgeTable from '../portfolio/BridgeTable'
import PortfolioMap from '../portfolio/PortfolioMap'

function SummaryChip({ label, value, hint }) {
  return (
    <div className="rounded-[24px] border border-slate-200/90 bg-[linear-gradient(180deg,rgba(255,255,255,0.98)_0%,rgba(248,251,255,0.98)_100%)] px-4 py-4 shadow-sm">
      <p className="text-[11px] uppercase tracking-[0.24em] text-slate-600">{label}</p>
      <p className="mt-2 text-2xl font-semibold tracking-[-0.04em] text-slate-900">{value}</p>
      {hint ? <p className="mt-2 text-sm leading-6 text-slate-700">{hint}</p> : null}
    </div>
  )
}

export default function PortfolioWorkbench({ bridges, onLoadBridge }) {
  const normalizedBridges = useMemo(() => {
    if (Array.isArray(bridges)) {
      return bridges
    }
    return bridges?.bridges ?? []
  }, [bridges])

  const [query, setQuery] = useState('')
  const [county, setCounty] = useState('all')
  const [bridgeClass, setBridgeClass] = useState('all')
  const [riskBand, setRiskBand] = useState('all')
  const [rankingMetric, setRankingMetric] = useState('prototypeVulnerability')
  const [selectedBridgeId, setSelectedBridgeId] = useState(null)

  const countyOptions = useMemo(
    () => [...new Set(normalizedBridges.map((bridge) => bridge.countyLabel))].slice(0, 80),
    [normalizedBridges],
  )
  const classOptions = useMemo(
    () => [...new Set(normalizedBridges.map((bridge) => bridge.bridgeClass))],
    [normalizedBridges],
  )

  const filtered = useMemo(() => {
    return normalizedBridges.filter((bridge) => {
      const matchesQuery = !query || bridge.searchableText.includes(query.toLowerCase())
      const matchesCounty = county === 'all' || bridge.countyLabel === county
      const matchesClass = bridgeClass === 'all' || bridge.bridgeClass === bridgeClass
      const matchesRisk = riskBand === 'all' || bridge.riskBand === riskBand
      return matchesQuery && matchesCounty && matchesClass && matchesRisk
    })
  }, [normalizedBridges, query, county, bridgeClass, riskBand])

  const selectedBridge = useMemo(() => {
    if (!filtered.length) {
      return null
    }
    return filtered.find((bridge) => bridge.structureNumber === selectedBridgeId) ?? filtered[0]
  }, [filtered, selectedBridgeId])

  const summary = useMemo(() => {
    if (!filtered.length) {
      return { meanScore: 0, meanPriority: 0, highRisk: 0 }
    }
    const count = filtered.length
    const meanScore = filtered.reduce((sum, bridge) => sum + Number(bridge.prototypeVulnerability || 0), 0) / count
    const highRisk = filtered.filter((bridge) => ['High', 'Critical'].includes(bridge.riskBand)).length
    return { meanScore, highRisk }
  }, [filtered])

  const handleSelect = (bridge) => {
    setSelectedBridgeId(bridge.structureNumber)
    onLoadBridge?.(bridge)
  }

  return (
    <div className="space-y-5">
      <div className="rounded-[32px] border border-slate-200/90 bg-[linear-gradient(180deg,rgba(255,255,255,0.98)_0%,rgba(244,248,254,0.98)_100%)] p-6 shadow-[0_28px_70px_rgba(15,23,42,0.09)]">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="paper-eyebrow">Portfolio explorer</p>
            <h3 className="mt-2 text-2xl font-semibold tracking-[-0.04em] text-slate-900">Search, filter, rank, and inspect individual bridges</h3>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-700">
              This layer uses real bridge rows exported from the repo. The map, ranking, and table are data-backed; the intrinsic score itself is a transparent frontend prototype until the final backend model is connected.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            <SummaryChip label="Filtered bridges" value={filtered.length.toLocaleString()} hint="Current portfolio slice" />
            <SummaryChip label="Mean score" value={summary.meanScore.toFixed(3)} hint="Prototype intrinsic vulnerability" />
            <SummaryChip label="High / critical" value={summary.highRisk.toLocaleString()} hint="Portfolio bridges needing attention" />
          </div>
        </div>

        <div className="mt-6 grid gap-4 xl:grid-cols-[1.3fr_0.9fr_0.9fr_0.9fr]">
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            className="field-input"
            placeholder="Search by bridge number, class, or county"
          />
          <select value={county} onChange={(event) => setCounty(event.target.value)} className="field-input">
            <option value="all">All counties</option>
            {countyOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
          <select value={bridgeClass} onChange={(event) => setBridgeClass(event.target.value)} className="field-input">
            <option value="all">All bridge classes</option>
            {classOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
          <select value={riskBand} onChange={(event) => setRiskBand(event.target.value)} className="field-input">
            <option value="all">All risk bands</option>
            {['Low', 'Guarded', 'Elevated', 'High', 'Critical'].map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.15fr_0.85fr]">
        <PortfolioMap bridges={filtered} selectedBridge={selectedBridge} onSelect={handleSelect} />
        <BridgeRankingList
          bridges={filtered}
          metric={rankingMetric}
          onMetricChange={setRankingMetric}
          selectedBridge={selectedBridge}
          onSelect={handleSelect}
        />
      </div>

      <BridgeDetailCard bridge={selectedBridge} onLoadBridge={onLoadBridge} />
      <BridgeTable bridges={filtered} selectedBridge={selectedBridge} onSelect={handleSelect} />
    </div>
  )
}
