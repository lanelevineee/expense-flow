# Smart Expense Tracker

A smart expense tracking platform with AI-powered insights, built for teams. Features a terminal TUI, synchronized web dashboard, QR code phone access, and gamification to encourage consistent expense logging.

> **Part of the [Seamless Technologies](https://github.com/seamless-tech) Open Source Initiative** — building tools that matter.

---

## Highlights

- **Terminal + Web** — Use the Rich TUI on desktop, or scan a QR code to access the web dashboard from your phone
- **AI-Powered Insights** — Anomaly detection, spending analysis, and budget recommendations via OpenRouter or Groq
- **Gamification** — XP, levels, streaks, achievements, and challenges to keep expense logging engaging
- **Role-Based Access** — Admin and staff roles with JWT authentication and optional MFA (TOTP + email OTP)
- **PostgreSQL + SQLite** — PostgreSQL as primary, SQLite as automatic fallback
- **Docker Ready** — One command to run the full stack (app + database)

---

## Quick Start

### Option 1: Docker (Recommended)

```bash
git clone https://github.com/seamless-tech/smart-expense-tracker.git
cd smart-expense-tracker
docker-compose up --build
```

Web dashboard: `http://localhost:7070`
Terminal app: `python3 -m src.main`

### Option 2: Local Setup

```bash
git clone https://github.com/seamless-tech/smart-expense-tracker.git
cd smart-expense-tracker
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 -m src.main
```

Requires PostgreSQL running locally. Copy `.env.example` to `.env` and configure.

---

## Features

### Terminal (TUI)
- Arrow key navigation with number shortcuts
- Record and view expenses with smart filtering
- Category management with budgets
- Recurring expense tracking
- Spending analytics with charts
- AI-powered insights (3 analysis modes)
- Gamification dashboard
- Reports and data export
- QR code for phone access

### Web Dashboard
- Mobile-responsive dark theme
- Login/register with email + password
- Dashboard with spending overview
- Expense CRUD with filtering
- Category and staff management
- Gamification stats and leaderboard
- Analytics visualizations

### AI Insights
- **General Analysis** — Overall spending patterns and recommendations
- **Anomaly Detection** — Flags unusual transactions
- **Budget Recommendations** — Suggested limits based on history

### Gamification
- XP and leveling system
- Daily activity streaks
- 13 unlockable achievements
- Time-bound challenges
- Staff leaderboard

---

## Architecture

```
smart-expense-tracker/
├── src/
│   ├── auth/           # JWT auth, bcrypt passwords, MFA (TOTP + email OTP)
│   ├── db/
│   │   ├── connection.py    # PostgreSQL + SQLite dual support
│   │   ├── schema.py        # Database schema (both dialects)
│   │   └── repositories/    # Data access layer (7 repositories)
│   ├── providers/      # AI provider abstraction (OpenRouter, Groq)
│   ├── services/       # Business logic layer
│   ├── ui/             # Rich terminal interface
│   │   ├── components/ # Reusable TUI widgets
│   │   └── screens/    # Application screens
│   └── web/            # FastAPI web platform
│       ├── routes/     # API endpoints (11 route modules)
│       └── templates/  # Jinja2 HTML templates
├── tests/              # Unit tests (24 tests)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── pyproject.toml
```

### SOLID Principles

| Principle | Implementation |
|---|---|
| **S**ingle Responsibility | Each class has one job — repositories handle data, services handle logic, UI handles display |
| **O**pen/Closed | New AI providers implement `AIProvider` ABC; new screens extend `BaseScreen` |
| **L**iskov Substitution | `OpenRouterProvider` and `GroqProvider` are interchangeable |
| **I**nterface Segregation | Repositories split by entity; small focused service interfaces |
| **D**ependency Inversion | Services depend on repository abstractions; UI depends on service abstractions |

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.9+ |
| Terminal UI | Rich |
| Web Framework | FastAPI + Uvicorn |
| Templates | Jinja2 |
| Primary DB | PostgreSQL 16 |
| Fallback DB | SQLite |
| Auth | bcrypt + JWT + pyotp |
| AI Providers | OpenRouter, Groq |
| Containerization | Docker + Docker Compose |

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DB_HOST` | _(empty = SQLite)_ | PostgreSQL host (`localhost` for terminal, `db` for Docker) |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_NAME` | `expense_tracker` | Database name |
| `DB_USER` | `expense_user` | Database user |
| `DB_PASSWORD` | `expense_pass` | Database password |
| `JWT_SECRET` | _(auto-generated)_ | Secret for JWT tokens |

### AI Provider Setup

1. Open the terminal app → Settings
2. Set your OpenRouter or Groq API key
3. Optionally change the model
4. Test the connection

---

## Testing

```bash
python3 -m pytest tests/ -v
```

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## AI Development Disclosure

This project was developed using AI-assisted coding tools. Specifically:

- **OpenCode** — AI coding assistant used throughout the development process
- **MiMo V2.5** — AI model (via OpenCode) used for code generation, debugging, and architectural guidance

**All AI-generated code was thoroughly reviewed, tested, and validated by a human developer** to ensure clean code, adherence to SOLID principles, security best practices, and production readiness. The human developer maintained full editorial control over the codebase, architecture decisions, and final implementation.

This project is part of a series of open-source tools being built by Seamless Technologies. AI was used as a development accelerator — the design decisions, code quality standards, and project vision are human-driven.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- Built with love by [Seamless Technologies](https://github.com/seamless-tech)
- AI tools: OpenCode + MiMo V2.5
- Open source because great tools should be shared
