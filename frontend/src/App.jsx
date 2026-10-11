import { lazy, Suspense, useState } from 'react'

import {
  Features,
  Footer,
  GetStarted,
  Hero,
  Navbar,
  Pipeline,
  Principles,
  TechStack,
} from './Components'
import './App.css'

// Loaded only once a meeting exists; it carries the report, chat and Markdown renderer.
const Workspace = lazy(() => import('./Components/Workspace.jsx'))

// The meeting ID lives in the URL so a refresh (or a shared link) reopens it.
function readMeetingId() {
  return new URLSearchParams(window.location.search).get('meeting')
}

function writeMeetingId(meetingId) {
  const url = new URL(window.location.href)

  if (meetingId) url.searchParams.set('meeting', meetingId)
  else url.searchParams.delete('meeting')

  window.history.replaceState(null, '', url)
}

export default function App() {
  const [meetingId, setMeetingId] = useState(readMeetingId)

  const openMeeting = (meeting) => {
    writeMeetingId(meeting.id)
    setMeetingId(meeting.id)
  }

  const resetMeeting = () => {
    writeMeetingId(null)
    setMeetingId(null)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <>
      <Navbar />
      <main>
        <Hero onMeetingCreated={openMeeting} />
        {meetingId && (
          <Suspense fallback={null}>
            <Workspace key={meetingId} meetingId={meetingId} onReset={resetMeeting} />
          </Suspense>
        )}
        <TechStack />
        <Features />
        <Pipeline />
        <Principles />
        <GetStarted />
      </main>
      <Footer />
    </>
  )
}
