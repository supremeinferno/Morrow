import { useState } from 'react'

import {
  ActionIcon,
  CheckIcon,
  CopyIcon,
  DecisionIcon,
  QuestionIcon,
  SummaryIcon,
} from './Icons.jsx'

const SECTIONS = [
  { key: 'decisions', title: 'Decisions', icon: DecisionIcon },
  { key: 'actions', title: 'Action items', icon: ActionIcon },
  { key: 'questions', title: 'Open questions', icon: QuestionIcon },
]

/**
 * The LLM returns items either as plain strings or as objects such as
 * { task, owner, deadline }. Normalize both into { text, meta }.
 */
function formatItem(item) {
  if (typeof item === 'string') return { text: item, meta: '' }

  const text =
    item.task ?? item.action ?? item.decision ?? item.question ?? item.description ?? item.text ??
    Object.values(item).find((value) => typeof value === 'string') ?? ''
  const owner = item.owner ?? item.responsible ?? item.assignee ?? item.person
  const deadline = item.deadline ?? item.due ?? item.due_date

  return { text, meta: [owner, deadline].filter(Boolean).join(' · ') }
}

function reportAsText(title, result) {
  const lines = [title, '', 'SUMMARY', result.summary || 'No summary available.']

  for (const { key, title: sectionTitle } of SECTIONS) {
    lines.push('', sectionTitle.toUpperCase())
    const items = result[key] ?? []

    if (!items.length) lines.push('None identified.')

    for (const item of items) {
      const { text, meta } = formatItem(item)
      lines.push(`- ${text}${meta ? ` (${meta})` : ''}`)
    }
  }

  return lines.join('\n')
}

export default function MeetingReport({ title, result, transcript }) {
  const [copied, setCopied] = useState(false)

  const copyReport = async () => {
    try {
      await navigator.clipboard.writeText(reportAsText(title, result))
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // Clipboard access can be blocked; nothing else to do.
    }
  }

  return (
    <div className="card report">
      <div className="report-header">
        <h3>Meeting report</h3>
        <button className="copy-button" type="button" onClick={copyReport}>
          {copied ? <CheckIcon size={16} /> : <CopyIcon size={16} />}
          {copied ? 'Copied' : 'Copy'}
        </button>
      </div>

      <div className="report-section">
        <h4>
          <SummaryIcon size={16} />
          Summary
        </h4>
        <p className="report-summary">{result.summary || 'No summary available.'}</p>
      </div>

      {SECTIONS.map(({ key, title: sectionTitle, icon: SectionIcon }) => {
        const items = (result[key] ?? []).map(formatItem)

        return (
          <div className="report-section" key={key}>
            <h4>
              <SectionIcon size={16} />
              {sectionTitle}
              <span className="report-count">{items.length}</span>
            </h4>

            {items.length ? (
              <ul>
                {items.map(({ text, meta }, index) => (
                  <li key={index}>
                    {text}
                    {meta && <span className="report-meta">{meta}</span>}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="report-empty">None identified.</p>
            )}
          </div>
        )
      })}

      {transcript && (
        <details className="transcript">
          <summary>View full transcript</summary>
          <p>{transcript}</p>
        </details>
      )}
    </div>
  )
}
