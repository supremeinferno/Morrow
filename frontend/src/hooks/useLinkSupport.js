import { useEffect, useState } from 'react'

import { getHealth } from '../api.js'

/**
 * Whether the backend can download video links. Starts as false so the
 * upload form shows immediately, and turns true once the server confirms.
 */
export function useLinkSupport() {
  const [linksEnabled, setLinksEnabled] = useState(false)

  useEffect(() => {
    let cancelled = false

    getHealth()
      .then((health) => {
        if (!cancelled) setLinksEnabled(Boolean(health.links))
      })
      .catch(() => {
        // Server unreachable: keep links hidden; uploads will show their own error.
      })

    return () => {
      cancelled = true
    }
  }, [])

  return linksEnabled
}
