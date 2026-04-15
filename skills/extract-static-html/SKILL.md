---
name: stitch::extract-static-html
description: >-
  Extract self-contained static HTML from a built web application or React components by inlining CSS and images. Use this skill whenever you need to capture a specific UI state, share a static version of a page, or prepare assets for Stitch upload, even if the user just asks to 'save the HTML' or 'mock the view'.
---

# Extract Static HTML

This skill allows you to extract a self-contained static HTML file from a web application. It supports two strategies:
- **Strategy A (Static)**: Converts JSX/React files to HTML statically using a Python script.
- **Strategy B (Dynamic)**: Runs the app locally and captures the rendered DOM from a browser.

## Which Strategy to Use

Work through these checks in order — the first "no" sends you to Strategy A:

1. **Do you have browser automation with JS execution?** If no → **Strategy A**.
2. **Can the app run locally** (dependencies installed, dev server starts)? If no → **Strategy A**.
3. **Do you need a specific UI state** that's hard to reach without mocking (e.g., error screens, empty states)? If yes → **Strategy A** (you control the state explicitly in the mock).
4. Otherwise → **Strategy B** (highest fidelity with the least manual effort).

| | Strategy A (Static) | Strategy B (Dynamic) |
| :--- | :--- | :--- |
| **Speed** | Fast — no server needed | Slower — requires server spin-up |
| **Fidelity** | May miss dynamic data/styles | Captures exactly what is rendered |
| **Setup** | Manual mock often required | Zero mock effort |
| **State control** | Explicit — you choose | Depends on app's default state |

***

## Strategy A: Static Extraction (JSX to HTML Script)

This method relies on the `extract_inline_html.py` script to process the HTML and inline assets.

### Workflow

Follow these steps to generate a single, self-contained HTML file from a built web application.

#### Prerequisites

- You must have the output directory of the built web app containing `index.html` and its assets (CSS, JS, images).

Use the Python script to convert JSX directly to HTML. If the page uses custom components, create a flattened mock file first.

