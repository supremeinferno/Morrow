import { useLayoutEffect, useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

const COLUMNS = 96
const ROWS = 10
const SPAN_X = 32
const NEAR_Z = -4
const FAR_Z = -20
const FLOOR_Y = -2.5

const warm = new THREE.Color('#ffb45e')
const rose = new THREE.Color('#ff7a8a')
const cool = new THREE.Color('#8b7bff')

function buildLayout() {
  const bars = []

  for (let row = 0; row < ROWS; row++) {
    for (let column = 0; column < COLUMNS; column++) {
      const x = (column / (COLUMNS - 1) - 0.5) * SPAN_X
      const z = NEAR_Z + (row / (ROWS - 1)) * (FAR_Z - NEAR_Z)
      const centerWeight = 1 - Math.min(Math.abs(x) / (SPAN_X / 2), 1)

      // Warm at the center of the horizon, cooling toward the edges.
      const color = centerWeight > 0.5
        ? rose.clone().lerp(warm, (centerWeight - 0.5) * 2)
        : cool.clone().lerp(rose, centerWeight * 2)

      bars.push({ x, z, row, centerWeight, color })
    }
  }

  return bars
}

/** A field of equalizer bars that ripples like speech along the horizon. */
export default function WaveHorizon({ speed = 1 }) {
  const mesh = useRef()
  const time = useRef(0)
  const bars = useMemo(() => buildLayout(), [])
  const dummy = useMemo(() => new THREE.Object3D(), [])

  useLayoutEffect(() => {
    bars.forEach((bar, index) => mesh.current.setColorAt(index, bar.color))
    mesh.current.instanceColor.needsUpdate = true
  }, [bars])

  useFrame((_, delta) => {
    time.current += delta * speed
    const t = time.current

    bars.forEach((bar, index) => {
      const wave =
        Math.sin(bar.x * 0.9 + t * 2.2) * 0.5 +
        Math.sin(bar.x * 0.37 - t * 1.3 + bar.row * 0.6) * 0.5
      const depthFalloff = 1 - (bar.row / ROWS) * 0.5
      const height = 0.03 + Math.abs(wave) * (0.1 + bar.centerWeight * 0.75) * depthFalloff

      dummy.position.set(bar.x, FLOOR_Y + height / 2, bar.z)
      dummy.scale.set(1, height, 1)
      dummy.updateMatrix()
      mesh.current.setMatrixAt(index, dummy.matrix)
    })

    mesh.current.instanceMatrix.needsUpdate = true
  })

  return (
    <instancedMesh ref={mesh} args={[undefined, undefined, bars.length]} frustumCulled={false}>
      <boxGeometry args={[0.06, 1, 0.06]} />
      <meshBasicMaterial transparent opacity={0.6} toneMapped={false} />
    </instancedMesh>
  )
}
