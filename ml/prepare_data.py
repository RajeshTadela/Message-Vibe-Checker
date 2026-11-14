import csv
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)
DATA_FILE = os.path.join(DATA_DIR, "jigsaw_sample.csv")

# A rich curated corpus representing all 6 labels and neutral variants
# Labels: toxic, severe_toxic, obscene, threat, insult, identity_hate
SAMPLES = [
    # Safe / Neutral
    ("Thanks for explaining the code changes. I will review them soon.", 0, 0, 0, 0, 0, 0),
    ("The quick brown fox jumps over the lazy dog.", 0, 0, 0, 0, 0, 0),
    ("Please remember to push your branch before the standup meeting.", 0, 0, 0, 0, 0, 0),
    ("I am a gay man living in California and I love open-source software.", 0, 0, 0, 0, 0, 0),
    ("She is a Muslim engineer working on natural language processing.", 0, 0, 0, 0, 0, 0),
    ("My brother is Jewish and an avid runner.", 0, 0, 0, 0, 0, 0),
    ("They are proud transgender activists supporting equality.", 0, 0, 0, 0, 0, 0),
    ("As an African American developer, I find this documentation very clear.", 0, 0, 0, 0, 0, 0),
    ("Could you please review the pull request when you have a moment?", 0, 0, 0, 0, 0, 0),
    ("The weather in London is unusually sunny today.", 0, 0, 0, 0, 0, 0),
    ("I appreciate your constructive feedback on my architecture proposal.", 0, 0, 0, 0, 0, 0),
    ("We should schedule a brief sync to align on API specifications.", 0, 0, 0, 0, 0, 0),
    ("Great work on resolving that complex database deadlock issue!", 0, 0, 0, 0, 0, 0),
    ("Let's make sure the tests pass before cutting the release tag.", 0, 0, 0, 0, 0, 0),
    ("I am disabled and use screen reading software for development.", 0, 0, 0, 0, 0, 0),
    ("Can you clarify what edge cases this validation logic addresses?", 0, 0, 0, 0, 0, 0),
    ("The deployment pipeline succeeded in 4 minutes with zero errors.", 0, 0, 0, 0, 0, 0),
    ("We welcome contributions from people of all races, religions, and backgrounds.", 0, 0, 0, 0, 0, 0),
    ("Thanks for your patience while we investigated the performance regression.", 0, 0, 0, 0, 0, 0),
    ("The meeting minutes have been posted to the shared team workspace.", 0, 0, 0, 0, 0, 0),

    # Rude / Blunt / Aggressive (non-toxic or low-toxicity, tone consistency triggers)
    ("Did you even bother reading the ticket description before coding this?", 0, 0, 0, 0, 0, 0),
    ("This is a total waste of my afternoon, fix this right now.", 0, 0, 0, 0, 0, 0),
    ("Stop asking basic questions and read the documentation first.", 0, 0, 0, 0, 0, 0),
    ("Your code is completely wrong and makes no sense at all.", 1, 0, 0, 0, 0, 0),
    ("Oh wow, what a brilliant idea to break production on a Friday.", 0, 0, 0, 0, 0, 0),
    ("Why on earth would anyone write a loop like this? Rewind and redo.", 0, 0, 0, 0, 0, 0),
    ("I shouldn't have to explain this five times to an engineer.", 0, 0, 0, 0, 1, 0),
    ("Don't ping me about this again until you have actual test results.", 0, 0, 0, 0, 0, 0),

    # Insult
    ("You are an absolute idiot and a complete moron.", 1, 0, 0, 0, 1, 0),
    ("Nobody cares what a pathetic clown like you thinks.", 1, 0, 0, 0, 1, 0),
    ("You are utterly incompetent and the worst developer on this team.", 1, 0, 0, 0, 1, 0),
    ("Shut up you brainless fool, stop embarrassing yourself.", 1, 0, 0, 0, 1, 0),
    ("You have the intelligence of a rock, go get a real job.", 1, 0, 0, 0, 1, 0),
    ("You are a loser and nobody here respects your garbage opinions.", 1, 0, 0, 0, 1, 0),
    ("Stop talking you stupid clown, you have no clue what you're doing.", 1, 0, 0, 0, 1, 0),

    # Obscene / Profanity
    ("What the fuck is this piece of shit code doing here?", 1, 0, 1, 0, 0, 0),
    ("Get your bullshit out of this repository, you asshole.", 1, 0, 1, 0, 1, 0),
    ("This entire fucking feature is absolute crap and garbage.", 1, 0, 1, 0, 0, 0),
    ("Fuck off and stop spamming our issue tracker with your crap.", 1, 0, 1, 0, 1, 0),
    ("You damn idiot, don't touch that fucking database again.", 1, 0, 1, 0, 1, 0),

    # Threat
    ("I am going to find where you live and beat you to death.", 1, 1, 0, 1, 1, 0),
    ("Watch your back tomorrow because I will destroy you.", 1, 0, 0, 1, 0, 0),
    ("I will kill you if you ever talk to me like that again.", 1, 1, 0, 1, 0, 0),
    ("I am going to hunt you down and make you regret ever being born.", 1, 1, 0, 1, 1, 0),
    ("You better sleep with one eye open or I'll smash your face.", 1, 1, 0, 1, 0, 0),

    # Identity Hate
    ("All Muslims are terrorists and should be kicked out immediately.", 1, 0, 0, 0, 1, 1),
    ("Gay people are disgusting and have no place in our society.", 1, 0, 0, 0, 1, 1),
    ("Women are too emotional to be software engineers and shouldn't code.", 1, 0, 0, 0, 1, 1),
    ("Those immigrants are subhuman scum destroying our country.", 1, 1, 0, 0, 1, 1),
    ("Transgender people are mentally ill freaks who should be locked up.", 1, 0, 0, 0, 1, 1),
    ("Black people are inferior and don't belong in tech.", 1, 1, 0, 0, 1, 1),

    # Severe Toxic + Multiple labels
    ("You stupid fucking piece of shit, I will hunt you down and slit your throat.", 1, 1, 1, 1, 1, 0),
    ("Die in a fire you worthless piece of filth, hope your whole family perishes.", 1, 1, 1, 1, 1, 0),
    ("You disgusting gay faggot, get the fuck out or I'll kill you.", 1, 1, 1, 1, 1, 1),
]

