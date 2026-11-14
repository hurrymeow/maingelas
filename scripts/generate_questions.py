#!/usr/bin/env python3
"""Generates js/questions.js with 1000 party-game prompts.

Tokens {player} and {player2} are resolved at runtime in the browser,
picking a random player from the current game's name list.
"""
import json
import os
import random

random.seed(42)

questions = []


def add(text, category, players=0):
    questions.append({"text": text, "category": category, "players": players})


# ---------------------------------------------------------------------------
# 1. Straight sip actions
# ---------------------------------------------------------------------------
sip_solo_templates = [
    "{player}, take {n} sip{s}.",
    "{player}, take {n} sip{s}, no questions asked.",
    "{player}, finish {n} sip{s} in a row without stopping.",
    "{player}, take {n} sip{s} and stare at the ceiling while you do it.",
]
for n in [1, 2, 3, 4]:
    s = "s" if n != 1 else ""
    for t in sip_solo_templates:
        text = t.replace("{n}", str(n)).replace("{s}", s)
        add(text, "drink", 1)

give_templates = [
    "Give %n sip%s to {player}.",
    "Give %n sip%s to the person on your left.",
    "Give %n sip%s to the person on your right.",
    "Give %n sip%s to whoever is closest to you.",
    "Give %n sip%s to {player} and tell them why they deserve it.",
    "Distribute %n sip%s however you like among the group.",
]
for n in [1, 2, 3, 5]:
    s = "s" if n != 1 else ""
    for t in give_templates:
        players = 1 if "{player}" in t else 0
        text = t.replace("%n", str(n)).replace("%s", s)
        add(text, "give", players)

everyone_templates = [
    "Everyone drinks {n} sip{s}.",
    "Everyone drinks {n} sip{s} except the person who read this card.",
    "Everyone drinks {n} sip{s}, cheers first.",
]
for n in [1, 2, 3]:
    s = "s" if n != 1 else ""
    for t in everyone_templates:
        add(t.format(n=n, s=s), "group")

add("{player} takes 2 sips for being the last one to raise their hand.", "drink", 1)
add("{player} chooses someone to finish their drink... just kidding, take 3 sips instead.", "drink", 1)
add("{player} and {player2} both take 2 sips.", "drink", 2)
add("{player} and {player2} have a staring contest. Loser drinks 3 sips.", "dare", 2)
add("Make eye contact with {player} for 10 seconds without laughing, or drink 2 sips.", "dare", 1)
add("{player} picks two people to do a shot / take 3 sips each.", "give", 1)

# ---------------------------------------------------------------------------
# 2. "Everyone who ___ drinks" group triggers
# ---------------------------------------------------------------------------
conditions = [
    "has a pet", "has been to another country", "is wearing socks",
    "has a sibling", "has kissed someone in this room", "has cried this week",
    "has a tattoo", "has broken a bone", "has sung karaoke",
    "has a piercing other than ears", "has ghosted someone",
    "has stalked an ex on social media this month", "has fallen asleep in public",
    "has lied to get out of plans", "has a crush on someone in this room",
    "has laughed at something inappropriate", "has more than three houseplants",
    "has sent a text to the wrong person", "has pretended to be sick to skip work or school",
    "has been dumped over text", "has stolen something small",
    "has cried during a movie", "has forgotten someone's name right after meeting them",
    "has sung in the shower today", "has a savings account under $100",
    "has never been on a plane", "has read a book for fun this year",
    "has more than 5 unread emails right now", "is the oldest sibling",
    "is the youngest sibling", "is an only child", "has bitten their nails this week",
    "has snooped through a partner's phone", "has left a party without saying bye",
    "has danced in front of a mirror", "has talked to a pet like it's a person",
    "has pretended to know a song they didn't", "has googled themselves",
    "has fallen down stairs",
    "has walked into a glass door", "has texted an ex recently",
    "has more than 3 apps for dating", "has cheated on a test",
    "has skipped a class or meeting to nap", "has cried happy tears this year",
    "has been on a reality TV show application",
    "has laughed so hard they cried",
    "has never had a broken heart", "has more than 10 unread texts right now",
    "has slept through an alarm for something important",
    "has been called their parent's name by accident", "has pretended to like a gift",
    "has drunk-texted someone", "has snorted while laughing",
    "has been the last one picked for a team",
    "has sung happy birthday off-key on purpose", "has cancelled plans to stay in",
    "has taken a selfie in the last hour",
    "has bought something just because it was on sale", "has forgotten their own phone number",
    "has cried during a Pixar movie", "has more than one email address",
    "has pretended to be busy to avoid someone",
    "has never broken a bone",
    "has laughed at their own joke before finishing it",
]
group_subjects = ["Whoever", "The one who"]
for i, cond in enumerate(conditions):
    verb = cond.split(" ", 1)[0]  # every condition starts with "has" or "is"
    neg_verb = "hasn't" if verb == "has" else "isn't"
    # Conditions already phrased in the negative ("has never...") would
    # double-negate into nonsense if flipped, so those always stay affirmative.
    can_flip = "never" not in cond
    # 4 variants per condition (not the full 3x3 cross product) to keep
    # this category from dominating the deck. Roughly half flip which
    # answer drinks, so players can't assume "yes" always costs a sip.
    for j, n in enumerate([1, 2, 3, 4]):
        s = "s" if n != 1 else ""
        subject = group_subjects[(i + j) % len(group_subjects)]
        flip = can_flip and (i + j) % 2 == 0
        v = neg_verb if flip else verb
        add(f"Who {cond}? {subject} {v}, drinks {n} sip{s}.", "group")

