import { useReveal } from '../hooks'
import { ActionIcon, ChatIcon, DecisionIcon, QuestionIcon, SummaryIcon } from './Icons.jsx'
import SectionHeading from './SectionHeading.jsx'

const OUTCOMES = [
  {
    icon: SummaryIcon,
    title: 'Summary',
    description: 'The key discussion and context, condensed into a few clear lines.',
    sample: 'Team reviewed the release plan and backend timeline.',
  },
  {
    icon: DecisionIcon,
    title: 'Decisions',
    description: 'Only what was actually decided. Suggestions and maybes stay out.',
    sample: 'Use PostgreSQL for production.',
  },
  {
    icon: ActionIcon,
    title: 'Action items',
    description: 'Tasks with owners and deadlines, but only when someone said them.',
    sample: 'Auth API · Pranav · Friday',
  },
  {
    icon: QuestionIcon,
    title: 'Open questions',
    description: 'What was raised but never resolved, so nothing slips through.',
    sample: 'Email notifications in v1?',
  },
]

export default function Features() {
  const revealRef = useReveal()

  return (
    <section className="section" id="features">
      <div className="container reveal" ref={revealRef}>
        <SectionHeading eyebrow="What you get" title="Every meeting, distilled into four answers.">
          Skip the rewatch. Morrow reads the whole conversation and pulls out the parts you
          actually need to act on.
        </SectionHeading>

        <div className="outcome-grid">
          {OUTCOMES.map(({ icon: OutcomeIcon, title, description, sample }, index) => (
            <article className="card outcome-card" key={title}>
              <div className="outcome-top">
                <span className="icon-badge">
                  <OutcomeIcon />
                </span>
                <span className="outcome-index">0{index + 1}</span>
              </div>
              <h3>{title}</h3>
              <p>{description}</p>
              <p className="outcome-sample">{sample}</p>
            </article>
          ))}
        </div>

        <article className="card ask-card">
          <span className="icon-badge icon-badge-large">
            <ChatIcon size={24} />
          </span>
          <div>
            <h3>Ask your meeting anything</h3>
            <p>
              Every transcript becomes a searchable knowledge base. Ask in plain English, and
              Morrow answers from what was actually said.
            </p>
          </div>
          <a className="button button-ghost" href="#demo">
            Try a question
          </a>
        </article>
      </div>
    </section>
  )
}
