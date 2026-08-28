# Contributing to NLAMS

Thank you for considering contributing to the National Land Acquisition & Management System!

## Local Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 15 with PostGIS extension
- Docker & Docker Compose (recommended)

### Quick Start
```bash
# Clone the repo
git clone https://github.com/your-org/nlams.git
cd nlams

# Start with Docker Compose (recommended)
docker-compose up --build

# Or set up manually:
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
python -m app.seed
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Running Tests
```bash
# Backend (requires PostgreSQL)
cd backend
pytest tests/ -v

# Frontend
cd frontend
npm run test
```

## Branch Naming

Use the following convention:
- `feature/<short-description>` — new features
- `fix/<short-description>` — bug fixes
- `chore/<short-description>` — maintenance, docs, CI
- `test/<short-description>` — adding or updating tests

Examples:
- `feature/add-otp-verification`
- `fix/parcel-geometry-migration`
- `chore/update-ci-security-scanning`

## Pull Request Checklist

Before submitting a PR, ensure:

- [ ] **Lint passes**: `ruff check app/ tests/` (backend), `npm run lint` (frontend)
- [ ] **Format passes**: `ruff format --check app/ tests/` (backend)
- [ ] **Type check passes**: `mypy app/ --ignore-missing-imports` (backend), `npm run typecheck` (frontend)
- [ ] **Tests pass**: `pytest tests/ -v` (backend), `npm run test` (frontend)
- [ ] **No secrets committed**: Verify no API keys, passwords, or real credentials in the diff
- [ ] **Env vars documented**: New env vars added to both `.env.example` files and `README.md`
- [ ] **DECISIONS.md updated**: Append a `## D<number>` entry for any non-trivial architectural decision
- [ ] **Seed script works**: `python -m app.seed` runs successfully and default logins work

## Code Style

### Backend (Python)
- Formatter/Linter: **ruff** (line length 100, Python 3.11 target)
- Type hints: encouraged but not enforced (mypy with `--ignore-missing-imports`)
- Tests: **pytest** with `pytest-asyncio` for async endpoints

### Frontend (TypeScript/React)
- Linter: **ESLint** with React hooks and refresh plugins
- Type checker: **TypeScript** strict mode
- Tests: **Vitest** with React Testing Library
- Components: **shadcn/ui** primitives with Tailwind CSS

## Reporting Issues

When reporting bugs, please include:
1. Steps to reproduce
2. Expected behavior
3. Actual behavior
4. Browser/OS if frontend-related
5. Python version and OS if backend-related

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
