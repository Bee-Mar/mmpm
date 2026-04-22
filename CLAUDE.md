# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

MMPM (MagicMirror Package Manager) is a CLI and web-based package manager for the MagicMirror smart display project. It exposes a Python CLI, a Flask REST/WebSocket API, and an Angular 19 web UI — all three shipped together as a single PyPI package (`mmpm`).

## Dev Environment

The project uses Nix Flakes + direnv. After `direnv allow`, the shell provides wrapper scripts for all common tasks.

```bash
direnv allow       # First-time setup — loads the Nix flake environment
nix develop        # Manual alternative if not using direnv
```

## Commands

### Python backend

```bash
unit-tests          # uv run coverage run -m pytest (all tests)
static-analysis     # uv run mypy mmpm
lint                # uv run ruff check mmpm && bun --cwd=ui run lint
format              # uv run ruff format mmpm tests (+ prettier for UI)
```

Run a single test file:
```bash
uv run pytest tests/test_utils.py
uv run pytest tests/subcommands/test_install.py
```

### Angular UI (`ui/`)

```bash
cd ui
npm run start       # Dev server (ng serve)
npm run build       # Production build
npm run test        # Karma/Jasmine tests
npm run lint        # ESLint
npm run format      # Prettier
```

### Full build (Python dist + UI)

```bash
deploy              # Builds UI → copies into mmpm/ui/ → builds Python wheel/sdist
```

### Local dev process management (PM2)

The `dev/ecosystem.json` defines four concurrent processes: API server, log server, repeater, and Angular dev server.

```bash
start               # pm2 start dev/ecosystem.json
stop                # pm2 stop all
logs                # pm2 logs
```

## Architecture

### Layers

```
CLI (mmpm/entrypoint.py + mmpm/subcommands/)
        │
        ▼
Package core (mmpm/magicmirror/)   ←── also called by API
        │
        ▼
MagicMirror process / filesystem

Flask API (mmpm/api/entrypoint.py + mmpm/api/endpoints/)
        │  WebSocket (Flask-SocketIO / gevent)
        ▼
Angular UI (ui/src/app/)
```

### Python package layout

| Path | Purpose |
|---|---|
| `mmpm/subcommands/` | One file per CLI subcommand (auto-discovered) |
| `mmpm/api/endpoints/` | Flask blueprint per resource (auto-discovered) |
| `mmpm/magicmirror/` | Package, database, controller, MM integration |
| `mmpm/env.py` | `MMPMEnv` singleton — all environment variable access |
| `mmpm/utils.py` | Shared helpers |
| `mmpm/ui.py` | UI server management |
| `mmpm/wsgi.py` | WSGI entry point for gunicorn |

### Angular UI layout (`ui/src/app/`)

Components are feature-scoped under `components/`: `marketplace`, `shopping-cart`, `config-editor`, `log-stream-viewer`, `magicmirror-controller`, `custom-package-manager`, `database-info`, `package-details-viewer`.

Real-time log streaming and package operation status use Socket.IO.

### Key design patterns

- **Subcommand / endpoint auto-discovery**: both CLI subcommands and API endpoints are loaded dynamically — adding a new file in the right directory is enough to register it.
- **`MMPMEnv` singleton**: all environment/config reads go through this object; values are re-read on each access to support live UI hot-reload without restart.
- **Gunicorn + gevent**: the API server uses gevent workers to support WebSocket connections alongside regular HTTP.
- **Built UI shipped in Python package**: `ng build` output is copied into `mmpm/ui/` so the wheel is self-contained.

## Testing

Coverage is configured in `.coveragerc` to include `mmpm/**/*.py` and exclude boilerplate (`__init__.py`, constants, logger, entrypoint, wsgi).

Python tests live in `tests/` mirroring the package structure:
- `tests/magicmirror/` — package and database tests
- `tests/subcommands/` — CLI subcommand tests
- `tests/ci/` — CI-only integration tests

## Toolchain Versions

- Python: 3.10–3.14 (3.13 preferred in Nix)
- Node: 20, 22, 24
- Package managers: `uv` (Python), `bun` / `npm` (JS)
- Linters: `ruff` (Python lint+format), `mypy` (types), ESLint + Prettier (TS)
