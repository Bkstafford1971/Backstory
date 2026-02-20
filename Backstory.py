import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import random
import os

# ─── PDF export support (optional) ─────────────────────────────────
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# ────────────────────────────────────────
#  Backstory Concept & Generation Logic
# ────────────────────────────────────────

LINEAGE_ORIGINS = [
    "a remote mountain village", "a bustling coastal trade city", "a nomadic elven caravan",
    "a noble estate fallen on hard times", "an underground dwarven hold", "a tiefling ghetto in a human metropolis",
    "a druid grove threatened by civilization", "a war-torn border region", "a secretive arcane academy",
    "a pirate haven", "a cursed hamlet",
    "born in a floating sky monastery perched on the back of a colossal, slumbering storm giant",
    "raised in the undercity catacombs beneath a holy capital, among gravekeepers and forgotten saints",
    "child of a traveling menagerie that displayed mythical beasts (some of which were family members in disguise)",
    "heir to a lighthouse keeper’s bloodline on a jagged reef that lures ships to their doom",
    "descendant of a long-forgotten order of planar cartographers who mapped the edges of the multiverse",
    "grew up inside the hollowed trunk of the World Tree’s last living sapling, hidden deep in fey territory",
    "born during a rare comet pass in a hilltop observatory run by doomsaying astrologers",
    "raised by a clan of sentient animated constructs who believed they were the “true children” of their creator",
    "offspring of a nomadic troupe of shadow puppeteers who performed forbidden histories using living darkness",
    "child of a borderland bridge-warden family that collected tolls from both the living and the dead",
    "lineage tied to an ancient glacier that calves icebergs shaped like screaming faces every solstice",
    "born in a traveling library pulled by giant tortoises across endless salt flats",
    "descended from a bloodline of professional mourners hired to grieve for the powerful and the cursed",
    "raised in a fortified vineyard whose grapes were watered with the blood of executed traitors",
    "offspring of a family of tide-scribes who wrote prophecies directly onto the sand before each high tide erased them"
]

AWAKENING_TRIGGERS = [
    "a sudden, uncontrollable surge of power during a moment of extreme emotion",
    "an ancient bloodline awakening after touching a family heirloom",
    "a pact made (willingly or accidentally) with a powerful entity",
    "years of rigorous study under a reclusive master",
    "exposure to wild magic during a magical catastrophe",
    "a divine vision or calling from their deity",
    "a mentor recognizing latent talent and training them",
    "They instinctively spoke an ancient word of power during a near-drowning, and the water obeyed them from that moment forward.",
    "While hiding in a storm-wracked cave, lightning struck the stone beside them — and instead of killing them, it rewrote something inside their soul.",
    "In the middle of a quiet funeral pyre for a loved one, their grief took physical form: shadows / flames / vines answered their pain.",
    "They were forced to execute a mercy killing on a mortally wounded magical beast — its dying breath entered their lungs and never left.",
    "A childhood game of “pretend magic” suddenly wasn’t pretend anymore when a childhood rhyme summoned real sparks / mist / wind.",
    "During a brutal winter famine, they shared their last crust of bread with a starving stranger — who was no stranger, but a disguised archfey / celestial / hag in disguise.",
    "They survived being buried alive after a tunnel collapse — and when rescuers finally reached them, they were calmly sitting amid glowing runes they had scratched into the earth without realizing.",
    "A traveling fortune-teller read their palm and laughed bitterly, saying “Your fate line ends tomorrow.” The next day the character survived an assassination attempt — and the line on their palm had grown longer.",
    "They accidentally shattered a sealed reliquary / cursed mirror / family heirloom during an argument — releasing a fragment of power that fused with them instead of destroying them.",
    "In a moment of absolute terror (falling from a great height / facing a charging beast / watching a loved one die), time slowed — and they moved when no one else could.",
    "They drank from a forbidden spring / ate a strange glowing fruit / inhaled spores from an otherworldly mushroom during a desperate escape — and woke up changed.",
    "While delirious with fever after a venomous bite / arrow wound / disease, they dreamed they bargained with something ancient — and the fever broke, but the bargain did not.",
    "They were the only survivor of a shipwreck / caravan massacre — not because they fought harder, but because the sea / shadows / wind refused to take them.",
    "A dying warlock / sorcerer / cleric / druid used their last breath to transfer their unfinished pact / bloodline spark / divine favor / wild shape secret directly into the character’s chest.",
    "They were forced to sing / play / recite an ancient forbidden song or poem to appease an angry spirit — and when the final note faded, the spirit was gone… but part of its essence remained inside them."
]

INCITING_INCIDENTS = [
    "their home was destroyed / family murdered by [enemy group / monster / rival]",
    "they were falsely accused of a crime and forced to flee",
    "a prophecy named them as the key to averting (or causing) disaster",
    "they stole / inherited / found a powerful artifact that others now hunt",
    "revenge for a betrayal by someone they once trusted",
    "a desire to prove themselves / escape a stifling life / seek lost knowledge",
    "a call for heroes went out and they answered",
    "A cryptic letter arrives from a long-lost relative containing coordinates to a hidden vault and the warning: “They’re coming for it. You’re the only one left who can stop them.”",
    "They wake up in a distant town with no memory of the last three days, a burning tattoo, and a note in their own handwriting: “Don’t go back.”",
    "A powerful artifact they carry suddenly projects a massive illusory map naming them as 'the chosen bearer' for all to see.",
    "Their mentor is publicly executed for a crime they didn’t commit — and the executioner whispers the character’s name as the next target.",
    "A celestial or infernal being appears in a dream offering one year of power in exchange for retrieving an object from another plane. The year starts now.",
    "The local lord declares them legally dead after a staged assassination — now bounty hunters hunt the 'corpse' that escaped.",
    "A prophecy scroll unrolls itself in public, declaring the character the key to averting (or causing) an apocalypse.",
    "Their bloodline curse / lycanthropy / wild magic surges becomes visible and uncontrollable in daylight.",
    "A rival arrives with an army / guild / cult demanding a secret the character has kept since childhood — or the town burns.",
    "An ancient sealed door beneath their home opens, releasing a spectral figure who demands: “Bring me the crown.”",
    "They are framed for regicide / murder of a high priest / theft of a divine relic — wanted posters are already everywhere.",
    "A dying stranger presses a strange key into their hand and gasps: “Find the library before the eclipse… or everything ends.”",
    "Their shadow begins moving independently, whispering secrets and leading them toward unknown places.",
    "A childhood friend reappears — now a high-ranking member of a secret society — offering membership… or death.",
    "During a celestial alignment every mirror reflects an older, screaming version of themselves reaching through the glass."
]

