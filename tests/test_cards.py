import json, os, subprocess, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from cardlib import lint, normalise

def card(text, **kw):
    c = {"text": text, "category": "dare", "players": text.count("{player}") and 1, "heat": 1, "pack": "base", "_src": text[:10]}
    if "{player2}" in text: c["players"] = 2
    c.update(kw); return c

class LintTests(unittest.TestCase):
    def ok(self, cards): self.assertEqual(lint(cards), [])
    def bad(self, cards, frag):
        errs = lint(cards); self.assertTrue(any(frag in e for e in errs), errs)

    def test_clean(self): self.ok([card("{player}, sing a verse of any song."), card("Name a hawker dish.", category="category")])
    def test_exact_dup(self): self.bad([card("Hop on one leg."), card("Hop on one leg.")], "exact duplicate")
    def test_sip_variant(self): self.bad([card("{player}, take 2 sips.", category="drink"), card("{player}, take 3 sips.", category="drink")], "near-duplicate")
    def test_unknown_token(self): self.bad([card("{plyer}, go.")], "unknown tokens")
    def test_missing_heat(self):
        c = card("Hop."); del c["heat"]; self.bad([c], "heat")
    def test_players_mismatch(self): self.bad([card("{player}, hop.", players=0)], "players is")
    def test_flip(self): self.bad([card("Had a pet? If you have not, take 3 sips.", category="neverhave")], "flip")
    def test_cap(self):
        words = ["alpha","bravo","charlie","delta","echo","foxtrot","golf","hotel","india","juliet","kilo","lima","mike","november","oscar","papa","quebec","romeo","sierra","tango","uniform","victor"]
        cards = [card(f"Do the {w} dance now.") for w in words]
        self.bad(cards, "over 20%")
    def test_callback_pair(self):
        a = card("{player} is infected.", id="v1", endedBy="c1"); b = card("Cure for all.", id="c1", ends="v1")
        self.ok([a, b]); b["ends"] = "zzz"; self.bad([a, b], "unknown id")
    def test_normalise(self): self.assertEqual(normalise("{player} takes 3 sips!"), normalise("{player} takes 5 sip."))

class GeneratorTest(unittest.TestCase):
    def test_runs_and_shape(self):
        out = os.path.join(tempfile.mkdtemp(), "q.js")
        script = os.path.join(os.path.dirname(__file__), "..", "scripts", "generate_questions.py")
        r = subprocess.run([sys.executable, script, out], capture_output=True, text=True)
        if os.listdir(os.path.join(os.path.dirname(script), "cards")):
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            body = open(out).read()
            self.assertIn("const PICOLO_QUESTIONS = ", body)
            data = json.loads(body.split("=", 1)[1].rstrip().rstrip(";"))
            for k in ("text", "category", "players", "heat", "pack"): self.assertIn(k, data[0])

if __name__ == "__main__": unittest.main()
