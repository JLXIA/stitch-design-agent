---
name: stitch::text-to-design
description: >-
  Generate new screens from a text prompt using Stitch MCP. Includes prompt
  enhancement pipeline, design mappings, and professional UI/UX terminology.
---

# Text-to-Design

Transform a text description into a high-fidelity design screen.

> [!NOTE]
> Refer to your system prompt for instruction on handling MCP tool prefixes for
> all tools mentioned in this skill (e.g., `list_projects`,
> `generate_screen_from_text`).

## 🎨 Prompt Enhancement Pipeline

Before calling any Stitch generation tool, you MUST enhance the user's prompt.

### 1. Analyze Context

- **Project**: Use `list_projects` to find the correct `projectId`. If no
  suitable project exists, create one using `create_project`.
- **Design System**: Check if a design system exists for the project via
  `list_design_systems`. If one exists, design tokens (colors, fonts, roundness)
  are already applied at the project level — do NOT include any color, font, or
  theme instructions in the generation prompt. If none exists, delegate to the
  **design-system** skill first before generating screens.

### 2. Refine UI/UX Terminology

Consult [Design Mappings](references/design-mappings.md) to replace vague terms.

- Vague: "Make a nice header"
- Professional: "Sticky navigation bar with glassmorphism effect and centered
  logo"

Use [Prompting Keywords](references/prompt-keywords.md) for component names,
adjective palettes, color roles, and shape descriptions.

### 3. Structure the Final Prompt

Format the enhanced prompt for Stitch. Focus exclusively on **layout, content,
and structure** — never include colors, fonts, or theme instructions (these are
handled by the design-system skill at the project level).

```markdown
[Overall purpose and user intent of the page]

**PLATFORM:** [Web/Mobile], [Desktop/Mobile]-first

**PAGE STRUCTURE:**
1. **Header:** [Description of navigation and branding]
2. **Hero Section:** [Headline, subtext, and primary CTA]
3. **Primary Content Area:** [Detailed component breakdown]
4. **Footer:** [Links and copyright information]
```

> [!CAUTION]
> Do NOT include hex codes, font names, color palettes, roundness values, or
> any design system tokens in the generation prompt. These are applied at the
> project level by the design-system skill and will conflict if duplicated.

### 4. Present AI Insights

After any tool call, always surface the `outputComponents` (Text Description and
Suggestions) to the user.

See [examples/enhanced-prompt.md](examples/enhanced-prompt.md) for a full
before/after prompt enhancement example.

--------------------------------------------------------------------------------

## Steps

### 1. Enhance the User Prompt

Apply the Prompt Enhancement Pipeline above.

### 2. Identify the Project

Use `list_projects` to find the correct `projectId` if it is not already known.

### 3. Generate the Screen

Call the `generate_screen_from_text` tool with the enhanced prompt.

```json
{
  "projectId": "...",
  "prompt": "[Your Enhanced Prompt]",
  "deviceType": "DESKTOP"  // Options: MOBILE, DESKTOP, TABLET
}
```

### 4. Present AI Feedback

Always show the text description and suggestions from `outputComponents` to the
user.

### 5. Download Design Assets

After generation, download the HTML and screenshot urls from `outputComponents`
to the `.stitch/designs` directory.

- **Naming**: Use the screen ID or a descriptive slug for the filename.
- **Tools**: Use `curl -o` via `run_command` or similar.
- **Directory**: Ensure `.stitch/designs` exists.

### 6. Review and Refine

- If the result is not exactly as expected, use the **edit-design** skill
  to make targeted adjustments.
- Do NOT re-generate from scratch unless the fundamental layout is wrong.

--------------------------------------------------------------------------------

## 💡 Tips

- **Be structural**: Break the page down into header, hero, features, and
  footer in your prompt.
- **Content first**: Describe what each section contains (text, images, CTAs)
  rather than how it looks.
- **Iterative Polish**: Prefer editing for targeted adjustments over full
  re-generation.
- **No theme leakage**: Never put hex codes, font names, or color roles in a
  generation prompt — the design system handles all visual styling.
- **Specify interactions**: Mention hover states, animations, and click behavior
  rather than visual styling.

## 📚 References

- [Design Mappings](references/design-mappings.md) — UI/UX keywords and
  atmosphere descriptors.
- [Prompting Keywords](references/prompt-keywords.md) — Technical terms Stitch
  understands best.
- [Enhanced Prompt Example](examples/enhanced-prompt.md) — Before/after prompt
  enhancement.