# ---------------------------------------------------------------------------
# 2b. Share & vote rounds — everyone reveals something, group votes, the
# winner (most votes) drinks. Reserved for prompts that are genuinely
# personal/subjective; plain yes-or-no facts stay in the group section above.
# ---------------------------------------------------------------------------
vote_prompts = [
    ("says their weirdest phobia", "the weirdest one"),
    ("shares a nickname they hate", "the worst one"),
    ("shares a food they refuse to try", "the weirdest"),
    ("shares their most obvious celebrity crush", "the most surprising"),
    ("reveals a secret talent", "the most useless"),
    ("tells the story behind a scar", "the best story"),
    ("shares a guilty pleasure TV show", "the most embarrassing"),
    ("does 3 seconds of an impression", "the worst one"),
    ("shares a playlist name they've made", "the funniest"),
    ("shares a conspiracy theory they secretly believe", "the wildest"),
]
for share, adj in vote_prompts:
    for n in [1, 2]:
        s = "s" if n != 1 else ""
        add(f"Everyone {share}. Vote for {adj}. Most votes drinks {n} sip{s}.", "vote")

# ---------------------------------------------------------------------------
# 3. "Name a ___, last person drinks" category rounds
# ---------------------------------------------------------------------------
categories_list = [
    "movie", "country", "animal", "celebrity", "food", "type of alcohol",
    "superhero", "song", "sport", "TV show", "phone app", "color",
    "brand of shoe", "dance move", "ice cream flavor", "holiday",
    "board game", "Disney movie", "2000s song", "fast food chain",
    "horror movie", "cartoon character", "city", "pizza topping",
    "candy bar", "video game", "dog breed", "car brand", "soda brand",
    "musical instrument", "swear word", "emoji", "breakfast food",
    "school subject", "job", "planet", "body part", "type of dance",
    "kitchen appliance", "sports team", "type of cheese", "action movie star",
    "boy band", "girl group", "cocktail", "reality TV show", "cereal brand",
    "type of pasta", "summer activity", "winter activity",
    "type of sandwich", "amusement park ride", "type of weather",
    "comic book character", "type of hat", "kitchen utensil",
    "type of tree", "wrestling move", "type of soup", "dance style",
    "type of jacket", "type of hairstyle", "punk or rock band",
    "children's cartoon", "type of tea", "gym exercise", "type of key on a keyboard",
]
category_templates = [
    "{{player}} starts. Name a {cat}. Go around the group — first to repeat or hesitate drinks.",
    "{{player}} goes first. Everyone names a {cat} in turn. Last person to answer drinks 2 sips.",
    "Category round: {cat}. {{player}} starts. First person who can't think of one drinks 3 sips.",
]
for cat in categories_list:
    for t in category_templates:
        add(t.format(cat=cat), "category", 1)