*   **Usage**:
    1.  **Preparation (For Complex Pages Only)**: If the page imports custom React components, create a temporary `MockPage.jsx` that inlines the rendered output of those components, resolves dynamic data, and replaces icons with placeholders.

        ##### Including the Full Page Layout

        Most React apps wrap every page in a shared shell — typically defined in `App.js` or a layout component — that includes a **header/navigation bar** at the top and a **footer** at the bottom. The extraction script only sees what you put in the mock file, so if you omit these shared components the extracted HTML will be missing the nav and footer.

        > [!CAUTION]
        > **ALWAYS** check the app's root component (usually `App.js` or `App.tsx`) to identify shared layout wrappers before building any mock file. Your mock must reproduce the **full visible page** as the user would see it in a browser, not just the route-specific content.

        Follow this checklist for every mock file:

        1. **Read `App.js`** (or the root layout) and identify which components wrap every route (e.g., `<AppHeader />`, `<AppFooter />`, `<Sidebar />`).
        2. **Read each wrapper component** and flatten it into static HTML the same way you flatten page content — resolve conditional rendering, replace `<Link>` with `<a>`, replace icons with emoji or SVG placeholders, and hardcode any dynamic values.
        3. **Preserve Logos and Branding**: Do NOT replace logos with text placeholders. If the logo is an image (SVG, PNG, etc.), use an `<img>` tag with the correct local path (e.g., `src/images/logo.svg`) so that the post-processing script can inline it later.
        4. **Assemble the mock** in this order:
           - Outermost layout `<div>` with background/theme classes from the root component
           - Flattened header / navigation bar
           - Page-specific content
           - Flattened footer
        5. **Verify** that the mock's structure matches what a user would see at the corresponding route in a browser. If the app has a sidebar layout, include the sidebar too.

        ##### Handling Conditional Rendering / UI State

        The extraction script converts JSX **statically** — it does not execute React code. This means conditional expressions like `{isOpen ? <ComponentA /> : <ComponentB />}` are NOT evaluated. The mock file must contain only the **concrete HTML for the desired state**, with all conditional logic removed.

        When building the mock, follow these steps:

        1. **Identify conditional branches** in the source code by searching for `useState`, ternary operators (`? :`), and `&&` guards that control which UI is rendered.
        2. **Choose the correct state to capture**:
           - If the user provided a **reference screenshot**, match that state exactly.
           - If no reference is given, choose the state that shows the **most complete and visually rich UI** (e.g., prefer a PromptBuilder with dropdowns over a plain textarea, prefer a populated dashboard over an empty state).
        3. **Flatten the chosen branch only** — copy the JSX from the winning branch into the mock and delete the conditional wrapper entirely. Do NOT include both branches or any `{condition ? ... : ...}` expressions.
        4. **Remove all dynamic expressions** — replace `{variable}` with hardcoded values, remove `.map()` loops by duplicating the inner JSX with concrete data, and remove event handlers.
        5. For components with **multiple meaningful states** (e.g., a free-text mode vs. a structured builder), consider extracting each state as a separate HTML file if the user needs both.

        > [!WARNING]
        > Never include fake data that doesn't exist in the initial app state. For example, don't add a "Songs Gallery" section with mock results if the app starts with an empty results array. Only include UI that actually appears in the chosen state.

        ##### Excluding Floating/Interactive Elements

        Extracted static HTML is often used for visual comparison or design review. Floating interactive elements like AI assistants, chat widgets, cookie banners, and feedback buttons can obscure the main content and cause false positives in visual regression tests if they render dynamically.

        When building the mock file:
        1. **Identify floating elements**: Look for fixed-position elements (e.g., classes like `fixed`, `bottom-8`, `right-8`, `z-50`).
        2. **Remove them from the mock**: If an element is an interactive overlay that is not part of the core page design being evaluated, delete its JSX from the mock file entirely.
        3. **Keep layout essentials**: Do not remove fixed elements that are part of the essential page layout, such as fixed headers or sidebars.

    2.  **Run Extraction Script**:
        ```bash
        python3 .agents/plugins/stitch/skills/extract-static-html/scripts/extract_inline_html.py \
          --tailwind-config tailwind.config.js \
          --index-css src/css/App.css \
          --extra-css index.html \
          --outdir .stitch \
          --page src/MockPage.jsx:Page.html:"Page Title"
        ```

        **Script flags**:
        - `--tailwind-config`: Path to `tailwind.config.js` (auto-converts `export default` and `module.exports` to browser-compatible `tailwind.config = `, and removes Node-style `require('tailwindcss/colors')` lines that fail in the browser).
        - `--index-css`: Path to the app's main CSS file. `@import` statements are converted to `<link>` tags; `@tailwind` directives are stripped.
        - `--extra-css`: **(Recommended)** Path to the app's `index.html` to extract custom `<style>` blocks (e.g., custom gradients, scrollbar styles, glass effects) and font `<link>` tags (e.g., Google Fonts). Many apps define critical styling here that won't be captured otherwise.
        - `--outdir`: Output directory (default: `.stitch`).
        - `--page`: One or more page specs in `src_file:dst_filename:title` format.

        **Automatic JSX-to-HTML fixes** (handled by the script):
        - `className=` → `class=`
        - `style={{...}}` → `style="..."`
        - Self-closing non-void tags (`<textarea />`, `<div />`) → properly closed (`<textarea></textarea>`, `<div></div>`)
        - React attributes (`defaultValue` → `value`, `htmlFor` → `for`)
        - `<Link to="...">` → `<div>`
        - SVG attribute names (`strokeLinecap` → `stroke-linecap`, etc.)

    3.  **Post-Process (If needed)**: The extraction script only embeds `http` URLs. If you used local paths for images in the mock JSX (e.g., `src/assets/...`), they will be left as local paths. Run the post-processing script to inline them as base64:
        ```bash
        python3 .agents/plugins/stitch/skills/extract-static-html/scripts/post_process.py \
          .stitch/Page1.html .stitch/Page2.html \
          --base-dir <app-directory>
        ```

        **Script flags**:
        - Positional args: one or more HTML files to process.
        - `--base-dir`: The app's root directory, used to resolve image paths. For example, if the HTML contains `src="src/images/logo.svg"` and the actual file is at `my-app/src/images/logo.svg`, pass `--base-dir my-app`. The script tries the path as-is first, then with `base-dir` prepended.

    4.  **Handling Local Fonts (Critical for Fidelity)**:
        If the application uses local fonts defined in CSS with relative paths (e.g., `url('../fonts/...')`), these paths will break when the generated HTML is placed in a subdirectory like `.stitch/`.
        
        > [!WARNING]
        > Missing fonts will cause the browser to fall back to default fonts, leading to text wrapping differences and compounding layout shifts in visual regression tests.
        
        To fix this:
        - Identify the font directory in the source (e.g., `src/fonts`).
        - Copy the fonts directory to a location where the relative paths in the inlined CSS will resolve correctly from the output directory. For example, if the HTML is in `.stitch/` and CSS expects `../fonts/`, copy the fonts to `fonts/` in the project root.
        - Example command: `mkdir -p fonts && cp -r src/fonts/* fonts/`

    5.  **Cleanup**: Delete the temporary `MockPage.jsx` file after generation.

## Strategy B: Dynamic Extraction (Browser-based Capture)

This method is preferred when the application requires a complex environment to render or when visual fidelity to the live state is critical. See the **Choice Decision** section above for prerequisites.

### Workflow

1.  **Start the App**: Run the development server locally in the workspace (e.g., `npm run dev`). Ensure it is running and note the assigned port.
2.  **Navigate**: Use a browser automation subagent to open the application URL (e.g., `http://localhost:5173`).
3.  **Wait for Render**: Allow time for the page to fully load and for all React components to mount and render their data.
4.  **Extract DOM**: Execute `document.documentElement.outerHTML` in the browser to capture the fully rendered DOM.
    
    > [!WARNING]
    > **Large pages may cause the browser subagent to truncate its report** due to file size limits (especially from injected styles).
    > To handle this:
    > - **Instruct the subagent explicitly** in your prompt not to truncate output for readability.
    > - **Hybrid Fallback**: If content is still too large, run JS in the browser to remove `<style>` tags before extraction (e.g., `document.querySelectorAll('style').forEach(el => el.remove());`). You must then re-add the styles statically in your parent context (e.g., adding links to Tailwind CDN or reading source CSS).
5.  **Save to File**: Save the captured HTML string to a target file (e.g., in a project `.stitch` folder or as requested by the user).
6.  **Stop Server**: Terminate the server task once extraction is verified.

