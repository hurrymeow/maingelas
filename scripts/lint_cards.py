#!/usr/bin/env python3
"""Lint scripts/cards/*.json. Exits 1 on any problem."""
import sys

from cardlib import load_cards, lint

cards = load_cards()
errors = lint(cards)
for e in errors:
    print("FAIL", e)
print(f"{len(cards)} cards, {len(errors)} problems")
sys.exit(1 if errors else 0)