# ---------------------------------------------------------------------------
# 4. Never have I ever
# ---------------------------------------------------------------------------
never_statements = [
    "gone skinny dipping", "been in a fist fight", "cheated on a partner",
    "been caught sneaking out", "lied about your age", "gone streaking",
    "stolen a street sign", "been fired from a job", "called in sick to go to a party",
    "kissed someone in this room", "had a crush on a friend's ex",
    "been kicked out of a bar or club", "faked an illness to avoid a date",
    "gone on a blind date", "been dumped on your birthday",
    "sent a risky text to the wrong person", "cried in front of a stranger",
    "danced on a table", "gone to school or work still drunk",
    "had a one night stand", "used a fake ID", "peed in a pool",
    "been in a car accident", "cheated on a test in school",
    "stalked someone on social media for hours", "ghosted someone you dated",
    "been catfished", "lied on a resume", "walked out on a bill",
    "regifted a present", "thrown up in public", "fallen asleep at work",
    "gotten a tattoo you regret", "been arrested or held by police",
    "snuck into a movie without paying", "had a threesome",
    "made out with a stranger", "been so drunk you forgot the night",
    "cried during a commercial", "pretended to be someone else online",
    "hooked up with a friend's sibling", "lied to your parents about where you were",
    "eaten food off the floor", "had a crush on a teacher",
    "been late to your own event", "gone commando to a public place",
    "broken a bone doing something stupid", "pretended to understand a joke you didn't get",
    "gotten lost in your own city", "sent a text meant for someone else to the wrong person",
    "laughed so hard you peed a little", "been the reason a party ended early",
    "hidden from someone at a store to avoid talking", "eaten an entire pizza alone",
    "told a lie that spiraled out of control", "pretended to be on the phone to avoid someone",
    "gone through a partner's phone without asking", "cried over a TV show character dying",
    "double-booked plans and ditched one", "been so nervous you threw up",
    "forgotten a friend's birthday", "gone to a party uninvited",
    "lied about liking a gift", "had a secret social media account",
    "been in the wrong place at the wrong time", "walked into traffic while texting",
    "accidentally liked an old photo while stalking someone",
    "cried happy tears at a wedding", "gone home with someone whose name you didn't know",
    "had a wardrobe malfunction in public", "pretended to be sick to avoid a family event",
    "spent an entire paycheck in one day", "fallen for a prank on April Fools' Day",
    "sung karaoke horribly on purpose", "gotten a speeding ticket",
    "snuck alcohol into an event", "made a fake social media profile",
    "been dumped by text message", "had a crush on a cartoon character",
    "eaten a whole tub of ice cream in one sitting", "lied about your whereabouts to a partner",
    "gone to work or school with a hangover", "pretended not to see someone to avoid them",
    "cheated in a board game", "cried while watching a sports game",
    "gotten so lost you had to ask for directions", "forgotten someone's name mid-introduction",
    "stayed in a relationship you knew was over", "had a crush on more than one person at once",
    "accidentally sent a text to a group chat instead of one person",
    "pretended to be an expert on something you knew nothing about",
    "danced in public without music playing", "worn the same outfit two days in a row on purpose",
    "eaten dessert before dinner", "skipped a meal just to save calories for drinking",
    "gone to a concert alone", "fallen in love at first sight",
    "had a friendship end over something small", "been the third wheel and hated it",
    "pretended to laugh at a joke that wasn't funny", "spent more than an hour picking an outfit",
    "cried because you were hungry", "had a really embarrassing autocorrect fail",
    "told a white lie to avoid a plan", "binge-watched a show in one sitting",
    "shown up to an event in the completely wrong outfit", "left the house with mismatched shoes",
    "forgotten you already told someone a story", "taken a nap that ruined your whole night's sleep",
    "accidentally called a teacher or boss 'mom' or 'dad'",
    "had a crush on someone way older or younger than you",
    "gotten way too competitive over a board game", "cried at an award show",
    "pretended to be busy on a night you had nothing to do",
    "gone through with a plan you regretted the whole time",
    "sent flirty texts to the wrong chat", "laughed at a funeral by accident",
    "made a scene in public over something small", "gone a full day without checking your phone",
    "had a secret handshake with a friend", "pretended to know a language you don't speak",
    "stayed friends with someone you probably shouldn't have",
    "shown up somewhere on the completely wrong day", "kept a pet's death a secret from someone",
    "eaten something after the expiration date on purpose", "fallen asleep during a movie in theaters",
    "had a crush on your best friend's partner", "cried tears of laughter until it hurt",
]
never_templates = [
    "Have you ever {s}? If you have, take {n} sip{s2}.",
    "Have you ever {s}? If you have not, take {n} sip{s2}.",
]
for s in never_statements:
    for i, t in enumerate(never_templates):
        n = 2 if i == 0 else 3
        s2 = "s" if n != 1 else ""
        add(t.format(s=s, n=n, s2=s2), "neverhave")

