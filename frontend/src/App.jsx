import {
  Demo,
  Features,
  Footer,
  GetStarted,
  Hero,
  Navbar,
  Pipeline,
  Principles,
  TechStack,
} from './Components'
import './App.css'

export default function App() {
  return (
    <>
      <Navbar />
      <main>
        <Hero />
        <TechStack />
        <Features />
        <Pipeline />
        <Demo />
        <Principles />
        <GetStarted />
      </main>
      <Footer />
    </>
  )
}
