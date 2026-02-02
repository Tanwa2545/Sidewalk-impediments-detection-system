const fs = require('fs');
const path = require('path');

const CSV_PATH = path.join(__dirname, '../../final_safety_report.csv');
console.log('Checking CSV Path:', CSV_PATH);
console.log('Exists:', fs.existsSync(CSV_PATH));

if (fs.existsSync(CSV_PATH)) {
    const content = fs.readFileSync(CSV_PATH, 'utf8');
    console.log('Content Length:', content.length);
    console.log('First 100 chars:', content.substring(0, 100));
}

const PUBLIC_IMAGES_PATH = path.join(__dirname, '../public/marker-images');
console.log('Checking Public Path:', PUBLIC_IMAGES_PATH);
try {
    fs.mkdirSync(PUBLIC_IMAGES_PATH, { recursive: true });
    console.log('Mkdir success');
} catch (e) {
    console.log('Mkdir error:', e.message);
}
