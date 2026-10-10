import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

const BASE_Y = 0.4

/** Eases the camera toward the pointer for a subtle parallax effect. */
export default function CameraRig() {
  useFrame(({ camera, pointer }, delta) => {
    camera.position.x = THREE.MathUtils.damp(camera.position.x, pointer.x * 0.5, 2, delta)
    camera.position.y = THREE.MathUtils.damp(camera.position.y, BASE_Y + pointer.y * 0.3, 2, delta)
    camera.lookAt(0, 0, 0)
  })

  return null
}
