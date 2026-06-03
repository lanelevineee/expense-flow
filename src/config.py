import json
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".expense_tracker")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "ai_provider": "openrouter",
    "openrouter_api_key": "",
    "groq_api_key": "",
    "openrouter_model": "openai/gpt-4o-mini",
    "groq_model": "llama3-70b-8192",
    "default_model": "openai/gpt-4o-mini",
    "active_staff_id": None,
    "monthly_budget": None,
    "jwt_secret": "",
    "smtp_host": "",
    "smtp_port": 587,
    "smtp_user": "",
    "smtp_password": "",
}

_ENV_MAP = {
    "ai_provider": "AI_PROVIDER",
    "openrouter_api_key": "OPENROUTER_API_KEY",
    "groq_api_key": "GROQ_API_KEY",
    "openrouter_model": "OPENROUTER_MODEL",
    "groq_model": "GROQ_MODEL",
    "default_model": "DEFAULT_MODEL",
    "jwt_secret": "JWT_SECRET",
    "smtp_host": "SMTP_HOST",
    "smtp_port": "SMTP_PORT",
    "smtp_user": "SMTP_USER",
    "smtp_password": "SMTP_PASSWORD",
}


class ConfigManager:
    def __init__(self):
        self._data = DEFAULT_CONFIG.copy()
        self._load_env()
        self._load_file()

    def _load_env(self):
        for key, env_var in _ENV_MAP.items():
            val = os.getenv(env_var)
            if val is not None and val != "":
                if key == "smtp_port":
                    try:
                        val = int(val)
                    except ValueError:
                        continue
                self._data[key] = val

    def _load_file(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE) as f:
                    file_data = json.load(f)
                for k, v in file_data.items():
                    self._data[k] = v
            except (json.JSONDecodeError, IOError):
                pass

    def save(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(self._data, f, indent=2)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value
        self.save()

    def is_env_overridden(self, key) -> bool:
        env_var = _ENV_MAP.get(key)
        if not env_var:
            return False
        return os.getenv(env_var) is not None
