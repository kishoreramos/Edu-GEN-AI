# Phase 3: Project Design Phase — User Interface & Visual Design System
## Project: EduGenie — Google Gemini Powered Learning Assistant

---

### 1. Design Philosophy
The EduGenie interface is designed around a single core principle: **Pedagogical Focus with Ambient Aesthetics**.
Instead of overwhelming students with cluttered panels, toolbars, and forms, EduGenie presents a distraction-free, modern AI workspace inspired by celestial depth and fluid motion:
- **Clean Spatial Hierarchy:** Primary focus rests on the conversational stream and composer.
- **Deep Space Palette:** Relieves eye fatigue during extended study sessions.
- **Interactive Lightfall Canvas:** An ambient, GPU-accelerated background that provides continuous visual life without competing with readability.

---

### 2. Design Tokens & Color Palette

| Token Name | Hex / Value | Semantic Role |
| :--- | :--- | :--- |
| `--bg-base` | `#050510` | Deep cosmic black background base |
| `--bg-surface` | `rgba(255, 255, 255, 0.025)` | Translucent glassmorphic cards and containers |
| `--bg-surface-elevated` | `rgba(13, 19, 33, 0.70)` | Active dialogs and elevated assistant message bubbles |
| `--bg-composer` | `rgba(10, 15, 26, 0.85)` | Docked input bar with backdrop blur |
| `--accent-indigo` | `#5227FF` | Primary action color, hero glow, and brand sparkle |
| `--accent-blue` | `#4C6FFF` | Electric azure blue accents and intermediate trails |
| `--accent-cyan` | `#66CCFF` | Vibrant cyan highlighting and interactive chips |
| `--accent-violet` | `#B58CFF` | Soft secondary accents and pedagogical tags |
| `--text-primary` | `#F5F7FF` | High-contrast readable typography for body text |
| `--text-secondary` | `#C4CDDC` | Subtitles, labels, and secondary information |
| `--text-muted` | `#8D96AA` | Metadata, keyboard shortcuts, and timestamps |

---

### 3. Application Layout & State Transitions

#### 3.1 Home State (`.state-home`)
- **Visual Composition:** Centered hero section vertically balanced across the viewport.
- **Components:**
  - **Brand Sparkle (`✦`):** Luminous indigo marker anchoring the visual center.
  - **Brand Title (`EduGenie`):** Minimal uppercase tracker.
  - **Primary Headline:** *"Learn anything. Understand everything."* with an electric gradient fill.
  - **Sub-lead Prompt:** Concise educational invitation.
  - **Centered Composer Dock:** Floating input field accompanied by six capability task chips (`Auto`, `Explain`, `Q&A`, `Quiz`, `Summary`, `Learning Path`).

#### 3.2 Chat State (`.state-chat`)
- **Transition:** Entering a message or loading an existing session smoothly fades out the welcome hero and expands the scrollable conversation viewport.
- **Components:**
  - **Minimal Sticky Header:** Contains the EduGenie brand, active topic indicator pill (`#activeTopicBadge`), and a *"New Chat"* action button.
  - **Scrollable Message Stream (`#messagesContainer`):**
    - **User Bubbles:** Right-aligned, semi-transparent indigo tint.
    - **Assistant Bubbles:** Left-aligned, rich Markdown formatting (code blocks, bullet points, bold concepts), topic tag pill, and copy controls.
    - **Interactive Quiz Cards:** Renders question text with 4 clickable option buttons that instantly reveal correct/incorrect feedback upon click.
    - **Contextual Suggestion Chips:** 2 to 3 contextual follow-up buttons (e.g., *"✦ Quiz me"*, *"💡 Give an example"*, *"🐣 Explain simpler"*).
  - **Docked Composer:** Fixed to the bottom edge with a subtle gradient backdrop fade.

---

### 4. Interactive Lightfall Background Architecture (`lightfall.js`)

```
+--------------------------------------------------------------+
| Canvas 2D Engine (Single requestAnimationFrame Loop)        |
|                                                              |
|  [ Layer 1: Celestial Nebula Bloom ]                         |
|    - Radial gradient anchored at upper-center (w*0.48, h*0.18)|
|    - Royal Purple (#5227FF) & Cyan (#66CCFF) ambient bleed   |
|                                                              |
|  [ Layer 2: 3-Tier Perspective Light Trails ]                |
|    - Deep Cosmic (40%): Long (300-550px), thin, faint violet |
|    - Midground (40%): Moderate speed, electric blue/cyan     |
|    - Hero Foreground (20%): Fast, thick, brilliant tips      |
|    - Trajectory: Cohesive diagonal flow (~26° from vertical) |
|    - Curvature: Continuous Bezier arcs with harmonic sway    |
|                                                              |
|  [ Layer 3: Interactive Reactive Dynamics ]                  |
|    - Pointer proximity deflection & luminous aura            |
|    - Chat Mode Auto-Dimming (1.0 -> 0.45 opacity)            |
|    - Accessibility: prefers-reduced-motion halts RAF loop    |
+--------------------------------------------------------------+
```

---

### 5. Responsive Design Breakpoints
- **Desktop ($\ge 1024\text{px}$):** Max-width 780px centered chat container, full Lightfall streak density (55 to 95 trails), hover micro-interactions.
- **Tablet ($768\text{px} - 1023\text{px}$):** Fluid margins, full-width composer padding.
- **Mobile ($< 768\text{px}$):**
  - Lightfall streak density automatically reduced by $55\%$ to conserve GPU/battery life.
  - Touch-optimized tap targets ($\ge 44\text{px}$) for task chips and quiz options.
  - Composer scrolls horizontally for task chips without breaking viewport bounds.
  - Disables pointer hover tracking, preserving touch scroll performance.
