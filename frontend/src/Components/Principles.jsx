import { useReveal } from '../hooks'

const RULES = [
  { title: 'No invented names', description: 'Owners are listed only when someone was named.' },
  { title: 'No guessed deadlines', description: 'Dates appear only if they were said out loud.' },
  { title: 'No upgraded maybes', description: 'A suggestion never becomes a decision.' },
]

export default function Principles() {
  const revealRef = useReveal()

  return (
    <section className="section principles">
      <div className="container reveal" ref={revealRef}>
        <p className="eyebrow">Grounded by design</p>
        <blockquote className="statement">
          If it wasn't said in the meeting, <em>Morrow won't say it.</em>
        </blockquote>

        <div className="rule-grid">
          {RULES.map((rule) => (
            <div className="rule" key={rule.title}>
              <h3>{rule.title}</h3>
              <p>{rule.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
