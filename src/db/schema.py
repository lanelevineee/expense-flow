import logging

logger = logging.getLogger(__name__)

POSTGRES_TABLES = """
CREATE TABLE IF NOT EXISTS staff (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    department VARCHAR(255) DEFAULT '',
    email VARCHAR(255) DEFAULT '',
    pin VARCHAR(255) DEFAULT '',
    password_hash VARCHAR(255) DEFAULT '',
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(255) DEFAULT '',
    otp_email VARCHAR(255) DEFAULT '',
    currency VARCHAR(10) DEFAULT 'USD',
    theme VARCHAR(50) DEFAULT 'default',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,
    staff_id INTEGER NOT NULL REFERENCES staff(id) ON DELETE CASCADE,
    amount NUMERIC(12,2) NOT NULL,
    category VARCHAR(255) NOT NULL,
    description TEXT DEFAULT '',
    expense_date DATE NOT NULL,
    payment_method_id INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    icon VARCHAR(255) DEFAULT '',
    color VARCHAR(50) DEFAULT '',
    budget NUMERIC(12,2) DEFAULT 0,
    is_default BOOLEAN DEFAULT FALSE,
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS recurring_expenses (
    id SERIAL PRIMARY KEY,
    staff_id INTEGER NOT NULL REFERENCES staff(id) ON DELETE CASCADE,
    amount NUMERIC(12,2) NOT NULL,
    category VARCHAR(255) NOT NULL,
    description TEXT DEFAULT '',
    frequency VARCHAR(50) NOT NULL DEFAULT 'monthly',
    interval_days INTEGER DEFAULT 30,
    next_date DATE NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS payment_methods (
    id SERIAL PRIMARY KEY,
    staff_id INTEGER NOT NULL REFERENCES staff(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'cash',
    is_default BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS user_stats (
    staff_id INTEGER PRIMARY KEY REFERENCES staff(id) ON DELETE CASCADE,
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    total_expenses INTEGER DEFAULT 0,
    days_active INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS achievements (
    id SERIAL PRIMARY KEY,
    code VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT DEFAULT '',
    icon VARCHAR(255) DEFAULT '',
    criteria_type VARCHAR(100) NOT NULL,
    criteria_value INTEGER NOT NULL,
    xp_reward INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS user_achievements (
    id SERIAL PRIMARY KEY,
    staff_id INTEGER NOT NULL REFERENCES staff(id) ON DELETE CASCADE,
    achievement_id INTEGER NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,
    earned_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(staff_id, achievement_id)
);

CREATE TABLE IF NOT EXISTS challenges (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT DEFAULT '',
    goal_type VARCHAR(100) NOT NULL,
    goal_value INTEGER NOT NULL,
    xp_reward INTEGER DEFAULT 0,
    starts_at DATE NOT NULL,
    ends_at DATE NOT NULL,
    active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS challenge_progress (
    id SERIAL PRIMARY KEY,
    challenge_id INTEGER NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
    staff_id INTEGER NOT NULL REFERENCES staff(id) ON DELETE CASCADE,
    progress INTEGER DEFAULT 0,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    UNIQUE(challenge_id, staff_id)
);

CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    staff_id INTEGER NOT NULL REFERENCES staff(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER,
    old_value TEXT,
    new_value TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS otp_codes (
    id SERIAL PRIMARY KEY,
    staff_id INTEGER NOT NULL REFERENCES staff(id) ON DELETE CASCADE,
    code VARCHAR(6) NOT NULL,
    purpose VARCHAR(20) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
"""

SQLITE_TABLES = """
CREATE TABLE IF NOT EXISTS staff (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    department TEXT DEFAULT '',
    email TEXT DEFAULT '',
    pin TEXT DEFAULT '',
    password_hash TEXT DEFAULT '',
    mfa_enabled INTEGER DEFAULT 0,
    mfa_secret TEXT DEFAULT '',
    otp_email TEXT DEFAULT '',
    currency TEXT DEFAULT 'USD',
    theme TEXT DEFAULT 'default',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    description TEXT DEFAULT '',
    expense_date DATE NOT NULL,
    payment_method_id INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    icon TEXT DEFAULT '',
    color TEXT DEFAULT '',
    budget REAL DEFAULT 0,
    is_default INTEGER DEFAULT 0,
    sort_order INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS recurring_expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    description TEXT DEFAULT '',
    frequency TEXT NOT NULL DEFAULT 'monthly',
    interval_days INTEGER DEFAULT 30,
    next_date TEXT NOT NULL,
    active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS payment_methods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'cash',
    is_default INTEGER DEFAULT 0,
    FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS user_stats (
    staff_id INTEGER PRIMARY KEY,
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date TEXT,
    total_expenses INTEGER DEFAULT 0,
    days_active INTEGER DEFAULT 0,
    FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    icon TEXT DEFAULT '',
    criteria_type TEXT NOT NULL,
    criteria_value INTEGER NOT NULL,
    xp_reward INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS user_achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id INTEGER NOT NULL,
    achievement_id INTEGER NOT NULL,
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE CASCADE,
    FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE,
    UNIQUE(staff_id, achievement_id)
);
CREATE TABLE IF NOT EXISTS challenges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    goal_type TEXT NOT NULL,
    goal_value INTEGER NOT NULL,
    xp_reward INTEGER DEFAULT 0,
    starts_at TEXT NOT NULL,
    ends_at TEXT NOT NULL,
    active INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS challenge_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    challenge_id INTEGER NOT NULL,
    staff_id INTEGER NOT NULL,
    progress INTEGER DEFAULT 0,
    completed INTEGER DEFAULT 0,
    completed_at TEXT,
    FOREIGN KEY (challenge_id) REFERENCES challenges(id) ON DELETE CASCADE,
    FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE CASCADE,
    UNIQUE(challenge_id, staff_id)
);
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id INTEGER,
    old_value TEXT,
    new_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS otp_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id INTEGER NOT NULL,
    code TEXT NOT NULL,
    purpose TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE CASCADE
);
"""


def init_tables(db):
    sql = POSTGRES_TABLES if db.is_postgres else SQLITE_TABLES
    with db.cursor() as cur:
        for statement in sql.split(";"):
            statement = statement.strip()
            if statement:
                cur.execute(statement)
    logger.info("Database tables initialized (%s)", "PostgreSQL" if db.is_postgres else "SQLite")
