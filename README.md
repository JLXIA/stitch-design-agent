# Stitch Design Agent Plugin

Stitch agents and skills that enable AI assistants to design and build modern user interfaces.

## Features

### Skills
This plugin installs several skills to assist with design tasks:

*   **text-to-design**: Generate high-fidelity user interfaces directly from natural language text descriptions.
*   **code-to-design**: Assist in converting existing code structures or component lists into design representations.
*   **design-md**: Manage and maintain `DESIGN.md` files as the single source of truth for project design.
*   **design-system**: Extract and manage consistent design tokens, color palettes, and typography systems.
*   **edit-design**: Modify and refine screens directly within the Stitch platform using automated commands.
*   **extract-static-html**: Capture high-fidelity static HTML and screenshots for visual regression testing.
*   **upload-to-stitch**: Upload generated assets, screens, and design files to your Stitch project.


## Installation

```bash
npx skills add JLXIA/stitch-design-agent
```

## Usage

Once the skills are installed, you can invoke them using your agent's command interface or by referencing them in your prompts.

Example usage in a prompt:
> "Use the `stitch::text-to-design` skill to create a login page for a mobile app."

For specific skill documentation, refer to the `SKILL.md` file in each skill's directory within `skills/`.

## License
This project is licensed under the terms specified in the `plugin.json` or standard repository license.