# ---------------------------------------------------------------------------
# 5. Dares / light truths (non-hazardous, party-appropriate)
# ---------------------------------------------------------------------------
dares = [
    "Do your best impression of a celebrity until your next turn.",
    "Text the last person you called and tell them a random fun fact.",
    "Let the group scroll your camera roll for 10 seconds.",
    "Sing the chorus of a song the group picks for you.",
    "Do 10 jumping jacks right now.",
    "Speak in an accent chosen by the group until your next turn.",
    "Let someone draw a small doodle on your hand.",
    "Tell the group the most-used emoji in your recent texts.",
    "Do your best dance move for 15 seconds.",
    "Let the group pick your profile picture for the next hour.",
    "Talk in a whisper until your next turn.",
    "Do an impression of another player until someone guesses who.",
    "Hold a plank for 20 seconds or drink 3 sips.",
    "Let the person to your left post anything on your story (with your ok).",
    "Try to make the group laugh without using words.",
    "Recite the alphabet backwards or drink 3 sips.",
    "Do your best robot dance for 10 seconds.",
    "Tell a joke. If nobody laughs, drink 2 sips.",
    "Balance a cup on your head for 15 seconds.",
    "Let the group choose your nickname for the next 15 minutes.",
    "Do an interpretive dance of the last movie you watched.",
    "Speak only in questions until your next turn.",
    "Show the group the last photo in your camera roll.",
    "Do your best impression of the person to your right.",
    "Try to lick your elbow.",
    "Hum a song and have the group guess it.",
    "Talk like a pirate until your next turn.",
    "Do your best cat impression.",
    "Give a 15 second motivational speech to the group.",
    "Trade seats with someone for the rest of the round.",
    "Let the group pick a silly walk for you to do across the room.",
    "Make up a two-line rap about the person to your left.",
    "Do your best news anchor voice for your next sentence.",
    "Act out your favorite movie scene without speaking.",
    "Try to draw the room with your eyes closed.",
    "Do 5 push-ups or drink 3 sips.",
    "Freeze in place until your next turn, or drink 3 sips.",
    "Say the last text you sent out loud.",
    "Let someone else answer your phone if it rings this round.",
    "Do your best impression of a game show host.",
    "Tell the group an unpopular opinion you have.",
    "Share the weirdest dream you remember.",
    "Describe your perfect day in 10 words or less.",
    "Share your most-used app this week.",
    "Say the alphabet while patting your head and rubbing your stomach.",
    "Do your best beatbox for 10 seconds.",
    "Let the group rename you for the next 15 minutes.",
    "Try to whistle a tune for the group to guess.",
    "Share your most played song this month.",
    "Do your best impression of a baby.",
    "Tell the group about your first celebrity crush.",
    "Answer the next 3 questions in a movie-trailer voice.",
    "Let the group pick your next drink order (non-alcoholic is fine).",
    "Do a 10 second freestyle rap about drinking games.",
    "Wear something backwards for the next round.",
    "Try to touch your nose with your tongue.",
    "Tell the group your most embarrassing childhood nickname.",
    "Do your best impression of your favorite cartoon character.",
    "Share the last thing you searched online (keep it clean).",
    "Say three truths and one lie — group guesses the lie.",
    "Tell the group about a time you got in trouble as a kid.",
    "Do your best slow-motion action scene.",
    "Try to say a tongue twister three times fast.",
    "Share your go-to karaoke song.",
    "Do your best impression of an announcer at a sports game.",
    "Let the group choose a silly hashtag for your night.",
    "Share the most useless talent you have.",
    "Do a dramatic reading of a text from your phone.",
    "Try to snap and whistle at the same time.",
    "Share the last lie you told and why.",
    "Do your best superhero pose and hold it for 10 seconds.",
    "Tell the group your comfort food.",
    "Share a fun fact nobody in the room probably knows.",
    "Do your best villain laugh.",
    "Try to name 5 movies in 10 seconds.",
    "Share your most irrational fear.",
    "Do your best impression of a news reporter covering this party.",
    "Tell the group the last show you binge-watched.",
    "Let the group pick your walk-up song for the rest of the night.",
    "Share a hobby you wish you had time for.",
    "Do your best dramatic movie trailer voice-over for this room.",
    "Try to make everyone laugh with just your facial expressions.",
    "Share your zodiac sign and one trait that fits you perfectly.",
    "Do your best runway walk across the room.",
    "Tell the group the weirdest food combo you enjoy.",
    "Share the last concert or show you went to.",
    "Do your best impersonation of someone else in the room, no naming names.",
    "Do your best impression of a weather reporter mid-storm.",
    "Try to juggle two objects from the table for 10 seconds.",
    "Do your best impression of a toddler having a tantrum.",
    "Share the most awkward first date you've been on.",
    "Do your best slow clap for the person to your right.",
    "Try to name every player's middle name — 2 sips per one you miss.",
    "Do your best impression of a golf commentator narrating this game.",
    "Share the worst haircut you've ever had.",
    "Do your best impression of a Shakespearean actor for your next sentence.",
    "Try to draw your own face on a napkin in 15 seconds.",
    "Do your best impression of someone waking up hungover.",
    "Share a New Year's resolution you already broke.",
    "Do your best impression of an infomercial host selling the drink in your hand.",
    "Try to keep a straight face while everyone else makes funny faces at you for 10 seconds.",
    "Share the most trouble you ever got into at school.",
    "Do your best impression of a nature documentary narrator describing this room.",
    "Try to recite your phone number backwards.",
    "Do your best impression of a diva storming off stage.",
    "Share your most-used text abbreviation.",
    "Do your best impression of a coach giving a halftime speech.",
    "Try to stack 3 cups into a pyramid one-handed in 15 seconds.",
    "Share the last white lie you told a friend.",
    "Do your best impression of someone trying not to laugh.",
    "Share the most overrated movie you've ever watched.",
    "Do your best impression of a substitute teacher taking attendance.",
]
for d in dares:
    add("{player}: " + d, "dare", 1)

