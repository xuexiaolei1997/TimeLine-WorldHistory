const fs = require('fs');
const path = require('path');

function deletePycache(dir) {
    if (!fs.existsSync(dir)) return;

    fs.readdirSync(dir).forEach(file => {
        const fullPath = path.join(dir, file);
        const stat = fs.statSync(fullPath);

        if (stat.isDirectory()) {
            if (file === '__pycache__') {
                fs.rmSync(fullPath, { recursive: true, force: true });
                console.log(`Removed: ${fullPath}`);
            } else {
                deletePycache(fullPath);
            }
        }
    });
}

// Clear Python cache
console.log('Clearing Python cache...');
deletePycache(path.join(__dirname, '..', 'backend'));

// Clear React build cache
const buildDir = path.join(__dirname, '..', 'build');
if (fs.existsSync(buildDir)) {
    fs.rmSync(buildDir, { recursive: true, force: true });
    console.log('Cleared React build directory');
}

// Clear node_modules/.cache
const nodeCacheDir = path.join(__dirname, '..', 'node_modules', '.cache');
if (fs.existsSync(nodeCacheDir)) {
    fs.rmSync(nodeCacheDir, { recursive: true, force: true });
    console.log('Cleared node_modules/.cache');
}

console.log('Cache clearing completed!');