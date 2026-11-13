# Plan: fresher cards

## Goal
Make every game feel new. Replace the deck the generator multiplies out of templates with distinct hand-written cards. Deal them smartly. Add formats, callback cards and packs.

## Audit (2026-11-13)
- 714 of the 1000 cards come from 260 prompts. Group: 65 × 4. Never have I ever: 128 × 2. Category: 67 × 3.
- 174 cards differ from another card only in the sip count.
- 251 cards use the "have not" flip. Some come out absurd, e.g. "had a threesome? If you have not, take 3 sips."
- 575 cards don't name a player. "Do your best impression" appears 20 times.
- Commit 3b2f90e (21 Sep) changed first-person "Never have I ever" to "Have you ever?" and cut the group wordings from 3 to 1.
- app.js reshuffles the full deck each game. There's no seen-history, escalation or card state.

## Decisions and why
- **Scope: everything** (Hari, 13 Nov). Covers A curate, B dealer, C formats, D callbacks, E packs.
- **One idea per card.** No cartesian templates and no sip-count variants. Duplicates are what make the deck feel stale.
- **Deck ~450 cards across the base deck and packs.** A night is about 150 cards, so distinct cards matter more than the count.
- **Drop the "have not" flip.** Only the person who did the thing drinks.
- **Bring back first-person "Never have I ever".**
- **Write cards by hand in a data file, not in code.** Hari can then edit the cards without touching Python.
- **Sequence B, D and E after the PWA thread merges.** They touch app.js, index.html and css.

## Tasks
Order: 1 → 2 → 3 run in parallel with the PWA work. Tasks 4 to 7 wait for the PWA merge.

### 1. Card schema and lint (Sonnet)
- Files: `scripts/cards/*.yaml` or `.json` (new), `scripts/generate_questions.py` (rewrite to read the data files), `scripts/lint_cards.py` (new).
- Schema: `text`, `category`, `players`, `heat` (1–3), `pack` (default `base`), optional `ends` / `endedBy` for callbacks.
- The lint fails on exact duplicates, and on near-duplicates once numbers and player tokens are stripped.
- It also fails if any category exceeds 20% of a pack, or on unknown tokens or a missing heat.
- Done-check: the lint passes on the new data, and running the generator writes `js/questions.js` with the same `PICOLO_QUESTIONS` shape plus the new fields.

### 2. Rate a 40-card sample (Sonnet writes, Hari rates)
- File: `docs/plans/fresher-cards-sample.md`, with 40 cards spanning every format and heat level.
- Hari marks each card keep, fix or cut. Those marks set the tone for task 3.
- Done-check: Hari's ratings are recorded in the file.

### 3. Write the base deck (Sonnet)
- Files: `scripts/cards/base.*`.
- About 300 cards. Mix: never have I ever 15%, group "who has" 12%, point-on-three 10%, hot take 8%, hot seat 6%, face-off 8%, category 8%, dare 12%, rule 6%, vote 8%, non-sip penalty 7%.
- At least 60% of cards name a player. No phrasing opener may appear on more than 10 cards.
- Heat split: 1 at 45%, 2 at 40%, 3 at 15%.
- Done-check: the lint passes. A spot read of 30 random cards turns up no near-duplicates.

### 4. Dealer rules (Sonnet, after the PWA merge)
- File: `js/app.js`.
- Never deal the same category twice in a row.
- Heat ceiling by round: round 1 deals heat ≤1, round 2 ≤2, round 3+ ≤3.
- A per-device seen-history in localStorage (try/catch) deals unseen cards first and resets once the deck runs out.
- Done-check: a unit test or Node script deals 150 cards and asserts no back-to-back categories and the heat ceiling per round. Over two simulated games, the second game opens with unseen cards.

### 5. Callback cards (Sonnet, after task 4)
- Files: `js/app.js`, `scripts/cards/base.*`.
- A card with `ends: "<id>"` starts a virus or rule. The dealer then guarantees its Cure card 8–15 cards later.
- If a round ends first, the round-end screen lists the active effects.
- Write about 15 virus/Cure pairs.
- Done-check: the simulation shows every started effect ending within 15 cards or at round end.

### 6. Singapore pack (Sonnet)
- File: `scripts/cards/sg.*`.
- About 80 cards on hawker, NS, MRT, HDB, Singlish, chope and kiasu. Same mix and lint as the base deck.
- Done-check: the lint passes and Hari approves a 10-card sample.

### 7. Spice level and pack toggles (Sonnet, after task 4)
- Files: `index.html`, `js/app.js`, `css/style.css`.
- On the setup screen: a spice cap (Chill = heat 1, Spicy = ≤2, Wild = ≤3) and pack checkboxes. Both persist in localStorage.
- Done-check: a Playwright run shows that Chill deals no heat 2–3 cards and that turning off the SG pack excludes its cards. Screenshot to Hari before shipping.

## Open questions
- **Spice ceiling.** Does heat 3 stop at the current level (threesome / cheating questions), or go further? Default: the current level.
- **Deck counter.** Rounds currently derive from deck length. Keep 50-card rounds over a smaller deck, or end the game after 3 rounds?
- **Rename `PICOLO_QUESTIONS`** and the "Picolo" docstring to Maingelas? It's cosmetic and fits into task 1.
