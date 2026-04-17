import { useMemo, useState } from 'react'
import BridgeDetailCard from '../portfolio/BridgeDetailCard'
import BridgeRankingList from '../portfolio/BridgeRankingList'
import BridgeTable from '../portfolio/BridgeTable'
import PortfolioMap from '../portfolio/PortfolioMap'

function SummaryChip({ label, value, hint }) {
  return (
    <div className="rounded-[24px] border border-slate-200/80 bg-white/90 px-4 py-4 shadow-sm">
      <p className="text-[11px] uppercase tracking-[0.24em] text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-semibold tracking-[-0.04em] text-slate-950">{value}</p>
      {hint ? <p className="mt-2 text-sm leading-6 text-slate-500">{hint}</p> : null}
    </div>
  )
}

export default function PortfolioWorkbench({ bridges, onLoadBridge }) {
  const [query, setQuery] = useState('')
  const [county, setCounty] = useState('all')
  const [bridgeClass, setBridgeClass] = useState('all')
  const [riskBand, setRiskBand] = useState('all')
  const [rankingMetric, setRankingMetric] = useState('prototypeVulnerability')
  const [selectedBridgeId, setSelectedBridgeId] = useState(bridges[0]?.structureNumber ?? null)

  const countyOptions = useMemo(
    () => [...new Set(bridges.map((bridge) => bridge.countyLabel))].slice(0, 80),
    [bridges],
  )
  const classOptions = useMemo(
    () => [...new Set(bridges.map((bridge) => bridge.bridgeClass))],
    [bridges],
  )

  const filtered = useMemo(() => {
    return bridges.filter((bridge) => {
      const matchesQuery = !query || bridge.searchableText.includes(query.toLowerCase())
      const matchesCounty = county === 'all' || bridge.countyLabel === county
      const matchesClass = bridgeClass === 'all' || bridge.bridgeClass === bridgeClass
      const matchesRisk = riskBand === 'all' || bridge.riskBand === riskBand
      return matchesQuery && matchesCounty && matchesClass && matchesRisk
    })
  }, [bridges, query, county, bridgeClass, riskBand])

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
      <div className="rounded-[32px] border border-slate-200/70 bg-[linear-gradient(180deg,rgba(255,255,255,0.96)_0%,rgba(243,247,252,0.96)_100%)] p-6 shadow-[0_28px_70px_rgba(15,23,42,0.08)]">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-slate-500">Portfolio explorer</p>
            <h3 className="mt-2 text-2xl font-semibold tracking-[-0.04em] text-slate-950">Search, filter, rank, and inspect individual bridges</h3>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
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
