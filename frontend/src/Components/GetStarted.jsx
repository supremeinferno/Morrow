import { useEffect, useState } from 'react'

import { GITHUB_URL } from '../constants.js'
import { useReveal } from '../hooks'
import { CheckIcon, CopyIcon, GithubIcon } from './Icons.jsx'

const COMMANDS = [
  `git clone ${GITHUB_URL}.git && cd Morrow`,
  'pip install -r requirements.txt',
  'python -m uvicorn backend.api:app',
  'cd frontend && npm install && npm run dev   # in a second terminal',
]

export default function GetStarted() {
  const revealRef = useReveal()
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (!copied) return
    const timeout = setTimeout(() => setCopied(false), 2000)
    return () => clearTimeout(timeout)
  }, [copied])

  const copyCommands = async () => {
    try {
      await navigator.clipboard.writeText(COMMANDS.join('\n'))
      setCopied(true)
    } catch {
      // Clipboard access can be blocked; the commands stay selectable.
    }
  }

  return (
    <section className="section get-started" id="get-started">
      <div className="get-started-glow" aria-hidden="true" />

      <div className="container get-started-inner reveal" ref={revealRef}>
        <p className="eyebrow">Get started</p>
        <h2>
          Your last meeting already happened.
          <br />
          <em>Find out what comes next.</em>
        </h2>
        <p className="section-lede">
          Run Morrow on your own machine. You need Python 3.10+, Node.js, FFmpeg and a free Groq API key.
        </p>

        <div className="terminal">
          <div className="terminal-bar">
            <span className="terminal-dots" aria-hidden="true">
              <span />
              <span />
              <span />
            </span>
            <button className="copy-button" type="button" onClick={copyCommands}>
              {copied ? <CheckIcon size={16} /> : <CopyIcon size={16} />}
              {copied ? 'Copied' : 'Copy'}
            </button>
          </div>
          <pre>
            {COMMANDS.map((command) => (
              <code key={command}>
                <span className="prompt">$</span> {command}
              </code>
            ))}
          </pre>
        </div>

        <a className="button button-primary" href={GITHUB_URL}>
          <GithubIcon />
          Star on GitHub
        </a>
      </div>
    </section>
  )
}
