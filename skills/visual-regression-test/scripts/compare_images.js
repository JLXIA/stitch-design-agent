const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function compareImages(name, livePath, extPath, outputDir) {
    console.log(`Comparing ${name}...`);
    
    if (!fs.existsSync(livePath) || !fs.existsSync(extPath)) {
        console.log(`  Error: Missing files for ${name}`);
        console.log(`  livePath: ${livePath} (${fs.existsSync(livePath)})`);
        console.log(`  extPath: ${extPath} (${fs.existsSync(extPath)})`);
        return;
    }

    const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox', '--disable-setuid-sandbox'] });
    const page = await browser.newPage();

    // Read images as base64 to inject into page
    const liveBase64 = fs.readFileSync(livePath).toString('base64');
    const extBase64 = fs.readFileSync(extPath).toString('base64');

    // We will run the comparison in the browser context via Canvas
    const result = await page.evaluate(async (liveB64, extB64) => {
        return new Promise((resolve) => {
            const img1 = new Image();
            const img2 = new Image();
            
            let loaded = 0;
            function checkLoaded() {
                loaded++;
                if (loaded === 2) {
                    compare();
                }
            }
            
            img1.onload = checkLoaded;
            img2.onload = checkLoaded;
            
            img1.src = 'data:image/png;base64,' + liveB64;
            img2.src = 'data:image/png;base64,' + extB64;
            
            function compare() {
                const width = Math.max(img1.width, img2.width);
                const height = Math.max(img1.height, img2.height);
                
                const canvas = document.createElement('canvas');
                canvas.width = width;
                canvas.height = height;
                const ctx = canvas.getContext('2d');
                
                // Fill with white first (padding)
                ctx.fillStyle = 'white';
                ctx.fillRect(0, 0, width, height);
                
                // Draw img1
                ctx.drawImage(img1, 0, 0);
                const data1 = ctx.getImageData(0, 0, width, height).data;
                
                // Clear and fill white again
                ctx.fillRect(0, 0, width, height);
                
                // Draw img2
                ctx.drawImage(img2, 0, 0);
                const data2 = ctx.getImageData(0, 0, width, height).data;
                
                // Find best vertical offset
                let bestDy = 0;
                let minDiff = Infinity;
                const maxShift = 50; // Search up to 50 pixels up and down
                
                // Simple search for best vertical offset
                for (let dy = -maxShift; dy <= maxShift; dy++) {
                    let currentDiff = 0;
                    let comparedPixels = 0;
                    
                    for (let y = 0; y < height; y++) {
                        const y2 = y + dy;
                        if (y2 < 0 || y2 >= height) continue;
                        
                        for (let x = 0; x < width; x++) {
                            const offset1 = (y * width + x) * 4;
                            const offset2 = (y2 * width + x) * 4;
                            
                            const diff = Math.abs(data1[offset1] - data2[offset2]) +
                                         Math.abs(data1[offset1+1] - data2[offset2+1]) +
                                         Math.abs(data1[offset1+2] - data2[offset2+2]);
                            
                            currentDiff += diff;
                            comparedPixels++;
                        }
                    }
                    
                    const avgDiff = currentDiff / comparedPixels;
                    if (avgDiff < minDiff) {
                        minDiff = avgDiff;
                        bestDy = dy;
                    }
                }
                
                console.log(`Best vertical offset found: ${bestDy}`);

                let diffPixels = 0;
                let sumSqDiff = 0;
                const totalPixels = width * height;
                
                // Create diff image data
                const diffCanvas = document.createElement('canvas');
                diffCanvas.width = width;
                diffCanvas.height = height;
                const diffCtx = diffCanvas.getContext('2d');
                
                // Draw img1 as background for diff
                diffCtx.drawImage(img1, 0, 0);
                const diffData = diffCtx.getImageData(0, 0, width, height);
                const dData = diffData.data;
                
                // Compare using best offset
                for (let y = 0; y < height; y++) {
                    const y2 = y + bestDy;
                    
                    for (let x = 0; x < width; x++) {
                        const offset1 = (y * width + x) * 4;
                        
                        const r1 = data1[offset1];
                        const g1 = data1[offset1+1];
                        const b1 = data1[offset1+2];
                        
                        let r2 = 255, g2 = 255, b2 = 255; // Fallback to white if out of bounds
                        
                        if (y2 >= 0 && y2 < height) {
                            const offset2 = (y2 * width + x) * 4;
                            r2 = data2[offset2];
                            g2 = data2[offset2+1];
                            b2 = data2[offset2+2];
                        }
                        
                        // Use a small tolerance (20) to ignore anti-aliasing
                        if (Math.abs(r1 - r2) > 20 || Math.abs(g1 - g2) > 20 || Math.abs(b1 - b2) > 20) {
                            diffPixels++;
                            // Highlight in red
                            dData[offset1] = 255;
                            dData[offset1+1] = 0;
                            dData[offset1+2] = 0;
                            dData[offset1+3] = 255; // opaque
                        }
                        
                        sumSqDiff += Math.pow(r1 - r2, 2) + Math.pow(g1 - g2, 2) + Math.pow(b1 - b2, 2);
                    }
                }
                
                diffCtx.putImageData(diffData, 0, 0);
                const diffBase64 = diffCanvas.toDataURL('image/png');
                
                const diffPercentage = (diffPixels / totalPixels) * 100;
                const rmse = Math.sqrt(sumSqDiff / (totalPixels * 3));
                
                resolve({
                    diffPercentage,
                    rmse,
                    width,
                    height,
                    diffBase64
                });
            }
        });
    }, liveBase64, extBase64);

    // Save diff image
    if (result.diffBase64) {
        const base64Data = result.diffBase64.replace(/^data:image\/png;base64,/, "");
        const diffPath = path.join(outputDir, `diff-${name}.png`);
        fs.writeFileSync(diffPath, Buffer.from(base64Data, 'base64'));
        console.log(`  Diff image saved to ${diffPath}`);
    }

    console.log(`  Dimensions: ${result.width}x${result.height}`);
    console.log(`  Diff Percentage: ${result.diffPercentage.toFixed(2)}%`);
    console.log(`  RMSE Score: ${result.rmse.toFixed(4)}`);
    
    if (result.rmse < 10) {
        console.log("  Conclusion: High similarity (Pass)");
    } else if (result.rmse < 30) {
        console.log("  Conclusion: Moderate differences (Review needed)");
    } else {
        console.log("  Conclusion: Significant differences (Fail)");
    }

    await browser.close();
    return result;
}

async function main() {
    const args = process.argv.slice(2);
    if (args.length < 3) {
        console.error("Usage: node compare_images.js <live_path> <ext_path> <name> [output_dir]");
        process.exit(1);
    }

    const livePath = path.resolve(args[0]);
    const extPath = path.resolve(args[1]);
    const name = args[2];
    const outputDir = args[3] ? path.resolve(args[3]) : path.dirname(livePath);

    await compareImages(name, livePath, extPath, outputDir);
}

main().catch(console.error);
