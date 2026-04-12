---
name: design-md
description: >-
  Extract design system guidelines (DESIGN.md) from static HTML files. Analyzes
  atmosphere, colors, typography, geometry, and depth.
---

# Design-MD

Extract a "source of truth" for your project's design language from existing HTML files.

## 🧠 Analysis & Synthesis

After obtaining the HTML, perform these concrete extraction steps:

### 1. Identify Identity

- Capture the Project Title and Project ID.

### 2. Define Atmosphere

- Read the HTML and look for overall patterns:
  - **Background colors**: What is the `<body>` or root `background-color`?
    Light (#f-range) → Airy/Clean. Dark (#0-#2 range) → Moody/Dark Mode.
  - **Whitespace**: Are there large `padding`/`margin` values (32px+)?
    → "Generous whitespace, breathing room".
  - **Overall density**: Lots of components packed tightly → "Information-dense".
    Few components with space → "Minimal, focused".
- Summarize in 1–2 sentences using atmosphere vocabulary.

### 3. Map Color Palette

Scan the HTML for these CSS properties and Tailwind classes:

| What to search for | CSS Properties | Tailwind patterns |
|:---|:---|:---|
| **Backgrounds** | `background-color`, `background` | `bg-*` |
| **Text colors** | `color` | `text-*` |
| **Borders/Accents** | `border-color`, `outline-color` | `border-*`, `ring-*` |
| **Button/CTA colors** | Background of `<button>`, `<a>` elements | `bg-*` on buttons |
| **Hover/Active states** | `:hover` pseudo-class colors | `hover:bg-*` |

For each unique color found, assign a functional role with a descriptive name:
- `#2563eb` on primary buttons → **"Electric Blue"** (#2563eb) — Primary Action
- `#6b7280` on body text → **"Slate Gray"** (#6b7280) — Body Text
- `#f9fafb` on page background → **"Whisper White"** (#f9fafb) — Page Background

### 4. Extract Typography

Search for font declarations:

| What to search for | CSS Properties | Tailwind patterns |
|:---|:---|:---|
| **Font families** | `font-family` | `font-sans`, `font-serif`, `font-mono` |
| **Heading sizes** | `font-size` on `<h1>`–`<h6>` | `text-xl`, `text-2xl`, etc. |
| **Font weights** | `font-weight` | `font-bold`, `font-semibold`, etc. |
| **Line heights** | `line-height` | `leading-*` |

Document as: "**Headings**: [Font], [Weight] — [Usage]" (e.g., "**Headings**: Inter, Bold (700) — Section titles and hero headlines").

### 5. Translate Geometry

Search for border-radius values and convert to natural language:

| CSS / Tailwind | Description |
|:---|:---|
| `border-radius: 0` / `rounded-none` | Sharp, squared-off edges |
| `border-radius: 4px` / `rounded` | Slightly softened corners |
| `border-radius: 8px` / `rounded-lg` | Generously rounded corners |
| `border-radius: 12px` / `rounded-xl` | Very rounded, pillow-like |
| `border-radius: 9999px` / `rounded-full` | Pill-shaped, circular |

### 6. Document Depth & Shadows

Search for `box-shadow` properties or Tailwind `shadow-*` classes:

| Shadow Pattern | Description |
|:---|:---|
| No shadows, only borders | **Flat**: Color blocking and borders |
| `0 1px 2px` / `shadow-sm` | **Whisper-soft**: Subtle lift |
| `0 4px 6px` / `shadow-md` | **Moderate**: Gentle elevation |
| `0 10px 15px` / `shadow-lg` | **Floating**: High above the surface |
| `inset` shadows | **Inset**: Pressable or nested elements |

## 📝 Output Structure

Create a `.stitch/DESIGN.md` file in the project directory with this structure:

```markdown
# Design System: [Project Title]
**Project ID:** [Insert Project ID Here]

## 1. Visual Theme & Atmosphere
[1–2 sentences describing the mood, aesthetic philosophy, and overall feel. Use specific atmosphere descriptors like "Calm, airy, and nurturing" not vague ones like "modern".]

## 2. Color Palette & Roles
[List each color with a descriptive name, hex code, and functional role:]
- **[Descriptive Name]** (#hexcode) — [Role in the UI]
- **[Descriptive Name]** (#hexcode) — [Role in the UI]

## 3. Typography Rules
- **Headings**: [Font Family], [Weight] — [Usage]
- **Body**: [Font Family], [Weight] — [Usage]
- **Base size**: [size]px, H1 at [size]px

## 4. Component Stylings
* **Buttons**: [Shape], [colors], [hover behavior]
* **Cards**: [Border style], [shadow/elevation]
* **Navigation**: [Style description]

## 5. Layout Principles
- [Content width strategy]
- [Vertical spacing between sections]
- [Responsive approach]
```

## 💡 Best Practices

- **Be Precise**: Always include hex codes in parentheses.
- **Be Descriptive**: Use natural language like "Deep Ocean Blue" instead of just "Blue".
- **Be Functional**: Explain *why* an element is used.
