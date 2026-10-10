import { GITHUB_URL } from '../constants.js'
import { GithubIcon, LogoMark } from './Icons.jsx'

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container footer-inner">
        <a className="brand" href="#top" aria-label="Back to top">
          <LogoMark size={22} />
          <span>morrow</span>
        </a>

        <p className="footer-tagline">Turn conversations into what comes next.</p>

        <a className="icon-link" href={GITHUB_URL} aria-label="Morrow on GitHub">
          <GithubIcon />
        </a>
      </div>
    </footer>
  )
}