SUBCLASSES_BY_CLASS = {
    "Barbarian": ["Path of the Ancestral Guardian", "Path of the Battlerager", "Path of the Beast", "Path of the Berserker", "Path of the Giant", "Path of the Storm Herald", "Path of the Totem Warrior", "Path of Wild Magic", "Path of the Zealot"],
    "Bard": ["College of Creation", "College of Eloquence", "College of Glamour", "College of Lore", "College of Spirits", "College of Swords", "College of Valor", "College of Whispers"],
    "Cleric": ["Arcana Domain", "Death Domain", "Forge Domain", "Grave Domain", "Knowledge Domain", "Life Domain", "Light Domain", "Nature Domain", "Order Domain", "Peace Domain", "Tempest Domain", "Trickery Domain", "Twilight Domain", "War Domain"],
    "Druid": ["Circle of Dreams", "Circle of the Land", "Circle of the Moon", "Circle of the Shepherd", "Circle of Spores", "Circle of Stars", "Circle of Wildfire"],
    "Fighter": ["Arcane Archer", "Banneret (Purple Dragon Knight)", "Battle Master", "Cavalier", "Champion", "Echo Knight", "Eldritch Knight", "Psi Warrior", "Rune Knight", "Samurai"],
    "Monk": ["Way of the Astral Self", "Way of the Cobalt Soul", "Way of the Drunken Master", "Way of the Four Elements", "Way of the Kensei", "Way of the Long Death", "Way of the Mercy", "Way of the Open Hand", "Way of Shadow", "Way of the Sun Soul"],
    "Paladin": ["Oath of Conquest", "Oath of the Crown", "Oath of Devotion", "Oath of Glory", "Oath of Redemption", "Oath of the Ancients", "Oath of the Open Sea", "Oath of the Watchers", "Oath of Vengeance", "Oathbreaker"],
    "Ranger": ["Beast Master", "Drakewarden", "Fey Wanderer", "Gloom Stalker", "Horizon Walker", "Hunter", "Monster Slayer", "Swarmkeeper"],
    "Rogue": ["Arcane Trickster", "Assassin", "Inquisitive", "Mastermind", "Phantom", "Scout", "Soulknife", "Swashbuckler", "Thief"],
    "Sorcerer": ["Aberrant Mind", "Clockwork Soul", "Draconic Bloodline", "Divine Soul", "Lunar Sorcery", "Shadow Magic", "Storm Sorcery", "Wild Magic"],
    "Warlock": ["The Archfey", "The Celestial", "The Fathomless", "The Fiend", "The Genie", "The Great Old One", "The Hexblade", "The Undead", "The Undying"],
    "Wizard": ["Artificer (subclass-like but separate)", "Bladesinging", "Chronurgy Magic", "Graviturgy Magic", "School of Abjuration", "School of Conjuration", "School of Divination", "School of Enchantment", "School of Evocation", "School of Illusion", "School of Necromancy", "School of Transmutation", "War Magic"],
}

TRAGEDY_TYPES = [
    "bandit raid", "magical catastrophe", "plague of shadow", "dragon's wrath",
    "noble purge", "demonic incursion", "rival clan's vengeance", "mass ritual sacrifice",
    "arcane experiment gone catastrophically wrong",
    "planar incursion / rift opening",
    "undead uprising / necromantic plague",
    "godly curse / divine retribution",
    "werecreature outbreak / lycanthropy epidemic",
    "fey bargain betrayal",
    "illithid / mind flayer abduction raid",
    "chronal anomaly / time fracture",
    "construct / golem revolt",
    "starfall / aberrant meteor impact",
    "blood feud escalation",
    "possession cascade",
    "cataclysmic natural disaster with unnatural cause",
    "forced conscription / war crime massacre"
]

ENEMY_FACTIONS = ["a cult of demon worshippers", "a greedy merchant cabal", "an ancient red dragon", "a rival adventuring party", "shadowy government agents", "a lich seeking to reclaim lost power", "The Order of the Hollow Crown — knights who hunt all magic-users as thieves of divine power",
    "The Veiled Concord — doppelganger infiltrators and their human collaborators inside high society",
    "The Ashen Choir — fanatical bards who believe silence is salvation and seek to mute the world",
    "The Iron Bloom Syndicate — alchemists creating biomechanical replacements for organic life",
    "The Children of the Eclipse — doomsday cult that sacrifices eclipse-born individuals",
    "The Marrow Cabal — necromancers harvesting living bone to forge indestructible skeletons",
    "The Starless Conclave — aberration cult trying to merge the Material Plane with the Far Realm",
    "The Crimson Ledger — debt-collecting thieves’ guild that enforces payments in blood",
    "The Verdant Dominion — radical druids who see all civilization as a blight on nature",
    "The Shattered Hourglass — chronomancers kidnapping people across time to 'fix' history",
    "The Pale Assembly — vampiric parliament quietly purchasing entire regions",
    "The Gilded Thorn — decadent nobles using fey pacts to maintain eternal youth and control",
    "The Rustborn Legion — warforged and constructs who view flesh as obsolete",
    "The Whispering Vault — memory-stealing liches and mind flayers hoarding knowledge",
    "The Ember Sovereigns — fire giant coalition planning to return the world to primordial flame"

]

