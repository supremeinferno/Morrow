import { useEffect, useRef, useState } from 'react'
import Markdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

import { askQuestion } from '../api.js'
import { usePrefersReducedMotion } from '../hooks'
import { SendIcon } from './Icons.jsx'

// Answers are Markdown (bold, lists, tables). Raw HTML is never rendered.
const MARKDOWN_COMPONENTS = {
  a: ({ href, children }) => (
    <a href={href} target="_blank" rel="noreferrer">
      {children}
    </a>
  ),
}

const SUGGESTIONS = [
  'What were the main decisions?',
  'Who is responsible for what?',
  'What are the deadlines?',
  'What is still unresolved?',
]

/** RAG chat: every answer is retrieved from this meeting's transcript. */
export default function MeetingChat({ meetingId }) {
  const reducedMotion = usePrefersReducedMotion()
  const [messages, setMessages] = useState([])
  const [draft, setDraft] = useState('')
  const [isThinking, setIsThinking] = useState(false)
  const threadRef = useRef(null)

  useEffect(() => {
    const thread = threadRef.current
    thread.scrollTo({ top: thread.scrollHeight, behavior: reducedMotion ? 'auto' : 'smooth' })
  }, [messages, isThinking, reducedMotion])

  const ask = async (question) => {
    question = question.trim()
    if (!question || isThinking) return

    setDraft('')
    setMessages((current) => [...current, { role: 'user', text: question }])
    setIsThinking(true)

    try {
      const { answer } = await askQuestion(meetingId, question)
      setMessages((current) => [...current, { role: 'morrow', text: answer }])
    } catch (error) {
      setMessages((current) => [...current, { role: 'error', text: error.message }])
    } finally {
      setIsThinking(false)
    }
  }

  const onSubmit = (event) => {
    event.preventDefault()
    ask(draft)
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
        {messages.length === 0 && (
          <div className="chat-empty">
            <p>Ask anything about this meeting.</p>
            <div className="chip-row">
              {SUGGESTIONS.map((suggestion) => (
                <button className="chip" type="button" key={suggestion} onClick={() => ask(suggestion)}>
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message, index) => (
          <div className={`bubble bubble-${message.role}`} key={index}>
            {message.role === 'morrow' ? (
              <Markdown remarkPlugins={[remarkGfm]} components={MARKDOWN_COMPONENTS}>
                {message.text}
              </Markdown>
            ) : (
              message.text
            )}
          </div>
        ))}

        {isThinking && (
          <div className="bubble bubble-morrow">
            <span className="thinking" aria-label="Morrow is thinking">
              <span />
              <span />
              <span />
            </span>
          </div>
        )}
      </div>

      <form className="chat-form" onSubmit={onSubmit}>
        <input
          className="text-input"
          type="text"
          placeholder="Ask a question about the meeting..."
          aria-label="Your question"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
        />
        <button
          className="send-button"
          type="submit"
          aria-label="Send question"
          disabled={!draft.trim() || isThinking}
        >
          <SendIcon size={18} />
        </button>
      </form>
    </div>
  )
}
