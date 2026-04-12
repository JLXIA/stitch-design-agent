---
name: design-system
description: >-
  Manage design systems in Stitch using MCP tools. Includes retrieval of assets,
  creating/updating design systems in Stitch, and applying them to screens.
---

# Design-System

Create a "source of truth" for your project's design language to ensure
consistency across all future screens.

> [!NOTE]
> Refer to your system prompt for instruction on handling MCP tool prefixes for
> all tools mentioned in this skill (e.g., `get_screen`, `create_design_system`,
> `update_design_system`, `apply_design_system`).

## 📥 Retrieval

To analyze a Stitch project, you must retrieve metadata and assets using the
Stitch MCP tools:

1. **Project lookup**: Use `list_projects` to find the target `projectId`.
2. **Screen lookup**: Use `list_screens` for that `projectId` to find
   representative screens (e.g., "Home", "Main Dashboard").
3. **Metadata fetch**: Call `get_screen` for the target screen to get
   `screenshot.downloadUrl` and `htmlCode.downloadUrl`.
4. **Asset download**: Use `read_url_content` to fetch the HTML code.

## 🧠 Synthesis from Description

If you need to extract a design system from existing screens, use the `design-md` skill.

If there are no existing screens (new project), or the user provides a direct description (e.g., "dark theme, blue and purple, rounded, Inter font"):

1. Map the user's vague terms to precise values using the design mappings (see `design-md` skill or text-to-design skill).
2. Select concrete hex codes, font families, and roundness values.
3. Generate the `DESIGN.md` file (refer to `design-md` for structure).
4. Proceed to the "Create or Update Design System in Stitch" step below.

## 📝 Output Structure

The `DESIGN.md` file should follow the structure defined in the `design-md` skill.

## 🚀 Create or Update Design System in Stitch

After generating `.stitch/DESIGN.md`, make sure to also create or update the
design system in Stitch using MCP tools.

**Two-step design system creation:**

Read [reference/tool-schema.md](reference/tool-schema.md) for the exact call
formats before making these calls.

1. Call `create_design_system` with **only `displayName`** — no theme fields.
   This creates the asset shell and returns the asset ID.
2. Immediately call `update_design_system` with the `designMd` field set to
   the full DESIGN.md content. Use the returned asset ID as the `name`
   (format: `assets/{asset_id}`).

> [!IMPORTANT]
> When calling `update_design_system`, you must provide the required theme fields (`colorMode`, `headlineFont`, `bodyFont`, `roundness`, `customColor`) in addition to `designMd`, following the schema defined in `reference/tool-schema.md`.

Once both `create_design_system` and `update_design_system` have been called,
Stitch holds the design tokens at the project level — you do NOT need to repeat
them in generation prompts.

## 🎨 Apply Design System to Screens

Use `apply_design_system` to apply a design system to existing screens.

> [!IMPORTANT]
> `selectedScreenInstances` must contain **only** `id` and `sourceScreen` — do
> NOT include position/dimension fields (`x`, `y`, `width`, `height`) or the
> request will fail with "invalid argument". Get the screen instance IDs from
> `get_project`.

```json
{
  "projectId": "...",
  "assetId": "...",
  "selectedScreenInstances": [
    {
      "id": "...",
      "sourceScreen": "projects/.../screens/..."
    }
  ]
}
```

**How to get the required IDs:**
1. Call `get_project` to retrieve `screenInstances` — each has an `id` and
   `sourceScreen`.
2. Call `list_design_systems` to retrieve the design system `name` (format:
   `assets/{assetId}`) — use the part after `assets/` as the `assetId`.
3. Filter out any instances with `type: "DESIGN_SYSTEM_INSTANCE"` — only pass
   real screens.

## 📋 Update Project Metadata

After writing `.stitch/DESIGN.md`, also create or update `.stitch/metadata.json`
to track the `projectId`, `title`, all known screens, and design system summary.
See [examples/metadata.json](examples/metadata.json) for the format.

## Schema Reference

See [reference/tool-schema.md](reference/tool-schema.md) for the full
`designSystem` object schema with all available options.

## 💡 Best Practices

Refer to the `design-md` skill for best practices on describing design elements.
