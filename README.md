# Stitch Design Agent Plugin

Stitch agents and skills that enable AI assistants to design and build modern user interfaces.

## Features

### Skills
This plugin installs several skills to assist with design tasks:
- **text-to-design**: Generate user interfaces from text descriptions.
- **code-to-design**: Assist in converting code structures to design representations.
- **design-md**: Manage and maintain `DESIGN.md` files as the source of truth.
- **design-system**: Extract and manage design tokens and systems.
- **edit-design**: Modify and refine screens directly within the Stitch platform.
- **extract-static-html**: Capture high-fidelity static HTML for visual regression testing.
- **upload-to-stitch**: Upload assets and screens to the Stitch project.

## Installation

Choose the instructions below based on the agent platform you are using.

### 1. Jetski
For environments using the Jetski agent framework, copy the skills and agents directly into your application data directory.

```bash
# Clone the repository
git clone https://github.com/jilinxia/stitch-design-agent.git

# Copy skills to the Jetski skills directory
cp -r stitch-design-agent/skills/* ~/.gemini/jetski/skills/

# Copy agents to the Jetski agents directory
cp -r stitch-design-agent/agents/* ~/.gemini/jetski/agents/
```

### 2. Gemini CLI
If you are using the Gemini CLI, you can install the skills directly from the repository or from a local clone.

**From the Repository:**
```bash
gemini skills install https://github.com/jilinxia/stitch-design-agent.git --path skills
```

**From a Local Clone:**
```bash
git clone https://github.com/jilinxia/stitch-design-agent.git
gemini skills install ./stitch-design-agent/skills/
```

### 3. Claude Code

For Claude Code, users can install and use these skills in several ways:

#### Method A: Using npx (Easiest)
You can use `npx` pointing directly to the GitHub repository to install the skills into your agent's directory. Flags `--claude`, `--antigravity`, and `--codex` are supported:

```bash
# Install skills for Claude Code
npx github:jilinxia/stitch-design-agent --claude

# Install skills for Antigravity
npx github:jilinxia/stitch-design-agent --antigravity

# Install skills for Jetski
npx github:jilinxia/stitch-design-agent --jetski

# Install skills for Gemini CLI
npx github:jilinxia/stitch-design-agent --gemini

# Install skills for Cursor
npx github:jilinxia/stitch-design-agent --cursor

# Install skills for Codex
npx github:jilinxia/stitch-design-agent --codex
```

#### Method B: Manual Installation
Users can clone the repository and reference the skills directory when starting Claude Code.

```bash
# Clone the repository
git clone https://github.com/jilinxia/stitch-design-agent.git

# Run Claude Code with the skills directory
claude --plugin-dir ./stitch-design-agent/skills
```

#### Method C: Marketplace Installation (Experimental)
If you are using a plugin manager that supports the `/plugin` commands (like [Addy Osmani's agent-skills](https://github.com/addyosmani/agent-skills)), you can add this repository as a source:

```bash
# Add the repository to your marketplace sources
/plugin marketplace add jilinxia/stitch-design-agent

# Install the skills
/plugin install stitch-design-agent
```

### 4. Cursor
For Cursor, you can make these skills available by adding them to your custom rules.

```bash
# Clone the repository
git clone https://github.com/jilinxia/stitch-design-agent.git

# Copy relevant SKILL.md files to your project's cursor rules
# Example:
cp stitch-design-agent/skills/design-md/SKILL.md .cursor/rules/design-md.md
```

## License
This project is licensed under the terms specified in the `plugin.json` or standard repository license.