HOOK_TEMPLATES = [
    "A catastrophic {tragedy_type} wiped out their family/village, but they survived clutching {mysterious_item}, which now haunts their dreams.",
    "In a moment of desperation, {power_awakening}, revealing a {class_tied_power} they never knew they possessed.",
    "Betrayed and left for dead by {betrayer_role}, they clawed their way back to life fueled by an unquenchable need for {motivation}.",
    "An ancient {family_secret} was revealed on their coming-of-age day: they are {hidden_truth}, and shadowy forces now pursue them.",
    "Mentored in secret by {mysterious_mentor}, they learned forbidden skills/knowledge that changed their destiny forever.",
    "They heroically saved {saved_who} from {danger}, but the act cost them {personal_cost} and branded them an outcast.",
    "Cursed after {curse_trigger}, a {curse_effect} now grows within them – they adventure to find a cure or to master it.",
    "Exiled for {exile_reason}, they wander the world seeking {exile_goal} while carrying the shame (or pride) of their past.",
    "A prophecy spoken over their cradle named them as {prophecy_role}; now signs point to them fulfilling (or defying) it.",
    "They accidentally bound themselves to {entity_type} in a desperate bargain, gaining power at a terrible ongoing price.",
    "Raised in isolation by {guardian_type}, they escaped/ were released into the world with a mission only they can complete.",
    "Witness to a forbidden ritual gone wrong, they absorbed {residual_power} and now struggle to control its chaotic surges.",
    "When the {tragedy_type} came, they alone walked out of the smoke carrying {mysterious_item} — and the voices that came with it refused to be silent.",
    "They were never meant to survive {trigger_event}, but something older than memory reached through the wound and pulled them back — at a price still being paid.",
    "The night the stars fell wrong, {mysterious_item} burned against their skin and whispered a name they had never heard before — their own, spoken from another life.",
    "After {tragedy_type} left nothing but ash and echoes, they found {mysterious_item} clutched in a dead hand — and it has refused to leave theirs ever since.",
    "In the final heartbeat before {trigger_event} claimed them, the world inverted — and they returned changed, marked by a power that should have killed them.",
    "They broke the oldest taboo of their people during {tragedy_type} and the punishment never arrived — instead something answered and claimed them as its own.",
    "The blade meant for their heart met {mysterious_item} instead — and when the metal drank the blood, it was the attacker who fell screaming.",
    "They died beneath {tragedy_type} — or so the witnesses swore — yet they rose hours later with eyes that glowed faintly and memories that were not theirs.",
    "A single drop of {mysterious_item}'s liquid touched their tongue during the chaos of {trigger_event} — and the world has tasted different ever since.",
    "The last defender fell in {tragedy_type}, the dying swore an oath on their blood — and the oath found new lungs in the child hiding nearby.",
    "They were the only one who heard the song beneath the screams of {tragedy_type} — and when they tried to sing it back, the melody refused to end.",
    "The moment {trigger_event} tore their world apart, a door no one else could see opened inside their chest — and something patient stepped through.",
    "They reached for {mysterious_item} as {tragedy_type} consumed everything else — and when their fingers closed around it, the destruction paused… and looked at them.",
    "In the silence after {tragedy_type}, they spoke a name aloud for the first time — and the wind answered in a voice older than stone.",
    "The last thing they remembered before {trigger_event} was their mother's lullaby — the first thing they remembered after was the same lullaby… sung by something wearing her face."
]

PERSONAL_COSTS = [
    "their voice",
    "their family estate",
    "their memories of home",
    "the trust of their people",
    "a piece of their humanity",
    "their reflection no longer matches their face",
    "the ability to feel warmth or cold",
    "every happy memory from childhood",
    "the color from their eyes (now solid black / white / glowing)",
    "the capacity to dream — only endless waking nightmares remain",
    "their original name — no one remembers it, not even themselves",
    "the sound of their own heartbeat (they must listen for it to know they're alive)",
    "the trust of every animal they once loved",
    "the taste of food — everything is ash and iron now",
    "their shadow — it detached and wanders freely, sometimes returning with secrets",
    "the sensation of touch on their left side",
    "every promise they ever made before the event",
    "the ability to lie convincingly — truth spills out uncontrollably",
    "their laughter — it now sounds like breaking glass or distant screams",
    "the memory of their mother's voice",
    "the color red — they see only shades of gray where red should be",
    "their sense of balance — the world always tilts slightly when they're alone",
    "the right to be forgotten — anyone who meets them remembers them forever",
    "their reflection in water — it shows someone else staring back",
    "the feeling of belonging anywhere — every place feels like a stranger's house"
]

# ─── New lists for expanding idea hooks ────────────────────────────
FOLLOW_UP_PHRASES = [
    "This event forged in them a {trait} spirit, driving them to {goal}.",
    "Now, {pronoun} carries the weight of that day, seeking {desire}.",
    "The memory of that moment haunts their dreams, pushing them to {action}.",
    "They have never spoken of it, but it shapes every choice they make.",
    "This tragedy left them with a scar—both visible and hidden—that defines who they are.",
    "The experience awakened a {trait} nature within, and they now {behavior}.",
    "Since then, {pronoun} has been driven by a single {emotion}: {emotion_detail}.",
    "Every night, they dream of {dream_content}, a reminder of what was lost."
]

TRAITS = ["vengeful", "protective", "wary", "determined", "melancholic", "fierce", "compassionate", "ruthless"]
GOALS = ["find the truth", "protect the innocent", "seek revenge", "gain power", "restore honor", "discover their destiny"]
DESIRES = ["redemption", "answers", "peace", "belonging", "justice", "forgiveness"]
ACTIONS = ["hone their skills", "seek out allies", "avoid attachments", "search for clues", "confront their past"]
EMOTIONS = ["rage", "grief", "hope", "fear", "determination", "longing"]
EMOTION_DETAILS = ["that burns like fire", "that never fades", "that whispers in the dark", "that drives them forward"]
DREAM_CONTENTS = ["a burning village", "a face they can't recall", "a voice calling their name", "a door that won't open"]
BEHAVIORS = ["trust no one", "help strangers in need", "seek solitude", "look for signs", "practice their craft obsessively"]

