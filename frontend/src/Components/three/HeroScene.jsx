import { useEffect, useState } from 'react'
import { Canvas } from '@react-three/fiber'
import { Stars } from '@react-three/drei'

import { usePrefersReducedMotion } from '../../hooks'
import CameraRig from './CameraRig.jsx'
import VoiceOrb from './VoiceOrb.jsx'
import WaveHorizon from './WaveHorizon.jsx'

export default function HeroScene({ eventSource }) {
  const reducedMotion = usePrefersReducedMotion()
  const [isOnScreen, setIsOnScreen] = useState(true)
  const speed = reducedMotion ? 0.15 : 1

  // Stop rendering once the hero scrolls out of view.
  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => setIsOnScreen(entry.isIntersecting))
    observer.observe(eventSource.current)
    return () => observer.disconnect()
  }, [eventSource])

  return (
    <Canvas
      camera={{ position: [0, 0.4, 7], fov: 42 }}
      dpr={[1, 1.75]}
      gl={{ antialias: true, alpha: true, powerPreference: 'high-performance' }}
      eventSource={eventSource}
      eventPrefix="client"
      frameloop={isOnScreen ? 'always' : 'never'}
    >
      <fog attach="fog" args={['#07060f', 7, 22]} />
      <CameraRig />
      <VoiceOrb speed={speed} />
      <WaveHorizon speed={speed} />
      <Stars radius={50} depth={40} count={1800} factor={2.5} saturation={0} fade speed={speed * 0.6} />
    </Canvas>
  )
}
