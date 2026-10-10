import { useState } from 'react'

import {
  Features,
  Footer,
  GetStarted,
  Hero,
  Navbar,
  Pipeline,
  Principles,
  TechStack,
  Workspace,
} from './Components'
import './App.css'

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
        {meetingId && <Workspace key={meetingId} meetingId={meetingId} onReset={resetMeeting} />}
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
