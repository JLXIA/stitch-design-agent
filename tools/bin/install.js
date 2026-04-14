#!/usr/bin/env node

const path = require('path');
const fs = require('fs');
const os = require('os');

const HOME = os.homedir();

function parseArgs() {
  const args = process.argv.slice(2);
  let claude = false;
  let antigravity = false;
  let jetski = false;
  let gemini = false;
  let cursor = false;
  let codex = false;
  let pathArg = null;
  let help = false;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--help' || args[i] === '-h') {
      help = true;
      continue;
    }
    if (args[i] === '--claude') {
      claude = true;
      continue;
    }
    if (args[i] === '--antigravity') {
      antigravity = true;
      continue;
    }
    if (args[i] === '--jetski') {
      jetski = true;
      continue;
    }
    if (args[i] === '--gemini') {
      gemini = true;
      continue;
    }
    if (args[i] === '--cursor') {
      cursor = true;
      continue;
    }
    if (args[i] === '--codex') {
      codex = true;
      continue;
    }
    if (args[i] === '--path' && args[i + 1]) {
      pathArg = args[++i];
      continue;
    }
  }

  return { help, claude, antigravity, jetski, gemini, cursor, codex, pathArg };
}

function getTargets(opts) {
  const targets = [];
  if (opts.pathArg) {
    return [{ name: "Custom", path: path.resolve(opts.pathArg) }];
  }
  if (opts.claude) {
    targets.push({ name: "Claude Code", path: path.join(HOME, ".claude", "skills") });
  }
  if (opts.antigravity) {
    targets.push({ name: "Antigravity", path: path.join(HOME, ".gemini", "antigravity", "skills") });
  }
  if (opts.jetski) {
    targets.push({ name: "Jetski", path: path.join(HOME, ".gemini", "jetski", "skills") });
  }
  if (opts.gemini) {
    targets.push({ name: "Gemini", path: path.join(HOME, ".gemini", "skills") });
  }
  if (opts.cursor) {
    targets.push({ name: "Cursor", path: path.join(HOME, ".cursor", "skills") });
  }
  if (opts.codex) {
    targets.push({ name: "Codex", path: path.join(HOME, ".codex", "skills") });
  }
  return targets;
}

function printHelp() {
  console.log(`
Stitch Design Agent Installer

  npx github:jilinxia/stitch-design-agent [options]

Options:
  --claude       Install skills to ~/.claude/skills
  --antigravity  Install skills to ~/.gemini/antigravity/skills
  --jetski       Install skills to ~/.gemini/jetski/skills
  --gemini       Install skills to ~/.gemini/skills
  --cursor       Install skills to ~/.cursor/skills
  --codex        Install skills to ~/.codex/skills
  --path <dir>   Install skills to a custom directory
  --help, -h     Show this help message
`);
}

function copyRecursiveSync(src, dest) {
  const stats = fs.statSync(src);
  if (stats.isDirectory()) {
    if (!fs.existsSync(dest)) {
      fs.mkdirSync(dest, { recursive: true });
    }
    fs.readdirSync(src).forEach((child) => {
      copyRecursiveSync(path.join(src, child), path.join(dest, child));
    });
  } else {
    fs.copyFileSync(src, dest);
  }
}

function main() {
  console.log("Stitch Design Agent Installer started.");
  console.log("Arguments received:", process.argv.slice(2));
  
  const opts = parseArgs();
  console.log("Parsed options:", opts);
  
  if (opts.help) {
    printHelp();
    return;
  }

  const targets = getTargets(opts);
  
  if (targets.length === 0) {
    console.log("No target specified. Use --claude, --antigravity, --codex, or --path.");
    printHelp();
    return;
  }

  // Skills directory in the package
  // This script is at project_root/tools/bin/install.js
  const skillsSrc = path.resolve(__dirname, '../../skills');

  if (!fs.existsSync(skillsSrc)) {
    console.error(`Error: Skills source directory not found at ${skillsSrc}`);
    process.exit(1);
  }

  console.log(`Installing skills from: ${skillsSrc}`);

  for (const target of targets) {
    console.log(`Installing to ${target.name}: ${target.path}`);
    try {
      copyRecursiveSync(skillsSrc, target.path);
      console.log(`✓ Successfully installed to ${target.path}`);
    } catch (error) {
      console.error(`✗ Failed to install to ${target.path}: ${error.message}`);
    }
  }
}

if (require.main === module) {
  main();
}

module.exports = { main };
