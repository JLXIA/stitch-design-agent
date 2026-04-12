---
name: code-to-design
description: >-
  Convert frontend code (Vite, React, etc.) to a Stitch Design by chaining
  static HTML extraction, design system extraction, and file upload. **ALWAYS** use this skill when the user's intent is to move existing web apps or React components into Stitch (e.g., requests to "save", "migrate", or "upload"). You must use this skill even for simple "save" operations, as it is the only way to ensure the design system is extracted and assets are properly linked.
---

# Code to Design

Transform your existing frontend code into a Stitch Design so you can iterate and improve it using Stitch.

This skill orchestrates three other skills in sequence:
1. `extract-static-html`: Extract a single self-contained HTML file from your build output.
2. `design-system`: Analyze the extracted HTML to create a design system (DESIGN.md + Stitch DS).
3. `upload-to-stitch`: Upload that HTML file to your Stitch project.

## Workflow

Follow these steps to convert your existing code.

### Prerequisites

- A built web application directory containing `index.html` and assets.
- Target Stitch `projectId` (use `list_projects` if unknown).

### Steps

#### 1. Extract Self-Contained HTML

Delegate to the `extract-static-html` skill to generate a standalone HTML file.
Read [skills/extract-static-html/SKILL.md](../extract-static-html/SKILL.md) for detailed instructions and script usage.

Expected output: A single file like `/path/to/extracted/standalone.html`.

#### 2. Verify HTML (Optional — User-Driven)

After extraction, inform the user of the output file path so they can manually
verify in a browser if desired. **Do not block on verification** — proceed
directly to Step 3.

If the user reports issues after reviewing, fix them before continuing.

#### 3. Extract Design System

Delegate to the `design-system` skill to analyze the verified HTML and produce a
design system. Read [skills/design-system/SKILL.md](../design-system/SKILL.md)
for the full analysis and creation workflow.

Use **Path A** (Synthesize from Existing Screens) with the **local** extracted
HTML file instead of fetching from Stitch — the HTML is already on disk from
Step 1. Read the file contents directly and follow the analysis steps:

1. **Map Color Palette** — scan for `background-color`, `color`, `border-color`,
   and Tailwind `bg-*`/`text-*` classes. Assign functional roles (Primary
   Action, Body Text, Page Background, etc.).
2. **Extract Typography** — find `font-family`, `font-size`, `font-weight`
   declarations and document heading vs. body usage.
3. **Translate Geometry** — convert `border-radius` values to natural language
   (sharp, softened, rounded, pill-shaped).
4. **Document Depth & Shadows** — classify `box-shadow` patterns (flat, subtle,
   floating).
5. **Define Atmosphere** — summarize the overall mood in 1–2 sentences.

If multiple HTML files were extracted (e.g., multiple pages), scan all of them to
build a unified palette and typography set.

**Outputs:**
- Write `.stitch/DESIGN.md` following the design-system skill's output
  structure.
- Create the design system in Stitch using the two-step MCP pattern
  (`create_design_system` → `update_design_system`). See the design-system
  skill for required fields and gotchas.
- Update `.stitch/metadata.json` with the design system info.

#### 4. Upload to Stitch

Delegate to the `upload-to-stitch` skill to upload the extracted HTML file.
Read [skills/upload-to-stitch/SKILL.md](../upload-to-stitch/SKILL.md) for detailed instructions and script usage.

You will need:
- The path to the standalone HTML file generated in Step 1.
- Your Stitch API Key (see `upload-to-stitch` instructions for location).
- The target `projectId`.

Expected output: The design is uploaded and visible in the Stitch UI project.