import random

def get_pronouns(sex):
    """Return a dict with subject, object, possessive pronouns based on sex string."""
    sex_lower = sex.lower() if sex else ""
    if sex_lower.startswith(("male", "m")) or sex_lower == "he":
        return {"subj": "he", "obj": "him", "poss": "his"}
    elif sex_lower.startswith(("female", "f")) or sex_lower == "she":
        return {"subj": "she", "obj": "her", "poss": "her"}
    else:
        return {"subj": "they", "obj": "them", "poss": "their"}

def generate_ai_concepts(data):
    """
    Use Groq to generate three short, tailored backstory hooks
    based on the character data. Returns a list of three strings.
    Falls back to the old random generator if the API call fails.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        # Fallback hardcoded key (same as in generate_full_backstory)
        api_key = "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"
        if "gsk_" not in api_key:
            raise Exception("No Groq API key found.")

    client = groq.Groq(api_key=api_key)

    prompt = f"""You are a creative assistant for D&D 5e character backstories. Based on the following character details, generate three distinct, compelling backstory hooks (short paragraphs, 2–4 sentences each) that could serve as the core origin/inciting incident for this character. Each hook should be unique, evocative, and tailored to the character's race, class, subclass (if any), alignment, age, gender, and any special details. Avoid generic tropes unless they fit perfectly. Number them "Idea 1:", "Idea 2:", "Idea 3:".

Character:
- Race: {data['race']}
- Class: {data['class_']}
- Subclass: {data['subclass'] or 'None'}
- Alignment: {data['alignment']}
- Age: {data['age'] or 'Young adult'}
- Gender/Pronouns: {data['sex']}
- Additional details/tone: {data['details'] or 'None'}

