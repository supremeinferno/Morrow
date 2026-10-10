const STACK = [
  { name: 'Whisper', role: 'Speech-to-text' },
  { name: 'Groq', role: 'LLM inference' },
  { name: 'LangChain', role: 'Orchestration' },
  { name: 'Chroma', role: 'Vector store' },
  { name: 'MiniLM', role: 'Embeddings' },
  { name: 'FFmpeg', role: 'Audio processing' },
  { name: 'yt-dlp', role: 'Audio download' },
]

export default function TechStack() {
  return (
    <section className="stack" aria-label="Technology">
      <div className="container">
        <p className="stack-label">Built on open, proven tools</p>
        <ul className="stack-list">
          {STACK.map((tool) => (
            <li key={tool.name}>
              <span className="stack-name">{tool.name}</span>
              <span className="stack-role">{tool.role}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}