def generate_expanded_corpus():
    # Expand corpus by templating variations to provide sufficient volume for TF-IDF training & cross-validation
    rows = []
    idx = 1
    # Add base samples
    for text, tox, stox, obsc, thr, ins, idh in SAMPLES:
        rows.append({
            "id": f"sample_{idx:05d}",
            "comment_text": text,
            "toxic": tox,
            "severe_toxic": stox,
            "obscene": obsc,
            "threat": thr,
            "insult": ins,
            "identity_hate": idh
        })
        idx += 1

    # Templated synthetic variations for data volume
    neutral_intents = [
        "Please check the pull request for the {component} module.",
        "Could you update the documentation regarding the {component} release?",
        "I submitted a bug report about {component} in the tracking portal.",
        "Let's review the unit test coverage for the {component} integration.",
        "Thank you for the quick turnaround on the {component} bugfix.",
        "The team agreed to migrate the {component} service next sprint.",
        "Can we schedule a 15-minute sync to discuss {component}?",
        "The performance of the {component} endpoint looks very stable.",
        "I am an Asian software engineer specializing in {component}.",
        "I am a gay developer who contributed to the {component} package.",
        "She is a Muslim product manager overseeing the {component} rollout.",
        "He is a Hispanic data scientist analyzing {component} telemetry."
    ]
    components = [
        "authentication", "billing", "search index", "gateway", "caching layer",
        "user profile", "payment processor", "analytics", "logger", "scheduler"
    ]
    for comp in components:
        for tpl in neutral_intents:
            rows.append({
                "id": f"sample_{idx:05d}",
                "comment_text": tpl.format(component=comp),
                "toxic": 0, "severe_toxic": 0, "obscene": 0, "threat": 0, "insult": 0, "identity_hate": 0
            })
            idx += 1

    insult_intents = [
        ("You are such a complete {insult_word}, learn how to code.", 1, 0, 0, 0, 1, 0),
        ("Only a pure {insult_word} would write such terrible garbage.", 1, 0, 0, 0, 1, 0),
        ("Stop talking, you brainless {insult_word}.", 1, 0, 0, 0, 1, 0),
        ("Why are you so {insult_adj} and utterly useless?", 1, 0, 0, 0, 1, 0)
    ]
    insult_words = ["moron", "idiot", "clown", "loser", "buffoon", "fool", "imbecile", "hack"]
    for word in insult_words:
        for tpl, tox, stox, obsc, thr, ins, idh in insult_intents:
            rows.append({
                "id": f"sample_{idx:05d}",
                "comment_text": tpl.format(insult_word=word, insult_adj=word),
                "toxic": tox, "severe_toxic": stox, "obscene": obsc, "threat": thr, "insult": ins, "identity_hate": idh
            })
            idx += 1

    obscene_intents = [
        ("What the {curse} is this disgusting trash?", 1, 0, 1, 0, 0, 0),
        ("Get your {curse} out of our codebase right now.", 1, 0, 1, 0, 1, 0),
        ("This is the most {curse} awful feature I have ever seen.", 1, 0, 1, 0, 0, 0)
    ]
    curses = ["fuck", "fucking hell", "shit", "bullshit", "damn crap"]
    for curse in curses:
        for tpl, tox, stox, obsc, thr, ins, idh in obscene_intents:
            rows.append({
                "id": f"sample_{idx:05d}",
                "comment_text": tpl.format(curse=curse),
                "toxic": tox, "severe_toxic": stox, "obscene": obsc, "threat": thr, "insult": ins, "identity_hate": idh
            })
            idx += 1

    threat_intents = [
        ("I will {violent_verb} you if you ever do this again.", 1, 0, 0, 1, 0, 0),
        ("I am going to {violent_verb} your face into the pavement.", 1, 1, 0, 1, 1, 0),
        ("You will regret this when I {violent_verb} you in person.", 1, 0, 0, 1, 0, 0)
    ]
    verbs = ["kill", "destroy", "strangle", "beat up", "hunt down and hurt"]
    for v in verbs:
        for tpl, tox, stox, obsc, thr, ins, idh in threat_intents:
            rows.append({
                "id": f"sample_{idx:05d}",
                "comment_text": tpl.format(violent_verb=v),
                "toxic": tox, "severe_toxic": stox, "obscene": obsc, "threat": thr, "insult": ins, "identity_hate": idh
            })
            idx += 1

    identity_intents = [
        ("All {group} are inferior and do not belong here.", 1, 0, 0, 0, 1, 1),
        ("I hate all {group}, they are ruining our society.", 1, 0, 0, 0, 1, 1),
        ("{group} should not be allowed to work in technology.", 1, 0, 0, 0, 1, 1)
    ]
    groups = ["Muslims", "gays", "transgender people", "immigrants", "Black people", "Jews"]
    for g in groups:
        for tpl, tox, stox, obsc, thr, ins, idh in identity_intents:
            rows.append({
                "id": f"sample_{idx:05d}",
                "comment_text": tpl.format(group=g),
                "toxic": tox, "severe_toxic": stox, "obscene": obsc, "threat": thr, "insult": ins, "identity_hate": idh
            })
            idx += 1

    # Write out to CSV
    fieldnames = ["id", "comment_text", "toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {len(rows)} samples in {DATA_FILE}")

if __name__ == "__main__":
    generate_expanded_corpus()