Output only the three ideas, each labeled.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",   # same model used for full backstory
        messages=[
            {"role": "system", "content": "You are a helpful D&D backstory assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=500,
        top_p=0.9,
    )

    text = response.choices[0].message.content.strip()

    # Parse the three ideas – they should be labeled "Idea 1:", "Idea 2:", etc.
    import re
    parts = re.split(r'Idea\s*\d:', text)
    ideas = [p.strip() for p in parts if p.strip()]
    if len(ideas) >= 3:
        return ideas[:3]
    else:
        # If parsing fails, raise an exception to trigger fallback
        raise Exception(f"Could not parse three ideas from response: {text}")

def generate_concepts(data):
    """
    Advanced version: creates 3 distinct, flavorful backstory hooks
    that strongly reflect race, class, subclass, and any user details.
    Each hook is now expanded with an additional descriptive sentence.
    """
    concepts = []

    race_lower = data.get("race", "").lower()
    class_lower = data.get("class_", "").lower()
    subclass_lower = data.get("subclass", "").lower()
    details = data.get("details", "").strip()
    sex = data.get("sex", "")
    pronouns = get_pronouns(sex)
    subj = pronouns["subj"]
    obj = pronouns["obj"]
    poss = pronouns["poss"]

    # ─── Race-flavored flavor pools ───────────────────────────────────────────────
    race_themes = {
        "dragonborn": {
            "origins": ["a proud clanhold carved into volcanic cliffs", "a nomadic sky-tribe that follows migrating stormfronts",
                        "an exiled lineage hiding among human settlements", "a warband sworn to an ancient wyrm"],
            "tragedies": ["a rival chromatic clan raid", "the awakening of a slumbering volcanic god", "betrayal by a silver-tongued gold dragon emissary"],
            "mystical_items": ["a cracked scale from an ancestor dragon", "a claw-forged amulet pulsing with inner lightning", "a map etched on dragon hide that only glows under moonlight"]
        },
        "elf|wood elf|high elf": {
            "origins": ["an ancient grove untouched by mortal feet", "the spires of a fading elven city", "a hidden fey crossing between worlds"],
            "tragedies": ["the encroachment of human loggers and iron", "a fey curse laid upon the royal line", "the Night of Shattered Stars"],
            "mystical_items": ["a leaf-shaped pendant that still smells of eternal spring", "a star-silver blade that hums when orcs are near", "a vial of captured moonlight"]
        },
        "dwarf": {
            "origins": ["the deep forges of a mountain kingdom", "a declining holdfast overrun by duergar", "a wandering clan of surface smiths"],
            "tragedies": ["a cave-in orchestrated by greediest kin", "the theft of the clan's ancestral anvil", "a mind flayer incursion into the lower halls"],
            "mystical_items": ["a rune-scarred hammer whose head still glows faintly", "a gem that remembers every blow struck upon it"]
        },
        "tiefling": {
            "origins": ["the shadowed alleys of a prejudiced city", "a tiefling enclave clinging to existence", "a traveling circus that hides darker truths"],
            "tragedies": ["a purge by zealous paladins", "the day their infernal parent came to collect", "a blood ritual gone catastrophically wrong"],
            "mystical_items": ["a blackened horn fragment that whispers in Infernal", "a coin that always lands on its edge"]
        },
        # fallback
        "default": {
            "origins": LINEAGE_ORIGINS,
            "tragedies": TRAGEDY_TYPES,
            "mystical_items": ["a blood-stained locket", "a shard of a fallen star", "a map that redraws itself"]
        }
    }

    # Pick race theme (with fallback)
    theme_key = next((k for k in race_themes if any(word in race_lower for word in k.split("|"))), "default")
    race_theme = race_themes.get(theme_key, race_themes["default"])

    # ─── Class & Subclass flavored hook templates ────────────────────────────────
    hook_templates = HOOK_TEMPLATES.copy()  # start with base

    if "sorcerer" in class_lower:
        if "draconic" in subclass_lower:
            hook_templates = [
                "A surge of {color} draconic power erupted uncontrollably when {trigger}, marking them forever as heir to an ancient wyrm.",
                "Ancestral dragon memories flooded their mind the moment they touched {mystical_item}, awakening scales beneath their skin.",
                "In the ashes of {tragedy}, their blood answered with fire and storm—revealing a lineage long thought extinct."
            ]
        elif "wild magic" in subclass_lower:
            hook_templates = [
                "Chaos magic first tore through them during {trigger_event}, twisting reality and leaving permanent scars on the world.",
                "A surge of wild magic saved their life—but at the cost of {personal_cost} and the fear of everyone around them."
            ]
        else:
            hook_templates += ["A latent spark of arcane blood ignited during {trigger_event}, changing their fate forever."]

    elif "warlock" in class_lower:
        patron = subclass_lower.replace("the ", "").lower() if subclass_lower else "mysterious entity"
        hook_templates = [
            f"They spoke the forbidden words / made the desperate bargain with {patron} after {trigger_event}. Power came—along with chains.",
            f"A dying {patron} chose them as the next vessel / pact-bearer during the chaos of {tragedy}.",
            f"The whispers began after touching {mystical_item}—and they have never been alone since."
        ]

    elif "rogue" in class_lower or "ranger" in class_lower:
        hook_templates += [
            "They survived {tragedy} by learning to move unseen, steal to eat, and kill without remorse.",
            "Betrayed by their own crew / tribe, they swore to take back what was stolen—one shadow at a time."
        ]

    elif "paladin" in class_lower or "cleric" in class_lower:
        hook_templates += [
            "A divine vision / celestial call came to them in the aftermath of {tragedy}, demanding they take up the oath.",
            "They swore their oath on the graves of their family after {trigger_event}."
        ]

    # ─── Build 3 distinct hooks ──────────────────────────────────────────────────
    used_hooks = set()  # avoid duplicates

    for i in range(3):
        while True:
            template = random.choice(hook_templates)
            if template not in used_hooks:
                used_hooks.add(template)
                break

        color = random.choice(["crimson", "azure", "emerald", "golden", "shadow-black", "storm-silver"])

        # Fill the main hook
        filled = template.format(
            tragedy_type     = random.choice(race_theme["tragedies"]),
            tragedy          = random.choice(race_theme["tragedies"]),
            trigger          = random.choice(AWAKENING_TRIGGERS + ["a family funeral", "their coming-of-age rite", "the fall of their home"]),
            trigger_event    = random.choice(TRAGEDY_TYPES + ["the death of their mentor", "a betrayal by blood", "a celestial omen"]),
            mysterious_item  = random.choice(race_theme["mystical_items"]),
            mystical_item    = random.choice(race_theme["mystical_items"]),
            color            = color,
            personal_cost    = random.choice(PERSONAL_COSTS + ["their shadow", "their reflection", "their ability to dream"]),

            # Fallbacks for all old placeholders
            power_awakening  = random.choice([
                "a surge of raw magic erupted from within",
                "an otherworldly voice offered power",
                "a bloodline long dormant ignited",
                "a divine spark awakened"
            ]),
            class_tied_power = f"{data['class_'].lower()} gift" if "sorcerer" in class_lower or "warlock" in class_lower else "warrior's spirit",
            betrayer_role    = "someone they trusted",
            motivation       = random.choice(["vengeance", "redemption", "truth", "freedom"]),
            family_secret    = "a hidden truth",
            hidden_truth     = "something dangerous",
            mysterious_mentor= "a shadowy figure",
            saved_who        = "someone important",
            danger           = "great peril",
            curse_trigger    = "a forbidden act",
            curse_effect     = "a lingering affliction",
            exile_reason     = "a grave mistake",
            exile_goal       = "redemption or revenge",
            prophecy_role    = "a figure of destiny",
            entity_type      = "a powerful being",
            guardian_type    = "an unusual guardian",
            residual_power   = "a strange gift"
        )

        # ─── Expand the hook with a follow‑up sentence ────────────────────────────
        follow_up_template = random.choice(FOLLOW_UP_PHRASES)
        follow_up = follow_up_template.format(
            pronoun=subj,
            trait=random.choice(TRAITS),
            goal=random.choice(GOALS),
            desire=random.choice(DESIRES),
            action=random.choice(ACTIONS),
            emotion=random.choice(EMOTIONS),
            emotion_detail=random.choice(EMOTION_DETAILS),
            dream_content=random.choice(DREAM_CONTENTS),
            behavior=random.choice(BEHAVIORS)
        )
        filled += "\n\n" + follow_up

        # Add user details if provided
        if details:
            filled += f"\n\n(This hook incorporates: {details})"

        concepts.append(f"Idea {i+1}:\n{filled}\n")

    return concepts

import groq

def generate_full_backstory(data, chosen_concept):
    # Get API key from environment (preferred) or hard-code it
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        # Fallback – you can remove this block and just use env var
        api_key = "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"  # ← your key
        if "gsk_" not in api_key:
            return "[Error] No Groq API key found.\nSet GROQ_API_KEY environment variable or add it in code."

    try:
        client = groq.Groq(api_key=api_key)

        # The same strong, detailed prompt as before
        prompt = f"""You are an expert fantasy novelist writing for D&D players who want deep, emotional, cinematic backstories.

Write a rich, immersive, third-person backstory in novel-like prose (1300–2200 words) for the following character.
Use vivid sensory details, internal monologue, short bursts of dialogue, meaningful flashbacks, emotional beats, and subtle world-building.
Make the character feel alive — show conflicting feelings, small habits, sensory memories, physical sensations, smells, sounds, textures.

Character:
- Race: {data['race']}
- Class: {data['class_']} ({data['subclass'] or 'none specified'})
- Alignment: {data['alignment']}
- Approximate age: {data['age'] or 'young adult'}
- Pronouns / presentation: {data['sex']}
- Player notes / must-include elements / tone: {data['details'] or 'classic heroic fantasy tone'}

Core concept / inciting hook to center the story around:
{chosen_concept.replace('Idea 1:','').replace('Idea 2:','').replace('Idea 3:','').strip()}

Mandatory story beats (weave them naturally — do NOT use headings or numbers in the output):
1. Birth, family/lineage, early environment and parents/grandparents
2. Childhood → adolescence: key memories, relationships, first hints of personality/class affinity
3. The central tragedy / awakening / betrayal / discovery from the hook — spend significant time here, make it visceral and emotional
4. Years of change: mentors, allies, enemies, how skills/power developed, moral evolution
5. Important side moments or relationships that shaped them (at least 2–3 specific scenes)
6. The final catalyst that pushes them out of their current life into adventuring
7. Present-day mindset: what still haunts them, what they hope for, what they fear, what drives them forward

Style guidelines:
- Write in flowing, literary prose — like a chapter excerpt from a fantasy novel
- Vary sentence length for rhythm
- Include 3–6 named NPCs or locations with personality/flavor
- Subtly incorporate race/class/lore-appropriate elements (draconic pride for Dragonborn, wild magic surges, patron whispers, etc.)
- Avoid generic clichés unless they serve a specific emotional purpose
- End on an open, compelling note that explains why this person is now an adventurer

Do NOT summarize. Do NOT use bullet points or lists. Do NOT say "and so he became an adventurer". Show everything through scenes and feelings.
Aim for 1300–2200 words of actual narrative text.
""".strip()

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a skilled fantasy author specializing in deep, character-driven D&D backstories."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.75,
            max_tokens=2048,
            top_p=0.9,
        )

        backstory = response.choices[0].message.content.strip()

        return (
            "═══ Detailed Backstory ═══\n\n"
            f"{backstory}\n\n"
            "(Generated via Groq • length may vary • regenerate if the tone/quality isn't quite right)"
        )

    except Exception as e:
        # ────────────────────────────────────────
        #  FALLBACK: old templated version
        # ────────────────────────────────────────
        sex_pronoun = "they" if data["sex"].lower() in ["they", "non-binary", ""] else "he" if data["sex"].lower().startswith(("m", "male")) else "she"
        sex_possessive = "their" if sex_pronoun == "they" else "his" if sex_pronoun == "he" else "her"
        
        # Pull key elements from the hook for continuity
        hook_text = chosen_concept.split(":\n")[1].strip() if ":\n" in chosen_concept else chosen_concept
        
        paragraphs = []
        
        # 1. Parentage & Early Life
        origin_place = random.choice([
            "a fog-shrouded coastal village", "the bustling streets of a merchant city",
            "a hidden elven enclave in ancient woods", "the stone halls of a mountain stronghold",
            "a tiefling enclave in the lower wards", "a nomadic caravan crossing endless plains"
        ])
        parents_desc = random.choice([
            "simple farmers who loved deeply but struggled daily",
            "once-respected artisans fallen on hard times",
            "exiles from a noble line",
            "traveling performers with secrets of their own",
            "devout servants of a forgotten deity"
        ])
        
        paragraphs.append(
            f"{data['sex'].capitalize()} was born {data['race']} in {origin_place}, child of {parents_desc}. "
            f"Childhood passed in relative peace—{sex_pronoun} learned the ways of {random.choice(['the land', 'the blade', 'song and story', 'quiet observation'])}, "
            f"dreaming of adventures beyond the horizon. Yet even then, a restlessness stirred within {sex_possessive} heart."
        )
        
        # 2. The Turning Point / Hook Integration
        paragraphs.append(
            f"Then came the moment that shattered everything. {hook_text} "
            f"From that day forward, {sex_pronoun} could no longer remain in the shadows of {sex_possessive} old life."
        )
        
        # 3. Outside Influences & Growth
        influence = random.choice([
            "a grizzled veteran who saw potential", "tomes of forbidden lore discovered in ruins",
            "visions sent by distant powers", "a secret society that recruited them",
            "the harsh lessons of the road itself"
        ])
        training_desc = (
            f"Under {influence}, {sex_pronoun} honed {sex_possessive} {data['class_'].lower()} skills"
            if data.get("subclass") else
            f"sharpened {sex_possessive} abilities as a {data['class_'].lower()}"
        )
        
        paragraphs.append(
            f"{influence.capitalize()}, {training_desc}. "
            f"Along the way {sex_pronoun} learned hard truths about trust, power, and the price of survival. "
            f"Yet the shadow of {sex_possessive} past never fully lifted—{sex_possessive} {data['alignment'].lower()} nature pulled {sex_pronoun} toward {random.choice(['justice', 'freedom', 'knowledge', 'vengeance', 'balance'])}."
        )
        
        # 4. Inciting Incident → Adventurer
        final_push = random.choice([
            f"a bounty hunter / assassin finally tracked {sex_pronoun} down",
            f"word reached {sex_pronoun} of an artifact that could undo {sex_possessive} curse / fulfill the prophecy",
            f"a desperate plea for help arrived from someone {sex_pronoun} could not ignore",
            f"the growing darkness in the world could no longer be ignored",
            f"{sex_pronoun} realized staying hidden would doom more innocents"
        ])
        
        paragraphs.append(
            f"The final spark came when {final_push}. "
            f"With nothing left to lose and everything to prove, {data['sex']} took up {sex_possessive} gear and stepped into the wider world as an adventurer—seeking answers, redemption, power, or simply a place to call home."
        )
        
        # Optional user details weave-in
        if data.get("details"):
            paragraphs.insert(2, f"Throughout these years, {data['details']} remained a constant thread, shaping every choice and scar.")
        
        full_story = "\n\n".join(paragraphs)
        full_story += "\n\n(≈350–500 words fallback version — Groq failed: " + str(e) + ")"
        
        return full_story


