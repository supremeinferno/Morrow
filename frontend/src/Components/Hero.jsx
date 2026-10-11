import { lazy, Suspense, useRef } from 'react'

import { useLinkSupport } from '../hooks'
import MeetingInput from './MeetingInput.jsx'

// Loaded separately so the headline renders before three.js arrives.
const HeroScene = lazy(() => import('./three/HeroScene.jsx'))

export default function Hero({ onMeetingCreated }) {
  const heroRef = useRef(null)
  const linksEnabled = useLinkSupport()

  return (
    <section className="hero" id="top" ref={heroRef}>
      <div className="hero-glow" aria-hidden="true" />

      <div className="hero-canvas" aria-hidden="true">
        <Suspense fallback={null}>
          <HeroScene eventSource={heroRef} />
        </Suspense>
      </div>

      <div className="hero-content container">
        <p className="eyebrow">
          <span className="eyebrow-dot" />
          AI meeting assistant
        </p>

        <h1 className="hero-title">
          Turn conversations into <em>what comes next.</em>
        </h1>

        <p className="hero-lede">
          {linksEnabled ? 'Paste a meeting link or upload a recording.' : 'Upload a meeting recording.'}{' '}
          Morrow gives you back the summary, the
          decisions, the action items and the open questions, then lets you chat with the meeting.
        </p>

        <MeetingInput onCreated={onMeetingCreated} allowLinks={linksEnabled} />
      </div>

      <a className="scroll-cue" href="#features" aria-label="Scroll to features">
        <span />
      </a>
    </section>
  )
}
