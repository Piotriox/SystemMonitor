# Contributing to SystemWatch

Thank you for your interest in contributing to SystemWatch. We welcome all contributions, whether they're bug reports, feature requests, or code improvements.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Making Changes](#making-changes)
4. [Submitting Changes](#submitting-changes)
5. [Code Style](#code-style)
6. [Testing](#testing)

---

## Getting Started

### Prerequisites
- Rust 1.70 or later
- Node.js 18 or later
- Git

### Fork & Clone

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/SystemWatch.git
cd SystemWatch

# Add upstream remote
git remote add upstream https://github.com/Piotriox/SystemWatch.git
```

---

## Development Setup

### 1. Install Dependencies

```bash
# Install Node.js dependencies
npm install
```

### 2. Start Development Server

```bash
# Start with hot reload
npm run dev

# Or clean build first
npm run clean && npm run dev
```

### 3. Test Changes

```bash
# Run the app
npm run dev

# To test the build
npm run build
```

---

## Making Changes

### Branch Strategy

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/description-of-feature
   # or
   git checkout -b fix/description-of-bug
   ```

2. Make your changes

3. Commit with clear messages:
   ```bash
   git commit -m "feat: add GPU temperature monitoring"
   git commit -m "fix: prevent flickering in process list"
   git commit -m "docs: update README with new features"
   ```

### Commit Message Format

Use conventional commits:
- `feat:` - A new feature
- `fix:` - A bug fix
- `docs:` - Documentation only
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring without feature changes
- `perf:` - Performance improvements
- `test:` - Test additions/modifications
- `chore:` - Build, dependency updates, etc.

---

## Code Style

### Rust Backend (src-tauri/src/)

- Use `cargo fmt` for formatting:
  ```bash
  cd src-tauri
  cargo fmt
  ```

- Use `cargo clippy` for linting:
  ```bash
  cargo clippy -- -D warnings
  ```

- Follow Rust naming conventions:
  - Functions/variables: `snake_case`
  - Structs/Types: `PascalCase`
  - Constants: `SCREAMING_SNAKE_CASE`

### JavaScript Frontend (src/)

- Use 2-space indentation
- Use `const` by default, `let` only when needed
- Use template literals for strings with variables
- Add comments for complex logic
- Keep functions focused and small

---

## Testing

### Before Submitting

1. Test on clean build:
   ```bash
   npm run clean && npm run dev
   ```

2. Check for visual regressions:
   - Verify all tabs work (Resources, Processes)
   - Check real-time updates
   - Test filtering/sorting

3. Backend testing (if Rust changes):
   ```bash
   cd src-tauri
   cargo test
   ```

4. Building:
   ```bash
   npm run build
   ```

---

## Submitting Changes

### Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### Create a Pull Request

1. Go to GitHub and create a PR from your fork
2. Use a clear title: `feat: add system temperature monitoring`
3. Describe your changes in the PR description:
   - What problem does it solve?
   - How did you test it?
   - Any breaking changes?

### Code Review

- Be open to feedback
- Discuss changes if you have concerns
- Respond to review comments

---

Thank you for contributing to SystemWatch!
