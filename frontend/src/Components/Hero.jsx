import { lazy, Suspense, useRef } from 'react'

import { GITHUB_URL } from '../constants.js'
import { ArrowIcon, GithubIcon } from './Icons.jsx'

// Loaded separately so the headline renders before three.js arrives.
const HeroScene = lazy(() => import('./three/HeroScene.jsx'))

export default function Hero() {
  const heroRef = useRef(null)

  return (
    <section className="hero" id="top" ref={heroRef}>
      <div className="hero-glow" aria-hidden="true" />

      <div className="hero-canvas" aria-hidden="true">
        <Suspense fallback={null}>
          <HeroScene eventSource={heroRef} />
        </Suspense>
      </div>

      <div className="hero-content container">
        <p className="eyebrow">
          <span className="eyebrow-dot" />
          AI meeting assistant
        </p>

        <h1 className="hero-title">
          Turn conversations into <em>what comes next.</em>
        </h1>

        <p className="hero-lede">
          Morrow listens to your meeting recordings and gives you back what matters: the
          summary, the decisions, the action items, and the questions still left open.
        </p>

        <div className="hero-actions">
          <a className="button button-primary" href="#demo">
            See it in action
            <ArrowIcon size={18} />
          </a>
          <a className="button button-ghost" href={GITHUB_URL}>
            <GithubIcon />
            View on GitHub
          </a>
        </div>
      </div>

      <a className="scroll-cue" href="#features" aria-label="Scroll to features">
        <span />
      </a>
    </section>
  )
}
