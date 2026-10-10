import { useEffect, useState } from 'react'

import { getMeeting } from '../api.js'

const POLL_INTERVAL_MS = 2000
const FINISHED = ['ready', 'failed']

/** Fetch a meeting and keep polling until processing finishes. */
export function useMeeting(meetingId) {
  const [meeting, setMeeting] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    let timeout

    async function poll() {
      try {
        const latest = await getMeeting(meetingId)
        if (cancelled) return

        setMeeting(latest)

        if (!FINISHED.includes(latest.status)) {
          timeout = setTimeout(poll, POLL_INTERVAL_MS)
        }
      } catch (pollError) {
        if (!cancelled) setError(pollError.message)
      }
    }

    poll()

    return () => {
      cancelled = true
      clearTimeout(timeout)
    }
  }, [meetingId])

  return { meeting, error }
}
