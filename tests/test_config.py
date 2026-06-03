import os
import tempfile
import unittest

import src.config as cfg_mod


class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.mkdtemp()
        self._orig_dir = cfg_mod.CONFIG_DIR
        self._orig_file = cfg_mod.CONFIG_FILE
        cfg_mod.CONFIG_DIR = self._tmpdir
        cfg_mod.CONFIG_FILE = os.path.join(self._tmpdir, "config.json")

    def tearDown(self):
        cfg_mod.CONFIG_DIR = self._orig_dir
        cfg_mod.CONFIG_FILE = self._orig_file

    def test_default_values(self):
        config = cfg_mod.ConfigManager()
        self.assertEqual(config.get("ai_provider"), "openrouter")
        self.assertEqual(config.get("openrouter_model"), "openai/gpt-4o-mini")
        self.assertIsNone(config.get("active_staff_id"))
        self.assertIsNone(config.get("monthly_budget"))

    def test_set_and_get(self):
        config = cfg_mod.ConfigManager()
        config.set("monthly_budget", 1000.0)
        self.assertEqual(config.get("monthly_budget"), 1000.0)

    def test_unknown_key_returns_default(self):
        config = cfg_mod.ConfigManager()
        self.assertEqual(config.get("nonexistent", 42), 42)
        self.assertIsNone(config.get("nonexistent"))

    def test_save_and_reload(self):
        config = cfg_mod.ConfigManager()
        config.set("monthly_budget", 500.0)
        config.set("ai_provider", "groq")

        new_config = cfg_mod.ConfigManager()
        self.assertEqual(new_config.get("monthly_budget"), 500.0)
        self.assertEqual(new_config.get("ai_provider"), "groq")


if __name__ == "__main__":
    unittest.main()
