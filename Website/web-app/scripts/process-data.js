const fs = require('fs');
const path = require('path');
const Papa = require('papaparse');

const CSV_PATH = path.join(__dirname, '../../final_safety_report_wlinks.csv');
// const IMAGES_BASE_PATH = path.join(__dirname, '../../annotated_streetview_images'); // No longer needed
// const PUBLIC_IMAGES_PATH = path.join(__dirname, '../public/marker-images'); // No longer needed
const OUTPUT_JSON_PATH = path.join(__dirname, '../src/data/markers.json');

// Ensure output directories exist
if (!fs.existsSync(path.dirname(OUTPUT_JSON_PATH))) {
    fs.mkdirSync(path.dirname(OUTPUT_JSON_PATH), { recursive: true });
}

const processData = () => {
    try {
        const fileContent = fs.readFileSync(CSV_PATH, 'utf8');
        
        Papa.parse(fileContent, {
            header: true,
            skipEmptyLines: true,
            complete: (results) => {
                const markers = [];
                let processedCount = 0;

                console.log(`Total rows found: ${results.data.length}`);
                if (results.data.length > 0) {
                    console.log('Sample Row 1:', results.data[0]);
                }

                results.data.forEach((row, index) => {
                    const status = row.status?.trim().toUpperCase();
                    if (index < 5) console.log(`Row ${index} status: '${status}'`); // Debug first few rows

                    
                    // Filter for WARNING or CRITICAL
                    if (status === 'WARNING' || status === 'CRITICAL') {
                        // const folder = row.folder?.trim();
                        const filename = row.file?.trim();
                        const imageUrl = row.image_url?.trim();
                        
                        if (!filename || !imageUrl) return;

                        // Parse Filename for Metadata
                        // Format: lat_long_panoID_heading_date.jpg
                        // 13.786769_100.607857_DLyAuLMD5nTahA3lRDxPTw_211_2025-10.jpg
                        const nameParts = filename.replace('.jpg', '').split('_');
                        if (nameParts.length >= 5) {
                            const lat = nameParts[0];
                            const lng = nameParts[1];
                            
                            // Date is always last
                            const dateStr = nameParts[nameParts.length - 1];
                            // Heading is always second to last
                            const heading = nameParts[nameParts.length - 2];
                            
                            // PanoID is everything in between
                            // Slice from index 2 to length-2
                            const panoId = nameParts.slice(2, nameParts.length - 2).join('_');

                            // Date Logic
                            const photoDate = new Date(dateStr);
                            const oneYearAgo = new Date();
                            oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);
                            
                            const isOld = photoDate < oneYearAgo;
                            const dateNote = isOld 
                                ? `Note: Data matches image taken on ${dateStr} (older than 1 year)` 
                                : `Image Date: ${dateStr}`;

                            markers.push({
                                id: panoId, // unique per pano
                                lat: parseFloat(lat),
                                lng: parseFloat(lng),
                                type: row.problem_type,
                                severity: status, // WARNING, CRITICAL
                                description: `Detected ${row.problem_type} (${status}).`,
                                image: imageUrl, // Use Firebase URL directly
                                panoId: panoId,
                                heading: parseInt(heading),
                                date: dateStr,
                                dateNote: dateNote,
                                raw: {
                                    total_blocked_pct: row.total_blocked_pct,
                                    obstacle_pct: row.obstacle_pct,
                                    damage_pct: row.damage_pct
                                }
                            });
                            processedCount++;
                        }
                    }
                });

                // Write JSON
                fs.writeFileSync(OUTPUT_JSON_PATH, JSON.stringify(markers, null, 2));
                console.log(`Processing Complete.`);
                console.log(`Generated ${markers.length} markers.`);
                console.log(`Processed with image verification: ${processedCount}`);
            }
        });
    } catch (error) {
        console.error('Error processing data:', error);
    }
};

processData();
