# AI PPT DESIGN BRIEF
## Research Presentation: Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems
### Initial Case Study: Software-Level Fault Resilience for ML-KEM-768 Decapsulation (11-Slide Deck)

---

## 1. Recommended Presentation Theme

**Theme Name:** "Technical Blueprint Dark"

A precision-engineering aesthetic that communicates scientific rigor and technical depth. Think: a security research paper presented as a modern conference talk — not a startup pitch. Clean, readable, serious. Evokes reliability and precision.

---

## 2. Colour Palette

| Role | Colour | Hex Code |
|---|---|---|
| **Primary Background** | Deep Navy / Midnight Blue | `#0F1C2E` |
| **Secondary Background** | Dark Slate (cards, panels) | `#1B2B40` |
| **Primary Accent — Success / Confirmed** | Vivid Teal | `#00C9A7` |
| **Secondary Accent — Warning / Limitation** | Amber / Warm Yellow | `#FFC857` |
| **Danger / Alert** | Muted Crimson | `#C84B31` |
| **Primary Text** | Soft White | `#E8EDF5` |
| **Secondary Text / Annotations** | Light Grey | `#9AAABB` |
| **Data Highlight / Numbers** | Bright Cyan | `#5BC8F5` |
| **Diagram Line / Connector** | Mid Blue-Grey | `#4A7BA7` |

**Rationale:** Dark navy backgrounds reduce eye strain in lecture theatres and make metric cards and diagrams stand out sharply. Teal accent signals success states. Amber signals limitations and disclosures. Bright cyan makes numerical values immediately readable.

---

## 3. Typography

| Element | Font | Weight | Size Guidance |
|---|---|---|---|
| **Slide Title** | Inter / SF Pro Display | Bold 700 | Large (48–60pt) |
| **Section Headings** | Inter / SF Pro Text | SemiBold 600 | Medium (28–36pt) |
| **Body Text / Bullets** | Inter / Source Sans Pro | Regular 400 | Standard (18–22pt) |
| **Code Snippets** | JetBrains Mono / Fira Code | Regular | Small (15–18pt) |
| **Metric Cards / Numbers** | Inter | ExtraBold 800 | Extra-Large (40–56pt) |
| **Footnotes / Evidence Tags** | Inter | Italic / Light 300 | Small (12–14pt) |

**Rules:**
- Never use more than two font families per slide.
- Code snippets must be monospaced and placed on a slightly lighter panel background.
- Metric card numbers should dominate visually — they are the primary communication.

---

## 4. Layout Principles

1. **Single Strong Visual Per Slide:** Every slide must have one primary visual element (diagram, chart, or metric grid). Text bullets are secondary — they support the visual, not replace it.
2. **Left-Align Key Text:** All body bullets and annotations left-aligned for readability in lecture settings.
3. **Metric Cards:** Use 2×2 or 1×4 card grids for numerical results. Cards have a slightly lighter background than the slide, a bold number in cyan, and a short descriptor in secondary text.
4. **Maximum Bullet Depth:** Two levels only. No nested sub-bullets beyond one indent.
5. **Whitespace as Structure:** Generously pad all elements. Do not crowd the slide. Audience is reading from a distance.
6. **Evidence Source Footer:** Each slide should have a small bottom-right footnote listing the primary data source (e.g., "Source: phase18_audit/raw_production_trials.csv"). Use the footnote style (small, italic, secondary grey).

---

## 5. Diagram Style

**General Principles:**
- Use flat, minimal icons — no 3D effects, no gradients on icons.
- Connector lines should be clean right-angle arrows or simple curved beziers.
- Layered architecture diagrams: use distinct horizontal bands with clear labels.
- NTT butterfly diagrams: use a simple box-and-arrow circuit style.

**Specific Diagram Types:**
- **Architecture diagrams:** Dark panel background, each layer in a distinct color band (blue → amber → red for escalation severity). Fault injection shown as a red dashed arrow.
- **Timeline:** Horizontal strip with milestone blocks. Color-coded by phase group (Foundation=blue, Architecture=teal, Evidence=amber, Publication=green).
- **Comparison tables:** Minimal table styling, no grid lines except horizontal dividers. Bold row for "Our Monitored Architecture."
- **Butterfly equation diagrams:** Clean circuit-diagram style. Label each operand clearly. Use annotation arrows for invariant equations — no crowded inline text.