# ---------------------------------------------------------------------------
# 6. Make-a-rule cards
# ---------------------------------------------------------------------------
rules = [
    "No pointing with your left hand for the next 15 minutes.",
    "Everyone must say 'cheers' before drinking for the next 15 minutes.",
    "No saying anyone's real name until your next turn — use nicknames only.",
    "Every sentence must end with 'friend' until your next turn.",
    "No crossing your legs for the rest of the round.",
    "Everyone must drink with their non-dominant hand for the next 15 minutes.",
    "No one can say 'drink' out loud for the next 15 minutes.",
    "Everyone must clink cups before every sip from now on.",
    "No phones on the table for the rest of the round — first to break it drinks.",
    "Everyone must raise their pinky when drinking for the next 15 minutes.",
    "No saying 'I' — say your own name instead, until your next turn.",
    "Everyone must stand up before they drink for the rest of the round.",
    "No laughing allowed for the next 2 minutes — first to laugh drinks.",
    "Everyone must whisper for the rest of the round.",
    "No one can use first names for the next 15 minutes — nicknames only.",
    "Everyone has to end questions with 'if you please' until your next turn.",
    "No pointing at the group with fingers — elbows only, for the rest of the round.",
    "Everyone must toast the group before drinking for the next 15 minutes.",
    "No saying 'yes' or 'no' — find another way, until your next turn.",
    "Everyone has to drink left-handed for the next 15 minutes.",
    "Everyone must give a toast title to every round for the next 15 minutes.",
    "No one may say 'okay' for the rest of the round.",
    "Everyone must knock on the table twice before drinking, for the next 15 minutes.",
    "No sitting down for the rest of the round — everyone stands.",
    "Everyone must high-five the group before drinking, for the rest of the round.",
    "No using phones for the rest of the round.",
    "Everyone must speak one octave higher for the rest of the round.",
    "No repeating a sip count out loud — mime it instead, for the next 15 minutes.",
    "Everyone must hold their cup with both hands for the rest of the round.",
    "No saying 'drink' or 'sip' — invent a new word for it, for the next 15 minutes.",
    "Everyone must wink before their turn for the rest of the round.",
    "No leaning back in your chair for the rest of the round.",
    "Everyone must count their sips out loud for the next 15 minutes.",
    "No using anyone's name — point and describe them instead, for the rest of the round.",
    "Everyone must applaud after every card is read, for the next 15 minutes.",
    "No touching your face for the rest of the round.",
    "Everyone must say the previous player's drink order before their turn, for the next 15 minutes.",
    "No crossing your arms for the rest of the round.",
    "Everyone must end every sentence with 'no cap' for the rest of the round.",
    "No standing during your turn for the rest of the round — sit only.",
]
for r in rules:
    add(f"{{player}} makes a new rule: {r} Whoever breaks it drinks.", "rule", 1)

