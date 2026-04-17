import { useEffect, useMemo, useState } from 'react'
import { loadBridgePortfolio, loadResearchData } from '../lib/dataAdapter.js'
import { fallbackResearchData } from '../data/fallbackResearchData.js'

export function useResearchData() {
  const [state, setState] = useState({
    loading: true,
    portfolioLoading: false,
    error: null,
    data: fallbackResearchData,
  })

  useEffect(() => {
    let isMounted = true

    loadResearchData()
      .then((data) => {
        if (!isMounted) return
        setState({ loading: false, portfolioLoading: false, error: null, data })
      })
      .catch((error) => {
        if (!isMounted) return
        setState({ loading: false, portfolioLoading: false, error, data: fallbackResearchData })
      })

    return () => {
      isMounted = false
    }
  }, [])

  const ensurePortfolioLoaded = async () => {
    if (state.portfolioLoading || state.data.availability?.portfolioLoaded) {
      return
    }

    setState((current) => ({ ...current, portfolioLoading: true }))

    try {
      const portfolio = await loadBridgePortfolio()
      setState((current) => ({
        ...current,
        portfolioLoading: false,
        data: {
          ...current.data,
          availability: {
            ...current.data.availability,
            portfolioLoaded: true,
          },
          portfolio,
        },
      }))
    } catch {
      setState((current) => ({ ...current, portfolioLoading: false }))
    }
  }

  const diagnostics = useMemo(() => {
    if (state.error) {
      return 'Fell back to bundled demo data because the exported repo snapshots could not be loaded.'
    }
    if (state.data.availability.repoData) {
      return 'Using repo-derived JSON snapshots and figure assets exported from the Python workflow.'
    }
    return 'Using bundled fallback data to preserve the demo experience.'
  }, [state.data.availability.repoData, state.error])

  return { ...state, diagnostics, ensurePortfolioLoaded }
}
