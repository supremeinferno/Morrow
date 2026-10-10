import { useEffect, useMemo, useRef } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import * as THREE from 'three'

import { orbFragmentShader, orbVertexShader } from './shaders.js'

const ORB_RADIUS = 1.35
const RING_RADIUS = 2.2

function buildSphere(count, radius) {
  const positions = new Float32Array(count * 3)
  const scales = new Float32Array(count)
  const goldenAngle = Math.PI * (3 - Math.sqrt(5))

  // Fibonacci sphere: evenly spread points without clumping at the poles.
  for (let i = 0; i < count; i++) {
    const y = 1 - (i / (count - 1)) * 2
    const ringRadius = Math.sqrt(1 - y * y)
    const theta = goldenAngle * i

    positions[i * 3] = Math.cos(theta) * ringRadius * radius
    positions[i * 3 + 1] = y * radius
    positions[i * 3 + 2] = Math.sin(theta) * ringRadius * radius
    scales[i] = 0.5 + Math.random()
  }

  const geometry = new THREE.BufferGeometry()
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  geometry.setAttribute('aScale', new THREE.BufferAttribute(scales, 1))
  return geometry
}

function buildRing(count, radius) {
  const positions = new Float32Array(count * 3)

  for (let i = 0; i < count; i++) {
    const angle = Math.random() * Math.PI * 2
    const spread = radius + (Math.random() - 0.5) * 0.35

    positions[i * 3] = Math.cos(angle) * spread
    positions[i * 3 + 1] = (Math.random() - 0.5) * 0.04
    positions[i * 3 + 2] = Math.sin(angle) * spread
  }

  const geometry = new THREE.BufferGeometry()
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  return geometry
}

export default function VoiceOrb({ speed = 1 }) {
  const group = useRef()
  const ring = useRef()
  const material = useRef()
  const time = useRef(0)

  const size = useThree((state) => state.size)
  const viewport = useThree((state) => state.viewport)
  const isWide = size.width >= 900

  const sphereGeometry = useMemo(() => buildSphere(isWide ? 9000 : 5000, ORB_RADIUS), [isWide])
  const ringGeometry = useMemo(() => buildRing(1400, RING_RADIUS), [])

  useEffect(() => () => sphereGeometry.dispose(), [sphereGeometry])
  useEffect(() => () => ringGeometry.dispose(), [ringGeometry])

  const uniforms = useMemo(() => ({
    uTime: { value: 0 },
    uSpeak: { value: 0 },
    uPixelRatio: { value: Math.min(window.devicePixelRatio, 2) },
    uColorCool: { value: new THREE.Color('#8b7bff') },
    uColorWarm: { value: new THREE.Color('#ffb45e') },
    uColorRim: { value: new THREE.Color('#ff7a8a') },
  }), [])

  useFrame((_, delta) => {
    time.current += delta * speed
    const t = time.current

    // A rough speech envelope: fast syllables inside slower phrases.
    const phrase = Math.max(0, Math.sin(t * 0.6))
    const syllables = 0.5 + 0.5 * Math.sin(t * 7.3) * Math.sin(t * 3.1)
    const shaderUniforms = material.current.uniforms

    shaderUniforms.uTime.value = t
    shaderUniforms.uSpeak.value = THREE.MathUtils.damp(
      shaderUniforms.uSpeak.value,
      phrase * syllables,
      6,
      delta,
    )

    group.current.rotation.y += delta * 0.08 * speed
    ring.current.rotation.y -= delta * 0.05 * speed
  })

  // Sit beside the headline on wide screens, above it on narrow ones.
  const position = isWide ? [viewport.width * 0.25, 0.25, 0] : [0, viewport.height * 0.2, 0]
  const scale = isWide ? 1 : 0.72

  return (
    <group position={position} scale={scale}>
      <group ref={group}>
        <points geometry={sphereGeometry}>
          <shaderMaterial
            ref={material}
            vertexShader={orbVertexShader}
            fragmentShader={orbFragmentShader}
            uniforms={uniforms}
            transparent
            depthWrite={false}
            blending={THREE.AdditiveBlending}
          />
        </points>
      </group>

      <group rotation={[1.25, 0, 0.3]}>
        <points ref={ring} geometry={ringGeometry}>
          <pointsMaterial
            color="#b9b0ff"
            size={0.018}
            sizeAttenuation
            transparent
            opacity={0.55}
            depthWrite={false}
            blending={THREE.AdditiveBlending}
          />
        </points>
      </group>
    </group>
  )
}
