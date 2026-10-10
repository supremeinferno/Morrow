# Morrow Frontend

The Morrow web app: a **React 19 + Vite** single-page app with a **Three.js** hero scene. Users submit a meeting link or recording, follow its progress, read the report and chat with the meeting.

For the project overview, see the [main README](../README.md). The API it talks to is documented in the [backend README](../backend/README.md).

---

## Table of Contents

- [Getting Started](#getting-started)
- [Scripts](#scripts)
- [How It Talks to the Backend](#how-it-talks-to-the-backend)
- [Project Structure](#project-structure)
- [Components](#components)
- [The 3D Hero Scene](#the-3d-hero-scene)
- [Styling](#styling)
- [Accessibility & Performance](#accessibility--performance)
- [Production Build](#production-build)

---

## Getting Started

**Requirements:** Node.js 20.19+ or 22.12+, and the [backend](../backend/README.md) running on port `8000`.

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**.

---

## Scripts

| Command | Description |
| --- | --- |
| `npm run dev` | Start the dev server with hot reload and the `/api` proxy |
| `npm run build` | Build an optimized production bundle into `dist/` |
| `npm run preview` | Serve the production build locally |
| `npm run lint` | Run ESLint, including the React Hooks rules |

---

## How It Talks to the Backend

In development, Vite forwards every `/api` request to `http://localhost:8000` (see [`vite.config.js`](vite.config.js)), so the app uses relative URLs and needs no CORS setup.

All network calls live in [`src/api.js`](src/api.js):

| Function | Endpoint | Notes |
| --- | --- | --- |
| `createMeetingFromLink(url)` | `POST /api/meetings` | Sends the link as form data |
| `uploadMeeting(file, onProgress)` | `POST /api/meetings` | Uses `XMLHttpRequest` to report upload progress |
| `getMeeting(id)` | `GET /api/meetings/:id` | Polled by `useMeeting` |
| `askQuestion(id, question)` | `POST /api/meetings/:id/questions` | Used by the chat |

**Flow:**
1. `MeetingInput` creates a meeting.
2. `App` stores its ID in the URL (`?meeting=<id>`).
3. `Workspace` mounts and `useMeeting` polls every 2 s until the status is `ready` or `failed`.
4. The report and chat render.

Because the ID is in the URL, a refresh or a shared link reopens the same meeting.

---

## Project Structure

```text
frontend/
├── index.html                 # Fonts, meta tags, root element
├── vite.config.js             # React plugin + /api dev proxy
├── public/
│   └── favicon.svg
└── src/
    ├── main.jsx               # React entry point
    ├── App.jsx                # Page layout + current meeting (URL-synced)
    ├── api.js                 # Backend client
    ├── constants.js           # Shared constants (GitHub URL)
    ├── index.css              # Design tokens, base styles, buttons, forms
    ├── App.css                # Section and component styles
    ├── hooks/
    │   ├── index.js
    │   ├── useMeeting.js      # Fetch + poll a meeting until it finishes
    │   ├── useReveal.js       # Fade sections in on scroll
    │   └── usePrefersReducedMotion.js
    └── Components/
        ├── index.js           # Re-exports the page sections
        ├── Navbar.jsx
        ├── Hero.jsx           # Headline + MeetingInput + lazy 3D scene
        ├── MeetingInput.jsx   # Link / file upload form
        ├── Workspace.jsx      # Progress, error and results states
        ├── MeetingReport.jsx  # Summary, decisions, actions, questions
        ├── MeetingChat.jsx    # RAG chatbot UI
        ├── TechStack.jsx
        ├── Features.jsx
        ├── Pipeline.jsx       # "How it works" steps
        ├── Principles.jsx     # "Grounded by design"
        ├── GetStarted.jsx     # Self-hosting commands
        ├── Footer.jsx
        ├── SectionHeading.jsx
        ├── Icons.jsx          # Inline SVG icon set + logo
        └── three/             # Three.js hero scene
            ├── HeroScene.jsx
            ├── VoiceOrb.jsx
            ├── WaveHorizon.jsx
            ├── CameraRig.jsx
            └── shaders.js
```

> **Note:** the folder is `Components` with a capital **C**. macOS ignores case in paths but Linux doesn't, so keep imports as `./Components` or builds will fail on Linux CI and hosting.

---

## Components

| Component | Responsibility |
| --- | --- |
| `MeetingInput` | Tabs for **Paste a link** / **Upload a file**, drag-and-drop dropzone, upload progress, validation errors |
| `Workspace` | Picks the view for the meeting's status: progress steps, error card, or report + chat |
| `MeetingReport` | Renders the analysis. Normalizes LLM items that may be strings or `{ task, owner, deadline }` objects. Copy-to-clipboard and full transcript |
| `MeetingChat` | Suggested questions, free-text input, "thinking" indicator, error bubbles |

---

## The 3D Hero Scene

Built with [React Three Fiber](https://r3f.docs.pmnd.rs/) and [drei](https://github.com/pmndrs/drei). The theme is dawn: "Morrow" means tomorrow.

| Piece | What it does |
| --- | --- |
| `VoiceOrb` | ~9,000 points on a Fibonacci sphere, displaced by simplex noise in a custom GLSL shader. A synthetic speech envelope makes it "talk" |
| `WaveHorizon` | An instanced mesh of equalizer bars rippling across the horizon |
| `CameraRig` | Eases the camera toward the pointer for subtle parallax |
| `Stars` (drei) | Background starfield |

The orb moves beside the headline on wide screens and above it on narrow ones, and uses fewer particles on mobile.

---

## Styling

Plain CSS, no framework.

- **`index.css`** holds the design tokens (`--bg`, `--amber`, `--rose`, `--violet`, the `--dawn` gradient, radii, fonts) plus base, button and form styles.
- **`App.css`** holds the styles for each section and component.
- **Fonts:** [Geist](https://vercel.com/font) for UI, Instrument Serif for italic accents, Geist Mono for labels and code. All load from Google Fonts in `index.html`.

---

## Accessibility & Performance

- **Lazy 3D.** The Three.js bundle loads in its own chunk, so the headline and form render first.
- **Off-screen pause.** The canvas stops rendering when the hero scrolls out of view.
- **Reduced motion.** `prefers-reduced-motion` slows the 3D scene to a crawl and disables CSS animations and smooth scrolling.
- **Live regions.** Progress text and chat answers use `aria-live`, so screen readers announce updates.
- **Keyboard support.** All controls are native buttons, inputs and links with visible focus styles.

---

## Production Build

```bash
npm run build
```

The output in `dist/` is static and can be served by any static host. The app calls the API at the **same origin** (`/api/...`), so in production you need one of these:

- **Same server:** put a reverse proxy (nginx, Caddy) in front that routes `/api` to the FastAPI server and everything else to `dist/`.
- **Separate API domain:** change the base URL in `src/api.js` and enable CORS in the FastAPI app.

The build warns that the Three.js chunk is over 500 kB. That's expected, and it's loaded lazily after the page renders.
