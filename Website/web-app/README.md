# Safety Map Web App

This is a Next.js application showing safety issues on a map with interactive filters and district highlighting.

## Prerequisites

- **Node.js**: You need Node.js installed on the target machine. (Version 18+ recommended).
  - Download from: [nodejs.org](https://nodejs.org/)

## Installation

1.  **Copy the project files** to the new device.
2.  Open a terminal/command prompt in the `web-app` directory.
3.  **Install dependencies**:
    ```bash
    npm install
    ```
    This command reads `package.json` and installs all necessary libraries (Leaflet, React, Next.js, etc.).

## Data Setup (Important)

Before running the website, you must process the raw CSV data into the format the app uses.

1.  Ensure you have the `final_safety_report.csv` and `annotated_streetview_images/` folder in the parent directory (one level up from `web-app`).
2.  Run the processing script:
    ```bash
    node scripts/process-data.js
    ```
    *This will generate `src/data/markers.json` and populate `public/marker-images/`.*

## Running the App

### Development Mode
To run the app locally with hot-reloading:
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

### Production Build
To create an optimized build for deployment:
```bash
npm run build
npm start
```
