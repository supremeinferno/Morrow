import { useEffect, useState } from 'react'

import { GITHUB_URL } from '../constants.js'
import { GithubIcon, LogoMark } from './Icons.jsx'

const LINKS = [
  { href: '#features', label: 'Features' },
  { href: '#how-it-works', label: 'How it works' },
  { href: '#get-started', label: 'Self-host' },
]

export default function Navbar() {
  const [isScrolled, setIsScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setIsScrolled(window.scrollY > 24)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <header className={`navbar ${isScrolled ? 'is-scrolled' : ''}`}>
      <nav className="navbar-inner container" aria-label="Main">
        <a className="brand" href="#top" aria-label="Morrow home">
          <LogoMark />
          <span>morrow</span>
        </a>

        <ul className="nav-links">
          {LINKS.map((link) => (
            <li key={link.href}>
              <a href={link.href}>{link.label}</a>
            </li>
          ))}
        </ul>

        <div className="nav-actions">
          <a className="icon-link" href={GITHUB_URL} aria-label="Morrow on GitHub">
            <GithubIcon />
          </a>
          <a className="button button-small button-primary" href="#top">
            Analyze a meeting
          </a>
        </div>
      </nav>
    </header>
  )
}
