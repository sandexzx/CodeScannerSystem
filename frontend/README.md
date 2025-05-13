# DataMatrix Scanner

A modern Electron-based interface for scanning and managing DataMatrix codes.

## Features

- Scan and display DataMatrix codes in real-time
- Track scanning sessions with box capacity limits
- View scan history with timestamps
- Clean, responsive UI with Apple-inspired design
- Cross-platform support (Windows, macOS, Linux)

## Getting Started

### Prerequisites

- Node.js (v16 or later)
- npm or yarn

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   cd CodeScannerFrontend
   npm install
   ```

### Development

To run the app in development mode:

```bash
npm run electron:dev
```

This will start the Vite dev server and Electron app simultaneously.

### Building for Production

To create a production build:

```bash
# Create a production build
npm run build

# Package the app
npm run electron:build
```

The packaged app will be available in the `dist` directory.

## Usage

1. Start a new scanning session by clicking "Start New Session"
2. Scan DataMatrix codes using a barcode scanner or enter them manually
3. View scanned items in the History tab
4. Configure box capacity in the Settings tab
5. Complete the session when done

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
