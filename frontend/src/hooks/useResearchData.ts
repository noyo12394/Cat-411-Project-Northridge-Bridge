import { useEffect, useState } from 'react'
import { loadResearchData } from '../lib/researchData'
import type { ResearchData } from '../types/research'

interface ResearchState {
  loading: boolean
  error: Error | null
  data: ResearchData | null
}

export function useResearchData() {
  const [state, setState] = useState<ResearchState>({
    loading: true,
    error: null,
    data: null,
  })

  useEffect(() => {
    let mounted = true

    loadResearchData()
      .then((data) => {
        if (!mounted) {
          return
        }
        setState({ loading: false, error: null, data })
      })
      .catch((error: Error) => {
        if (!mounted) {
          return
        }
        setState({ loading: false, error, data: null })
      })

    return () => {
      mounted = false
    }
  }, [])

  return state
}
