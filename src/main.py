#!/usr/bin/env python3
"""Smart Expense Tracker — Seamless Technologies Staff Insights.

A terminal-based expense tracker with AI-powered analytics,
supporting OpenRouter and Groq AI providers.
"""

import sys

from src.ui.app import App


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)
