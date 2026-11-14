# Rename the game to Habis

## Goal
Rename the player-facing game from "Maingelas" to "Habis". Remove the leftover "Picolo" names from the code.

## Decisions and why
- **Name: Habis.** Malay and Singlish for "finished, all gone", like a drink-up call. Hari picked it on 2026-11-14.
- **Why not the others.** Bojio and Tahan were the other local options. Yam Seng is used by many bars. Gelas is too generic.
- **Clash check.** Web and app-store search found no app or game called Habis. No trademark search was run.
- **Known risk.** English speakers may misread it as "habits". Accepted.
- **Keep the repo name and URL.** The repo stays `hurrymeow/maingelas`. Renaming it would change the Pages URL and break installed PWAs.
- **Keep saved players.** `app.js` stores players under `picolo:players`. The new key must read the old key once, so nobody loses their list.
- **Neutral code names.** `PICOLO_QUESTIONS` becomes `QUESTIONS`, not a brand name. A future rename then won't touch code.

## Tasks
1. **Player-facing copy** (Haiku)
   - Files: `index.html` (title and h1), `manifest.json` (name, short_name).
   - Done-check: the page title, setup heading and installed app name read "Habis".
2. **Code names and storage** (Sonnet)
   - Files: `js/app.js` (storage key with one-time migration from `picolo:players`), `js/questions.js` and `scripts/generate_questions.py` (`PICOLO_QUESTIONS` to `QUESTIONS`, the "Picolo" docstring).
   - Also fix the generator's hard-coded output path `/home/user/maingelas/js/questions.js` to a repo-relative path.
   - Done-check: `grep -rni picolo` outside `docs/` returns nothing. Players saved before the update still appear after it.
3. **Cache bump** (Haiku)
   - File: `sw.js`. Bump `CACHE_NAME` to `habis-v1` so clients pick up the new shell.
   - Done-check: the update banner shows on an installed copy after deploy.

Ship tasks 1 to 3 as one PR. Tasks are small and touch shared files.

## Open questions
- **Overlap with fresher cards.** Task 1 of `docs/plans/fresher-cards.md` also edits the generator and `questions.js`. That plan's open item on renaming `PICOLO_QUESTIONS` is now settled here. Run this rename first, or fold task 2 into fresher-cards task 1.
- **Icons.** The current icons may show "M". Check them, and redraw them if so (Mono Dark).