# ---------------------------------------------------------------------------
# 7. Special mechanic cards
# ---------------------------------------------------------------------------
specials = [
    "Waterfall: the reader starts drinking, then each person in turn starts. No one can stop until the person before them stops.",
    "{player} is the Thumb Master: at any point, they put their thumb on the table. Last person to copy them drinks 2 sips. Stays in effect until someone else draws this card.",
    "{player} is the Question Master: until their next turn, if anyone answers a question they ask, they drink 2 sips.",
    "Categories: pick a topic and go around the group naming things in it. First to repeat or blank drinks.",
    "Rhyme Time: pick a word. Go around the group rhyming with it. First to fail drinks.",
    "Bust a Move: everyone must dance for 10 seconds. Last one dancing drinks.",
    "Snake Eyes: keep eye contact with someone. If they look away first, they drink 2 sips.",
    "Mirror Round: pick a player to copy every move you make until your next turn, or they drink.",
    "Freeze: everyone must freeze in place for 10 seconds. First to move drinks 2 sips.",
    "Countdown: count down from 10 as a group without two people talking at once. If it breaks, restart and everyone drinks 1.",
    "Silent Round: no talking allowed until your next turn. First to speak drinks 2 sips.",
    "Accent Round: everyone must speak in a chosen accent until the next card. First to slip up drinks.",
    "Left Hand Only: everyone drinks with their left hand until your next turn.",
    "Reverse Round: play now moves in the opposite direction until someone draws this card again.",
    "Double Trouble: the next card is worth double sips for everyone.",
    "Rule Breaker: pick one active rule in play and cancel it immediately.",
    "Speed Round: the next 3 cards get read back to back with no discussion.",
    "Copycat: everyone must repeat the last player's sentence word for word or drink 2 sips.",
    "Alliance: pick a partner. You share sips for the rest of the round.",
    "Time Out: pause the game for 30 seconds. Whoever talks first drinks 2 sips.",
]
for sp in specials:
    players = 1 if "{player}" in sp else 0
    add(sp, "special", players)

# ---------------------------------------------------------------------------
# 8. Two-player prompts
# ---------------------------------------------------------------------------
two_player_conditions = [
    "who has known the group the longest", "who is wearing the most colorful outfit",
    "who has the most siblings", "who has traveled the furthest to be here",
    "who has the messiest room", "who is the better cook",
    "who is more likely to survive a zombie apocalypse", "who has the best singing voice",
    "who would win in an arm wrestle", "who is more likely to become famous",
    "who has the better dance moves", "who tells the funniest jokes",
    "who is more likely to cry during a movie", "who has the wildest party story",
    "who is more competitive", "who gives the best advice",
    "who is more likely to forget a birthday", "who has the best fashion sense",
    "who would survive longest without their phone", "who is the most likely to talk their way out of trouble",
]
versus_templates = [
    "The group decides: {{player}} or {{player2}}, {cond}? Loser drinks {n} sip{s}.",
    "{{player}} vs {{player2}} — {cond}? Group votes, loser drinks {n} sip{s}.",
]
for cond in two_player_conditions:
    for n in [2, 3]:
        s = "s" if n != 1 else ""
        t = versus_templates[n % 2]
        add(t.format(cond=cond, n=n, s=s), "versus", 2)

# ---------------------------------------------------------------------------
# Dedupe + trim/pad to exactly 1000
# ---------------------------------------------------------------------------
seen = set()
unique = []
for q in questions:
    if q["text"] not in seen:
        seen.add(q["text"])
        unique.append(q)

random.shuffle(unique)

print(f"Generated {len(unique)} unique questions before trim.")

if len(unique) < 1000:
    raise SystemExit(f"Not enough questions: {len(unique)} < 1000")

final = unique[:1000]

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "js", "questions.js"), "w") as f:
    f.write("// Auto-generated by scripts/generate_questions.py — do not hand-edit.\n")
    f.write("// {player} / {player2} are replaced at runtime with random players.\n")
    f.write("const QUESTIONS = ")
    f.write(json.dumps(final, indent=2, ensure_ascii=False))
    f.write(";\n")

print(f"Wrote {len(final)} questions to js/questions.js")