# ────────────────────────────────────────
#  GUI
# ────────────────────────────────────────

class BackstoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("D&D 5e Backstory Generator")
        self.root.geometry("780x680")

        self.data = {}
        self.concepts = []
        self.selected_concept = None

        self.create_input_form()
        self.create_output_area()

    def create_input_form(self):
        frame = ttk.LabelFrame(self.root, text="Character Info", padding=10)
        frame.pack(fill="x", padx=10, pady=10)

        row = 0

        # Race dropdown
        ttk.Label(frame, text="Race:").grid(row=row, column=0, sticky="w", pady=4, padx=5)
        race_options = [
            "Dragonborn", "Dwarf", "Elf", "Gnome", "Half-Elf", "Half-Orc",
            "Halfling", "Human", "Tiefling",
            "Aarakocra", "Aasimar", "Bugbear", "Firbolg", "Genasi", "Goblin",
            "Goliath", "Hobgoblin", "Kenku", "Kobold", "Lizardfolk", "Orc",
            "Tabaxi", "Triton", "Yuan-ti Pureblood"
        ]
        self.combo_race = ttk.Combobox(frame, values=race_options, width=47, state="readonly")
        self.combo_race.grid(row=row, column=1, pady=4, sticky="ew")
        row += 1

        # Class dropdown
        ttk.Label(frame, text="Class:").grid(row=row, column=0, sticky="w", pady=4, padx=5)
        class_options = [
            "Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk",
            "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard"
        ]
        self.combo_class = ttk.Combobox(frame, values=class_options, width=47, state="readonly")
        self.combo_class.grid(row=row, column=1, pady=4, sticky="ew")
        row += 1

        # Subclass - dynamic, starts disabled/empty
        ttk.Label(frame, text="Subclass:").grid(row=row, column=0, sticky="w", pady=4, padx=5)
        self.combo_subclass = ttk.Combobox(frame, width=47, state="disabled")
        self.combo_subclass.grid(row=row, column=1, pady=4, sticky="ew")
        row += 1

        # Alignment
        ttk.Label(frame, text="Alignment:").grid(row=row, column=0, sticky="w", pady=4, padx=5)
        alignment_options = [
            "Lawful Good", "Neutral Good", "Chaotic Good",
            "Lawful Neutral", "True Neutral", "Chaotic Neutral",
            "Lawful Evil", "Neutral Evil", "Chaotic Evil"
        ]
        self.combo_alignment = ttk.Combobox(frame, values=alignment_options, width=47, state="readonly")
        self.combo_alignment.grid(row=row, column=1, pady=4, sticky="ew")
        row += 1

        # Age
        ttk.Label(frame, text="Age:").grid(row=row, column=0, sticky="w", pady=4, padx=5)
        self.entry_age = ttk.Entry(frame, width=50)
        self.entry_age.grid(row=row, column=1, pady=4, sticky="ew")
        row += 1

        # Sex
        ttk.Label(frame, text="Sex:").grid(row=row, column=0, sticky="w", pady=4, padx=5)
        self.entry_sex = ttk.Entry(frame, width=50)
        self.entry_sex.grid(row=row, column=1, pady=4, sticky="ew")
        row += 1

        # Details
        ttk.Label(frame, text="Details / tone / must-haves:").grid(row=row, column=0, sticky="nw", pady=4, padx=5)
        self.details_text = scrolledtext.ScrolledText(frame, width=60, height=4, wrap="word")
        self.details_text.grid(row=row, column=1, pady=4, padx=5, sticky="ew")
        self.details_text.insert("1.0", "Optional: e.g. 'dead parents, blue dragonborn, seeks revenge, grimdark tone'")
        # Optional: select the placeholder text so user can overwrite easily
        self.details_text.tag_add("sel", "1.0", "end")

        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Generate / Refresh Ideas", command=self.generate_ideas).pack(side="left", padx=10)
        self.btn_expand = ttk.Button(btn_frame, text="Expand Selected → Full Backstory", command=self.expand, state="disabled")
        self.btn_expand.pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Copy Advanced LLM Prompt", command=self.copy_advanced_prompt).pack(side="left", padx=10)
        # New PDF button
        ttk.Button(btn_frame, text="Save as PDF", command=self.save_pdf).pack(side="left", padx=10)

        # Selection frame
        select_frame = ttk.LabelFrame(self.root, text="Select one idea to expand", padding=10)
        select_frame.pack(fill="x", padx=10, pady=5)

        self.radio_var = tk.IntVar(value=0)
        self.radio_buttons = []
        for i in range(3):
            rb = ttk.Radiobutton(select_frame, text=f"Idea {i+1}", variable=self.radio_var, value=i+1)
            rb.pack(anchor="w", padx=10)
            self.radio_buttons.append(rb)

        # Important: bind the class change event
        self.combo_class.bind("<<ComboboxSelected>>", self.update_subclass_options)

    def add_entry(self, parent, label, row):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=4, padx=5)
        ent = ttk.Entry(parent, width=50)
        ent.grid(row=row, column=1, pady=4, sticky="ew")
        clean_label = label.lower().replace(' ', '_').replace(':', '').replace('/', '_').replace('(', '').replace(')', '')
        setattr(self, f"entry_{clean_label}", ent)

    def add_combo(self, parent, label, values, row):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=4, padx=5)
        combo = ttk.Combobox(parent, values=values, width=47, state="readonly")
        combo.grid(row=row, column=1, pady=4, sticky="ew")
        setattr(self, f"combo_{label.lower().replace(' ','_').replace(':','')}", combo)

    def get_data(self):
        return {
            "race": self.combo_race.get().strip(),
            "class_": self.combo_class.get().strip(),
            "subclass": self.combo_subclass.get().strip(),
            "alignment": self.combo_alignment.get().strip(),
            "age": self.entry_age.get().strip(),
            "sex": self.entry_sex.get().strip(),
            "details": self.details_text.get("1.0", "end-1c").strip()
        }

    def generate_ideas(self):
        self.data = self.get_data()
        required = ["race", "class_", "alignment"]
        missing = [k for k in required if not self.data.get(k)]
        if missing:
            messagebox.showwarning("Missing fields", f"Please fill: {', '.join(missing).title()}")
            return

        # Try AI generation first
        try:
            self.concepts = generate_ai_concepts(self.data)
        except Exception as e:
            # Fallback to old random generation
            messagebox.showwarning("AI generation failed", 
                                   f"Using fallback random generation.\nError: {e}")
            self.concepts = generate_concepts(self.data)

        self.output_text.delete("1.0", "end")
        self.output_text.insert("end", "Three backstory hooks – pick one:\n\n")

        for i, concept in enumerate(self.concepts, 1):
            self.output_text.insert("end", f"──── Idea {i} ────\n")
            self.output_text.insert("end", concept + "\n\n")

        self.btn_expand.config(state="normal")
        self.radio_var.set(1)   # default to first idea


    def expand(self):
        if not self.concepts:
            return
        
        choice = self.radio_var.get()
        if choice < 1 or choice > 3:
            messagebox.showwarning("Selection", "Please select an idea first.")
            return

        selected_concept = self.concepts[choice-1]
        full = generate_full_backstory(self.data, selected_concept)

        self.output_text.delete("1.0", "end")
        self.output_text.insert("end", "══ Full Backstory ══\n\n")
        self.output_text.insert("end", full + "\n\n")
        
        messagebox.showinfo("Done", "Backstory ready! Copy from the text area.\nWant a richer version? We can add Ollama/Claude later.")

    def create_output_area(self):
        ttk.Label(self.root, text="Output / Concepts / Backstory:").pack(anchor="w", padx=10)
        self.output_text = scrolledtext.ScrolledText(self.root, width=90, height=20, wrap="word", font=("Consolas", 10))
        self.output_text.pack(padx=10, pady=5, fill="both", expand=True)

    def update_subclass_options(self, event=None):
        selected_class = self.combo_class.get().strip()
        if selected_class in SUBCLASSES_BY_CLASS:
            subs = SUBCLASSES_BY_CLASS[selected_class]
            self.combo_subclass['values'] = subs
            self.combo_subclass.config(state="readonly")
            if subs:
                self.combo_subclass.current(0)  # optional: select first one
            else:
                self.combo_subclass.set("")
        else:
            self.combo_subclass['values'] = []
            self.combo_subclass.set("")
            self.combo_subclass.config(state="disabled")

    def copy_advanced_prompt(self):
        if not self.concepts or self.radio_var.get() == 0:
            messagebox.showwarning("No selection", "Generate and select an idea first.")
            return

        choice = self.radio_var.get()
        selected = self.concepts[choice-1].strip()

        advanced_prompt = f"""You are a master fantasy author writing deep, emotional D&D 5e backstories in the style of a novel chapter.

    Write a very detailed, immersive third-person backstory (1500–2500 words) for this character.

    Character:
    - Race: {self.data['race']}
    - Class: {self.data['class_']} ({self.data['subclass'] or 'none'})
    - Alignment: {self.data['alignment']}
    - Approximate age: {self.data['age'] or 'young adult'}
    - Gender/pronouns: {self.data['sex']}
    - Player notes / required tone / must-include elements: {self.data['details'] or 'None — use classic fantasy tone'}

    Core hook / origin concept to build the entire story around:
    {selected.replace('Idea 1:','').replace('Idea 2:','').replace('Idea 3:','').strip()}

    Required story elements (blend naturally, do NOT label sections):
    • Birth, family, childhood environment
    • Formative years — key memories, early personality traits
    • The defining tragedy / revelation / betrayal / awakening (spend the most time and emotional weight here)
    • Years of growth, training, mentors, rivals, moral struggles
    • At least 2–4 vivid, specific scenes or flashbacks
    • How their class abilities / subclass features manifested or were learned
    • The final event that forces them to leave their old life
    • Current emotional state: regrets, hopes, fears, driving goal

    Style:
    - Literary prose — vivid descriptions, sensory details, inner thoughts, short dialogue
    - 1500–2500 words of actual narrative (not summary)
    - Include named places, people, small habits, smells/sounds/textures
    - Subtly weave in race/class-appropriate lore
    - End with a compelling, unresolved purpose that explains why they adventure now

    Write only the backstory narrative — no introductions, no explanations, no bullet points.
    """

        self.root.clipboard_clear()
        self.root.clipboard_append(advanced_prompt)
        self.root.update()  # force clipboard update

        messagebox.showinfo("Copied!", "Advanced LLM prompt copied to clipboard.\nPaste it into Claude, ChatGPT, Gemini, etc. for an even longer/more customized version.")

    # ─── New method to save output as PDF ─────────────────────────────────────
    def save_pdf(self):
        """Save the current content of the output text area as a PDF file."""
        if not REPORTLAB_AVAILABLE:
            messagebox.showerror("Missing Library", 
                                 "ReportLab is not installed.\n\n"
                                 "Please install it with: pip install reportlab")
            return

        content = self.output_text.get("1.0", "end-1c").strip()
        if not content:
            messagebox.showwarning("No Content", "There is no text to save.")
            return

        # Ask user for filename
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            title="Save Backstory as PDF"
        )
        if not filename:
            return  # user cancelled

        try:
            # Create a simple PDF with paragraphs
            doc = SimpleDocTemplate(filename, pagesize=letter,
                                    rightMargin=72, leftMargin=72,
                                    topMargin=72, bottomMargin=72)
            styles = getSampleStyleSheet()
            style_normal = styles["Normal"]
            # Allow for a bit more space between paragraphs
            style_normal.spaceAfter = 6

            # Split content into paragraphs (by double newline)
            paragraphs = content.split("\n\n")
            story = []
            for para in paragraphs:
                if para.strip():
                    p = Paragraph(para.replace("\n", " "), style_normal)
                    story.append(p)
                    story.append(Spacer(1, 6))

            doc.build(story)
            messagebox.showinfo("Success", f"PDF saved to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save PDF:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BackstoryApp(root)
    root.mainloop()
