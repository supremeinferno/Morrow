import { useReveal } from '../hooks'
import SectionHeading from './SectionHeading.jsx'

const STEPS = [
  {
    title: 'Extract',
    tool: 'yt-dlp',
    description: 'Pulls the audio track from a YouTube link.',
  },
  {
    title: 'Prepare',
    tool: 'FFmpeg',
    description: 'Converts to 16 kHz mono, levels the loudness, and splits it into overlapping chunks.',
  },
  {
    title: 'Transcribe',
    tool: 'Whisper',
    description: 'Turns speech into text, running locally on your machine.',
  },
  {
    title: 'Analyze',
    tool: 'Groq + LangChain',
    description: 'Extracts the summary, decisions, actions and questions, then merges long meetings.',
  },
  {
    title: 'Ask',
    tool: 'Chroma',
    description: 'Embeds the transcript so every answer is retrieved from the meeting itself.',
  },
]

export default function Pipeline() {
  const revealRef = useReveal()

  return (
    <section className="section section-tinted" id="how-it-works">
      <div className="container reveal" ref={revealRef}>
        <SectionHeading eyebrow="How it works" title="From recording to clarity in five steps.">
          One link in, one structured report out. Here's what happens in between.
        </SectionHeading>

        <ol className="pipeline">
          {STEPS.map((step, index) => (
            <li className="pipeline-step" key={step.title} style={{ '--step': index }}>
              <span className="pipeline-node">{index + 1}</span>
              <h3>{step.title}</h3>
              <p className="pipeline-tool">{step.tool}</p>
              <p>{step.description}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  )
}
