---
name: edit-design
description: >-
  Edit existing screens using Stitch MCP. Includes targeted prompt formulation,
  asset download, and metadata tracking.
---

# Edit-Design

Make targeted changes to an already generated design.

> [!NOTE]
> Refer to your system prompt for instruction on handling MCP tool prefixes for
> all tools mentioned in this skill (e.g., `list_projects`, `list_screens`,
> `edit_screens`).

## Steps

### 1. Identify the Screen

Use `list_screens` or `get_screen` to find the correct `projectId` and
`screenId`.

### 2. Formulate the Edit Prompt

Be specific about the changes you want to make. Do not just say "fix it".

- **Location**: "Change the color of the [primary button] in the [hero section]..."
- **Visuals**: "...to a darker blue (#004080) and add a subtle shadow."
- **Structure**: "Add a secondary button next to the primary one with the text 'Learn More'."

### 3. Apply the Edit

Call the `edit_screens` tool.

```json
{
  "projectId": "...",
  "selectedScreenIds": ["..."],
  "prompt": "[Your targeted edit prompt]"
}
```

### 4. Present AI Feedback

Always show the text description and suggestions from `outputComponents` to the
user.

### 5. Download Design Assets

After editing, download the updated HTML and screenshot urls from
`outputComponents` to the `.stitch/designs` directory, overwriting previous
versions to ensure the local files reflect the latest edits.

- **Naming**: Use the screen ID or a descriptive slug for the filename.
- **Tools**: Use `curl -o` via `run_command` or similar.
- **Directory**: Ensure `.stitch/designs` exists.

### 6. Update Project Metadata

After downloading assets, update `.stitch/metadata.json` to reflect any changes
(e.g., updated screen titles or new screen IDs from the edit). The metadata
file tracks all screens, their device types, and design system info. See the
**design-system** skill's `examples/metadata.json` for the format.

### 7. Verify and Repeat

- Check the output screen to see if the changes were applied correctly.
- If more polish is needed, repeat the process with a new specific prompt.

## 💡 Tips

- **Keep it focused**: One edit at a time is often better than a long list of
  changes.
- **Reference components**: Use professional terms like "navigation bar", "hero
  section", "footer", "card grid".
- **Mention colors**: Use hex codes for precise color matching.
