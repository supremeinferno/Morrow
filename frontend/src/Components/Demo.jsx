import { useEffect, useRef, useState } from 'react'

import { usePrefersReducedMotion, useReveal } from '../hooks'
import { ActionIcon, DecisionIcon, QuestionIcon, SummaryIcon } from './Icons.jsx'
import SectionHeading from './SectionHeading.jsx'

const REPORT = [
  {
    icon: SummaryIcon,
    title: 'Summary',
    items: ['The team reviewed the upcoming product release, set the backend timeline and chose a production database.'],
  },
  {
    icon: DecisionIcon,
    title: 'Decisions',
    items: ['Use PostgreSQL for the production database.'],
  },
  {
    icon: ActionIcon,
    title: 'Action items',
    items: [
      { text: 'Complete the authentication API', meta: 'Pranav · Friday' },
      { text: 'Begin frontend work once the auth API is done', meta: 'Owner not stated' },
    ],
  },
  {
    icon: QuestionIcon,
    title: 'Open questions',
    items: ['Should the first release include email notifications?'],
  },
]

const QUESTIONS = [
  {
    question: 'When can the frontend work start?',
    answer: 'After the authentication API is completed, which Pranav is expected to finish by Friday.',
  },
  {
    question: 'Which database are we using?',
    answer: 'The team decided to use PostgreSQL for the production database.',
  },
  {
    question: 'Are email notifications in v1?',
    answer: "That's still undecided. It was raised as an open question in the meeting.",
  },
  {
    question: 'How much budget was allocated?',
    answer: "I couldn't find that information in the meeting.",
  },
]

const THINKING_MS = 650
const TYPING_MS = 18

function MeetingReport() {
  return (
    <div className="card report">
      <div className="report-header">
        <div>
          <p className="report-label">Meeting report</p>
          <h3>Product release sync</h3>
        </div>
        <span className="status-pill">Analyzed</span>
      </div>

      {REPORT.map(({ icon: SectionIcon, title, items }) => (
        <div className="report-section" key={title}>
          <h4>
            <SectionIcon size={16} />
            {title}
          </h4>
          <ul>
            {items.map((item) => {
              const { text, meta } = typeof item === 'string' ? { text: item } : item
              return (
                <li key={text}>
                  {text}
                  {meta && <span className="report-meta">{meta}</span>}
                </li>
              )
            })}
          </ul>
        </div>
      ))}
    </div>
  )
}

function AskMeeting() {
  const reducedMotion = usePrefersReducedMotion()
  const [messages, setMessages] = useState([
    { role: 'user', text: QUESTIONS[0].question },
    { role: 'morrow', text: QUESTIONS[0].answer },
  ])
  const [pendingAnswer, setPendingAnswer] = useState(null)
  const [typedAnswer, setTypedAnswer] = useState(null)
  const threadRef = useRef(null)

  // Show a short "thinking" pause, then type the answer out.
  useEffect(() => {
    if (!pendingAnswer) return

    let interval
    const finish = () => {
      setMessages((current) => [...current, { role: 'morrow', text: pendingAnswer }])
      setPendingAnswer(null)
      setTypedAnswer(null)
    }

    const timeout = setTimeout(() => {
      if (reducedMotion) {
        finish()
        return
      }

      let length = 0
      interval = setInterval(() => {
        length += 2
        setTypedAnswer(pendingAnswer.slice(0, length))
        if (length >= pendingAnswer.length) {
          clearInterval(interval)
          finish()
        }
      }, TYPING_MS)
    }, THINKING_MS)

    return () => {
      clearTimeout(timeout)
      clearInterval(interval)
    }
  }, [pendingAnswer, reducedMotion])

  useEffect(() => {
    const thread = threadRef.current
    thread.scrollTo({ top: thread.scrollHeight, behavior: reducedMotion ? 'auto' : 'smooth' })
  }, [messages, typedAnswer, pendingAnswer, reducedMotion])

  const ask = ({ question, answer }) => {
    if (pendingAnswer) return
    setMessages((current) => [...current, { role: 'user', text: question }])
    setPendingAnswer(answer)
  }

  return (
    <div className="card chat">
      <div className="chat-header">
        <span className="chat-avatar" aria-hidden="true" />
        <div>
          <p className="chat-title">Ask Morrow</p>
          <p className="chat-subtitle">Answers come only from this meeting</p>
        </div>
      </div>

      <div className="chat-thread" ref={threadRef} aria-live="polite">
        {messages.map((message, index) => (
          <p className={`bubble bubble-${message.role}`} key={index}>
            {message.text}
          </p>
        ))}

        {pendingAnswer && (
          <p className="bubble bubble-morrow">
            {typedAnswer ?? (
              <span className="thinking" aria-label="Morrow is thinking">
                <span />
                <span />
                <span />
              </span>
            )}
          </p>
        )}
      </div>

      <div className="chat-suggestions">
        <p>Try asking</p>
        <div className="chip-row">
          {QUESTIONS.map((item) => (
            <button
              className="chip"
              type="button"
              key={item.question}
              onClick={() => ask(item)}
              disabled={Boolean(pendingAnswer)}
            >
              {item.question}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

export default function Demo() {
  const revealRef = useReveal()

  return (
    <section className="section" id="demo">
      <div className="container reveal" ref={revealRef}>
        <SectionHeading eyebrow="See it in action" title="One meeting. Everything that matters.">
          Here's what Morrow produces for a short sample meeting, plus a conversation you can
          try yourself.
        </SectionHeading>

        <div className="demo-grid">
          <MeetingReport />
          <AskMeeting />
        </div>
      </div>
    </section>
  )
}
