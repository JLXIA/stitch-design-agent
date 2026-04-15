const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function main() {
    const args = process.argv.slice(2);
    if (args.length < 2) {
        console.error("Usage: node capture_screenshot.js <url_or_file_path> <output_path> [width] [height] [html_output_path]");
        process.exit(1);
    }

    const urlOrPath = args[0];
    const outputPath = path.resolve(args[1]);
    const width = parseInt(args[2]) || 1280;
    const height = parseInt(args[3]); // Optional
    const htmlOutputPath = args[4] ? path.resolve(args[4]) : null; // Optional

    let url = urlOrPath;
    if (!url.startsWith('http://') && !url.startsWith('https://') && !url.startsWith('file://')) {
        url = 'file://' + path.resolve(urlOrPath);
    }

    console.log(`Capturing ${url}...`);
    
    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    
    let useFullPage = !height;
    
    if (height) {
        console.log(`Setting fixed viewport: ${width}x${height}`);
        await page.setViewport({ width, height });
    } else {
        console.log(`Setting default viewport width: ${width}`);
        await page.setViewport({ width, height: 800 }); // Default height for initial load
    }
    
    try {
        await page.goto(url, { waitUntil: 'networkidle0', timeout: 30000 });
        
        // Wait a bit for any rendering
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        if (!height) {
            const fullHeight = await page.evaluate(() => document.documentElement.scrollHeight);
            console.log(`Resizing viewport to full height: ${width}x${fullHeight}`);
            await page.setViewport({ width, height: fullHeight });
            useFullPage = false; // We are now full page size, so no need for fullPage: true
        }
        
        await page.screenshot({ path: outputPath, fullPage: useFullPage });
        console.log(`Screenshot saved to ${outputPath}`);

        if (htmlOutputPath) {
            const html = await page.evaluate(() => document.documentElement.outerHTML);
            const htmlOutputDir = path.dirname(htmlOutputPath);
            if (!fs.existsSync(htmlOutputDir)) {
                fs.mkdirSync(htmlOutputDir, { recursive: true });
            }
            fs.writeFileSync(htmlOutputPath, html);
            console.log(`HTML saved to ${htmlOutputPath}`);
        }
    } catch (error) {
        console.error(`Error capturing screenshot: ${error.message}`);
    } finally {
        await browser.close();
    }
}

main().catch(console.error);
