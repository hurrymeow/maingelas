(function () {
  "use strict";

  const STORAGE_KEY = "habis:players";
  const LEGACY_STORAGE_KEY = "picolo:players"; // fallback until habis:players is first saved

  const CATEGORY_META = {
    drink: { label: "Drink" },
    give: { label: "Give" },
    group: { label: "Group" },
    category: { label: "Category" },
    neverhave: { label: "Never have I ever" },
    rule: { label: "New rule" },
    dare: { label: "Dare" },
    special: { label: "Special" },
    versus: { label: "Versus" },
    vote: { label: "Vote" },
  };

  const ROUND_SIZE = 50;

  const screens = {
    setup: document.getElementById("screen-setup"),
    game: document.getElementById("screen-game"),
    roundEnd: document.getElementById("screen-round-end"),
    end: document.getElementById("screen-end"),
  };

  const playerForm = document.getElementById("player-form");
  const playerInput = document.getElementById("player-name-input");
  const playerList = document.getElementById("player-list");
  const playerHint = document.getElementById("player-hint");
  const startGameBtn = document.getElementById("start-game-btn");

  const menuBtn = document.getElementById("menu-btn");
  const nextBtn = document.getElementById("next-btn");
  const cardEl = document.getElementById("question-card");
  const cardTextEl = document.getElementById("card-text");
  const cardCategoryEl = document.getElementById("card-category");
  const progressFill = document.getElementById("progress-fill");
  const deckCountEl = document.getElementById("deck-count");

  const reshuffleBtn = document.getElementById("reshuffle-btn");
  const backToSetupBtn = document.getElementById("back-to-setup-btn");

  const roundEndTitle = document.getElementById("round-end-title");
  const roundEndTagline = document.getElementById("round-end-tagline");
  const nextRoundBtn = document.getElementById("next-round-btn");

  /** @type {string[]} */
  let players = [];
  let deck = [];
  let deckIndex = -1;
  let lastUsedPlayer = null;
  let roundEndPending = false;

  function showScreen(name) {
    Object.values(screens).forEach((s) => s.classList.remove("active"));
    screens[name].classList.add("active");
  }

  // ---------------- Player setup ----------------

  function loadPlayers() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY) || localStorage.getItem(LEGACY_STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) players = parsed.filter((p) => typeof p === "string");
      }
    } catch (e) {
      players = [];
    }
  }

  function savePlayers() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(players));
    } catch (e) {
      /* ignore quota / privacy-mode errors */
    }
  }

  function renderPlayers() {
    playerList.innerHTML = "";
    players.forEach((name, i) => {
      const li = document.createElement("li");
      li.className = "player-chip";
      const span = document.createElement("span");
      span.textContent = name;
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "remove-player";
      btn.setAttribute("aria-label", "Remove " + name);
      btn.textContent = "✕";
      btn.addEventListener("click", () => {
        players.splice(i, 1);
        savePlayers();
        renderPlayers();
      });
      li.appendChild(span);
      li.appendChild(btn);
      playerList.appendChild(li);
    });

    const enough = players.length >= 2;
    startGameBtn.disabled = !enough;
    if (players.length === 0) {
      playerHint.textContent = "Add at least 2 players to start.";
      playerHint.classList.remove("hint-ok");
    } else if (!enough) {
      playerHint.textContent = "Add at least one more player.";
      playerHint.classList.remove("hint-ok");
    } else {
      playerHint.textContent = players.length + " players ready.";
      playerHint.classList.add("hint-ok");
    }
  }

  function addPlayer(rawName) {
    const name = rawName.trim();
    if (!name) return;
    if (players.some((p) => p.toLowerCase() === name.toLowerCase())) {
      playerInput.value = "";
      return;
    }
    players.push(name);
    savePlayers();
    renderPlayers();
    playerInput.value = "";
    playerInput.focus();
  }

  playerForm.addEventListener("submit", (e) => {
    e.preventDefault();
    addPlayer(playerInput.value);
  });

  startGameBtn.addEventListener("click", () => {
    if (players.length < 2) return;
    startGame();
  });

  // ---------------- Deck / game logic ----------------

  function shuffle(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  function pickPlayer(exclude) {
    let pool = players;
    if (players.length > 1 && exclude) {
      pool = players.filter((p) => p !== exclude);
    }
    const choice = pool[Math.floor(Math.random() * pool.length)];
    return choice;
  }

  function fillTemplate(text, playersNeeded) {
    let result = text;
    if (playersNeeded >= 1 && result.includes("{player}")) {
      const p1 = pickPlayer(lastUsedPlayer);
      lastUsedPlayer = p1;
      result = result.split("{player}").join(p1);
    }
    if (playersNeeded >= 2 && result.includes("{player2}")) {
      const p2 = pickPlayer(lastUsedPlayer);
      result = result.split("{player2}").join(p2);
    }
    return result;
  }

  function totalRounds() {
    return Math.ceil(deck.length / ROUND_SIZE);
  }

  function startGame() {
    deck = shuffle(QUESTIONS);
    deckIndex = -1;
    lastUsedPlayer = null;
    roundEndPending = false;
    updateProgress();
    cardCategoryEl.textContent = "Ready";
    cardTextEl.innerHTML = "Tap “Deal first card” to begin.";
    nextBtn.textContent = "Deal first card";
    showScreen("game");
  }

  function updateProgress() {
    const dealt = deckIndex + 1;
    const cardInRound = dealt === 0 ? 0 : ((dealt - 1) % ROUND_SIZE) + 1;
    const roundNum = dealt === 0 ? 1 : Math.floor((dealt - 1) / ROUND_SIZE) + 1;
    const pct = dealt === 0 ? 0 : (cardInRound / ROUND_SIZE) * 100;
    progressFill.style.width = pct + "%";
    deckCountEl.textContent =
      "Round " + roundNum + "/" + totalRounds() + " · " + (ROUND_SIZE - cardInRound) + " left";
  }

  function dealNext() {
    deckIndex++;
    if (deckIndex >= deck.length) {
      showScreen("end");
      return;
    }

    const q = deck[deckIndex];
    const meta = CATEGORY_META[q.category] || { label: "Card" };
    const text = fillTemplate(q.text, q.players || 0);

    cardCategoryEl.textContent = meta.label;
    cardTextEl.textContent = text;
    nextBtn.textContent = "Next card";

    cardEl.classList.remove("deal-in");
    // force reflow to restart animation
    void cardEl.offsetWidth;
    cardEl.classList.add("deal-in");

    updateProgress();

    const dealt = deckIndex + 1;
    const isRoundBoundary = dealt % ROUND_SIZE === 0;
    const isLastCard = dealt >= deck.length;
    roundEndPending = isRoundBoundary && !isLastCard;
  }

  function showRoundEndScreen() {
    const roundNum = Math.floor(deckIndex / ROUND_SIZE) + 1;
    roundEndTitle.textContent = "Round " + roundNum + " done";
    roundEndTagline.textContent = ROUND_SIZE + " questions down. Refill your drinks.";
    nextRoundBtn.textContent = "Start round " + (roundNum + 1);
    showScreen("roundEnd");
  }

  nextBtn.addEventListener("click", () => {
    if (roundEndPending) {
      roundEndPending = false;
      showRoundEndScreen();
      return;
    }
    dealNext();
  });

  nextRoundBtn.addEventListener("click", () => {
    showScreen("game");
    dealNext();
  });

  menuBtn.addEventListener("click", () => {
    showScreen("setup");
  });

  reshuffleBtn.addEventListener("click", () => {
    startGame();
  });

  backToSetupBtn.addEventListener("click", () => {
    showScreen("setup");
  });

  // ---------------- Init ----------------

  loadPlayers();
  renderPlayers();
  showScreen("setup");
})();
