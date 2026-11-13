"""Shared card loading and validation for generate_questions.py and lint_cards.py."""
import difflib
import glob
import json
import os
import re

CARDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cards")

# Categories the game knows today (app.js CATEGORY_META) plus the formats
# the fresher-cards plan adds. New ones show a generic "Card" label until
# app.js learns them (task 4 onwards).
CATEGORIES = {
    "neverhave", "group", "point", "hottake", "hotseat", "versus",
    "category", "dare", "rule", "vote", "penalty", "drink", "give", "special",
}
TOKENS = {"{player}": 1, "{player2}": 2}
FIELDS = {"id", "text", "category", "players", "heat", "pack", "ends", "endedBy"}
CATEGORY_CAP = 0.20
CAP_MIN_PACK_SIZE = 20  # skip the cap on tiny packs such as a work in progress
NEAR_DUP_RATIO = 0.88
BANNED_FLIPS = ("if you have not", "if you haven't", "whoever hasn't", "the one who hasn't")


def load_cards(cards_dir=CARDS_DIR):
    cards = []
    for path in sorted(glob.glob(os.path.join(cards_dir, "*.json"))):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError(f"{path}: expected a JSON list of cards")
        for i, card in enumerate(data):
            card = dict(card)
            card["_src"] = f"{os.path.basename(path)}[{i}]"
            card.setdefault("pack", "base")
            cards.append(card)
    return cards


def normalise(text):
    """Strip tokens, numbers and sip words so sip-count variants collapse."""
    t = text.lower()
    t = re.sub(r"\{player2?\}", " ", t)
    t = re.sub(r"\d+", " ", t)
    t = re.sub(r"\bsips?\b", " ", t)
    t = re.sub(r"[^a-z ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def lint(cards):
    errors = []
    ids = {}
    for c in cards:
        src = c["_src"]
        unknown = set(c) - FIELDS - {"_src"}
        if unknown:
            errors.append(f"{src}: unknown fields {sorted(unknown)}")
        text = c.get("text")
        if not isinstance(text, str) or not text.strip():
            errors.append(f"{src}: missing text")
            continue
        if c.get("category") not in CATEGORIES:
            errors.append(f"{src}: unknown category {c.get('category')!r}")
        if c.get("heat") not in (1, 2, 3):
            errors.append(f"{src}: heat must be 1, 2 or 3, got {c.get('heat')!r}")
        found = set(re.findall(r"\{[^}]*\}", text))
        bad = found - set(TOKENS)
        if bad:
            errors.append(f"{src}: unknown tokens {sorted(bad)}")
        needed = max([TOKENS[t] for t in found if t in TOKENS], default=0)
        if "{player2}" in found and "{player}" not in found:
            errors.append(f"{src}: {{player2}} without {{player}}")
        if c.get("players") != needed:
            errors.append(f"{src}: players is {c.get('players')!r} but text needs {needed}")
        low = text.lower()
        if any(b in low for b in BANNED_FLIPS):
            errors.append(f"{src}: 'have not' flip is banned: {text!r}")
        if "id" in c:
            if c["id"] in ids:
                errors.append(f"{src}: duplicate id {c['id']!r}")
            ids[c["id"]] = c
    for c in cards:
        src = c["_src"]
        for field, back in (("ends", "endedBy"), ("endedBy", "ends")):
            if field in c:
                if "id" not in c:
                    errors.append(f"{src}: {field} needs an id on the card")
                other = ids.get(c[field])
                if other is None:
                    errors.append(f"{src}: {field} points at unknown id {c[field]!r}")
                elif other.get(back) != c.get("id"):
                    errors.append(f"{src}: {field} {c[field]!r} does not point back")
        if "ends" in c and "endedBy" in c:
            errors.append(f"{src}: a card cannot have both ends and endedBy")

    # duplicates, within the whole deck (a duplicate across packs is still stale)
    seen_exact = {}
    norms = []
    for c in cards:
        text = c.get("text")
        if not isinstance(text, str):
            continue
        if text in seen_exact:
            errors.append(f"{c['_src']}: exact duplicate of {seen_exact[text]}")
            continue
        seen_exact[text] = c["_src"]
        n = normalise(text)
        for other_n, other_src in norms:
            if n == other_n or difflib.SequenceMatcher(None, n, other_n).ratio() >= NEAR_DUP_RATIO:
                errors.append(f"{c['_src']}: near-duplicate of {other_src}")
                break
        norms.append((n, c["_src"]))

    # category cap per pack
    by_pack = {}
    for c in cards:
        by_pack.setdefault(c["pack"], []).append(c)
    for pack, items in by_pack.items():
        if len(items) < CAP_MIN_PACK_SIZE:
            continue
        counts = {}
        for c in items:
            counts[c.get("category")] = counts.get(c.get("category"), 0) + 1
        for cat, n in counts.items():
            if n / len(items) > CATEGORY_CAP:
                errors.append(f"pack {pack!r}: category {cat!r} is {n}/{len(items)} cards, over {int(CATEGORY_CAP*100)}%")
    return errors
