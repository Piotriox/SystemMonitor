# SystemWatch

A lightweight, fast desktop system monitoring application built with Rust and Tauri.  
Monitor real-time CPU, GPU, RAM, disk, and network usage with live charts and detailed hardware information.

---

## Features

### Real-Time Monitoring
- CPU: Usage %, per-core breakdown, temperature, frequency, vendor, physical/logical cores
- GPU: Name, vendor, VRAM, driver version
- Memory: Usage %, used/total, available space, speed (MHz), RAM type
- Storage: Disk usage, type (SSD/HDD), model, file system
- Network: Download/upload rates, interface details, live chart
- Battery: Battery percentage, model and more

---

## Quick Start

### Prerequisites
- Rust 1.70+
- Node.js 18+
- npm or yarn

### Installation & Development

```bash
# Clone the repository
git clone https://github.com/yourusername/SystemWatch.git
cd SystemWatch

# Install dependencies
npm install

# Development mode (with hot reload)
npm run dev

# Build for production
npm run build

# Clean build artifacts
npm run clean
```

### Building Installers

After running `npm run build`, you'll find installers in `src-tauri/target/release/bundle/`:
- Linux: `.deb` (Ubuntu/Debian), `.AppImage` (universal)
- Windows: `.exe`, `.msi`
- macOS: `.app`, `.dmg`

---

### Stack
- Frontend: HTML5, CSS3, Vanilla JavaScript
- Backend: Rust, Tauri 2.0
- System Info: sysinfo crate
- Serialization: serde, serde_json

---

## Commands

```bash
npm run dev        # Start development server
npm run build      # Build for production
npm run tauri      # Run Tauri CLI directly
npm run clean      # Clean all build artifacts
```

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

## License

This project is licensed under the MIT License - see [LICENSE](./LICENSE) for details.

---

## Author

Piotriox - https://github.com/Piotriox
