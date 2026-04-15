---
name: visual-regression-test
description: Compare two images (e.g., live screenshot vs extracted HTML screenshot) to perform visual regression testing. It calculates pixel diff percentage and RMSE score, and generates a diff image highlighting differences. Make sure to use this skill whenever the user asks to evaluate the quality of extracted HTML, compare screenshots, or verify UI fidelity.
---

# Image Comparison Skill

This skill enables Claude to perform pixel-level comparison between two images, typically used for visual regression testing to compare a live application view against an extracted static HTML view.

## When to Use

Use this skill when:
- The user wants to evaluate the quality or fidelity of extracted HTML.
- The user wants to compare two screenshots for visual differences.
- You need to verify that a UI extraction or generation matches the reference design.

## Prerequisites

- Node.js installed.
- Puppeteer installed in the project or accessible globally.

## How to Use

The skill bundles a script `scripts/compare_images.js` that uses Puppeteer and HTML Canvas to perform the comparison.

### Step 1: Prepare Images

Ensure you have the two images you want to compare saved on disk:
1.  **Reference Image**: The original or "live" screenshot.
2.  **Test Image**: The extracted or generated screenshot.

> [!TIP]
> **Convention for file organization**: Always save the screenshots (reference and test) in the same directory as the target HTML file (e.g., in `.stitch_dynamic/` or `.stitch/`). This keeps all assets for an extraction organized, and the diff script will automatically output the diff image to that same folder.


#### Optional: Capturing Screenshot with Puppeteer
If you need to capture the screenshot from an extracted HTML file, use the bundled `capture_screenshot.js` script. This helps capture full-page content correctly, avoiding truncation issues often encountered with browser subagents.

```bash
node path/to/skill/scripts/capture_screenshot.js <url_or_file_path> <output_path> [width] [height]
```

**Example:**
```bash
node .agents/skills/visual-regression-test/scripts/capture_screenshot.js ./extracted_html/tracker.html ./extracted_html/extracted-tracker.png 1280 1104
```
*   If `height` is specified, it captures only that viewport.
*   If `height` is omitted, it captures the full page.


### Step 2: Run the Comparison

Run the bundled script using `node`. You need to pass the paths to the images and a name for the test.

```bash
node path/to/skill/scripts/compare_images.js <path_to_reference_image> <path_to_test_image> <test_name>
```

**Example:**
```bash
node /Users/jilinxia/.gemini/jetski/skills/image-comparison/scripts/compare_images.js ./screenshots/live_home.png ./screenshots/extracted_home.png home
```

### Step 3: Interpret Results

The script will output:
- **Diff Percentage**: The percentage of pixels that differ significantly.
- **RMSE Score**: Root Mean Square Error. Lower is better.
- **Conclusion**:
    - **RMSE < 10**: High similarity (Pass)
    - **10 <= RMSE < 30**: Moderate differences (Review needed)
    - **RMSE >= 30**: Significant differences (Fail)

It will also save a diff image named `diff-<test_name>.png` in the same directory as the reference image, with differences highlighted in red.

## Output Format

When answering the user, summarize the results in a table:

| State | Diff Percentage | RMSE Score | Conclusion |
| :--- | :--- | :--- | :--- |
| [Name] | [X.XX]% | [Y.YYYY] | [Pass/Review/Fail] |

Provide links to the diff images for the user to inspect.
