import { useEffect, useRef } from 'react'

import { useMeeting, usePrefersReducedMotion } from '../hooks'
import { AlertIcon, CheckIcon } from './Icons.jsx'
import MeetingChat from './MeetingChat.jsx'
import MeetingReport from './MeetingReport.jsx'

const STEPS = [
  { status: 'downloading', label: 'Downloading audio', linkOnly: true },
  { status: 'preparing', label: 'Preparing audio' },
  { status: 'transcribing', label: 'Transcribing speech' },
  { status: 'analyzing', label: 'Extracting insights' },
  { status: 'indexing', label: 'Building meeting chat' },
]

function ProgressSteps({ meeting }) {
  const steps = STEPS.filter((step) => !step.linkOnly || meeting.source === 'link')
  const activeIndex = steps.findIndex((step) => step.status === meeting.status)

  return (
    <div className="card progress">
      <div className="progress-orb" aria-hidden="true" />
      <h3>Working on your meeting</h3>
      <p className="progress-detail" aria-live="polite">{meeting.detail}</p>

      <ol className="progress-steps">
        {steps.map((step, index) => {
          const state = index < activeIndex ? 'done' : index === activeIndex ? 'active' : 'pending'

          return (
            <li className={`progress-step is-${state}`} key={step.status}>
              <span className="progress-marker">
                {state === 'done' ? <CheckIcon size={14} /> : index + 1}
              </span>
              {step.label}
            </li>
          )
        })}
      </ol>

      <p className="progress-note">
        Whisper runs on your machine, so long meetings can take several minutes. You can keep
        this tab open, or come back to this link later.
      </p>
    </div>
  )
}

function ErrorState({ message, details, onReset }) {
  return (
    <div className="card error-state" role="alert">
      <span className="icon-badge icon-badge-error">
        <AlertIcon size={22} />
      </span>
      <h3>{message}</h3>
      {details && <p className="error-details">{details}</p>}
      <button className="button button-ghost" type="button" onClick={onReset}>
        Try another meeting
      </button>
    </div>
  )
}

export default function Workspace({ meetingId, onReset }) {
  const { meeting, error } = useMeeting(meetingId)
  const reducedMotion = usePrefersReducedMotion()
  const sectionRef = useRef(null)

  useEffect(() => {
    sectionRef.current.scrollIntoView({ behavior: reducedMotion ? 'auto' : 'smooth' })
  }, [meetingId, reducedMotion])

  let content

  if (error) {
    content = <ErrorState message="We couldn't load this meeting." details={error} onReset={onReset} />
  } else if (!meeting) {
    content = <div className="card progress progress-loading">Loading meeting...</div>
  } else if (meeting.status === 'failed') {
    content = (
      <ErrorState
        message="This meeting couldn't be processed."
        details={meeting.error}
        onReset={onReset}
      />
    )
  } else if (meeting.status === 'ready') {
    content = (
      <div className="workspace-grid">
        <MeetingReport title={meeting.title} result={meeting.result} transcript={meeting.transcript} />
        <MeetingChat meetingId={meeting.id} />
      </div>
    )
  } else {
    content = <ProgressSteps meeting={meeting} />
  }

  return (
    <section className="section workspace" id="workspace" ref={sectionRef}>
      <div className="container">
        <div className="workspace-header">
          <div>
            <p className="eyebrow">Your meeting</p>
            <h2>{meeting?.title ?? 'Loading...'}</h2>
          </div>
          <button className="button button-ghost button-small" type="button" onClick={onReset}>
            Analyze another
          </button>
        </div>

        {content}
      </div>
    </section>
  )
}