---

## 6. Chart Style

**Preferred Chart Types:**
1. **Bar Charts (horizontal preferred):** For latency comparisons.
   - **Crucial Rule for Slide 08 (Experimental Results):** Present TWO SEPARATE charts/panels:
     - **Chart A (End-to-End Decapsulation):** Baseline (110.77 µs) vs Monitored Architecture (129.51 µs, +16.9%).
     - **Chart B (Isolated NTT Benchmarks):** Baseline NTT (46.65 µs) vs Sequential DMR NTT (92.98 µs, +99.33%) vs Dual-Transform Monitor (80.30 µs, +17.27%).
     - *Never combine isolated transform measurements with full decapsulation numbers into a single chart.*
2. **Metric Cards / KPI Tiles:** For primary outcome numbers (0 SDC, 100% recovery rate, +16.9% overhead). Do not use pie charts for these — cards are cleaner.
3. **Confidence Interval Annotations:** Show Wilson CI ranges as small error bars or bracket annotations below the primary metric.
4. **No 3D Charts:** Strictly prohibited — misleads the audience on proportionality.
5. **No Pie Charts for Performance Data:** Use bar charts or KPI tiles.

**Chart Labeling Rules:**
- All axis labels must be legible at lecture distances (minimum 16pt).
- Primary value labels should appear directly on bars, not on axes alone.
- Units always stated (e.g., µs, %, trials).

---

## 7. Image and Illustration Guidance

**Permitted:**
- Simplified circuit-style architecture diagrams drawn in vector.
- Clean NTT butterfly box-and-arrow illustrations.
- Icon-based visual metaphors (shield icon for containment, retry arrow for rollback, satellite for motivation slide).
- Abstract chip/register imagery to support Slide 02 motivation (use as background texture at low opacity, not a dominant element).

**Prohibited:**
- Stock photos of people, handshakes, or generic "technology" imagery.
- Clip art or overly decorative icons.
- Any imagery implying physical hardware radiation testing (no beam photos, accelerator imagery, or space mission imagery that overstates the scope).
- Dense mathematical symbol images taken from PDFs — reproduce equations cleanly in the slide editor.

---

## 8. Rules to Avoid Overcrowded Slides

1. **Maximum 6 primary bullet points per slide.** If you have more content, split into two slides or use a table instead.
2. **Never put full sentences on bullets.** Short phrases only — maximum 12 words per bullet.
3. **One equation per slide maximum.** Supporting equations belong in speaker notes.
4. **Tables: maximum 5 columns, 5 rows.** If more rows are needed, use a simplified summary row.
5. **Code snippets: maximum 6 lines.** No scrollable code blocks.
6. **Do not repeat the slide title in the body text.** The heading is already on screen.
7. **Every metric needs a unit and a confidence qualifier** if it is a statistical result (e.g., "0/300, 95% CI: [0.00%, 1.26%]").

---

## 9. Consistent Visual Identity Across All Slides

**Persistent Elements (every slide):**
- Same background color (`#0F1C2E`)
- Slide number in bottom-left corner (small, secondary grey)
- Short slide title in top-left header bar (teal accent bar, 4px height)
- Evidence source footnote in bottom-right (small italic, grey)

**Slide Transitions:**
- Simple fade or slide-from-right. No spin, zoom, or complex animations.
- Builds (progressive reveals): permitted for architecture diagrams only. Maximum 3 build steps per slide.

**Icon Consistency:**
- Use the same icon set throughout (e.g., Material Icons or Heroicons — flat, outlined).
- Designate a fixed icon for each concept: ✅ Confirmed, ⚠️ Limitation, 🔁 Retry/Rollback, 🛡 Containment, 📊 Data, 🔬 Experiment.

---

*End of Design Brief*

