"""T1 - Socioemotional category map. Documents, for every category across all six coded taxonomies
plus the two proposed lexical markers, whether it is a genuine affect-display code and, if so, its
valence. Nothing is included in the confirmatory family without a stated justification tied to the
scheme's own published definition."""
import os
import pandas as pd

OUT = os.path.dirname(__file__) + "/../data"
os.makedirs(OUT, exist_ok=True)

rows = []


def add(scheme, code, label, valence, family, justification):
    rows.append(dict(scheme=scheme, category_code=code, label=label, valence=valence,
                      in_confirmatory_family=family, justification=justification))


# ---- CACS (argument structure) - not affect-display codes ----
for c, l in [("arguable", "arguable"), ("converge", "convergent"), ("disagree", "disagreement"),
             ("delim", "delimiting"), ("nonarg", "non-arguable")]:
    add("CACS", c, l, "neutral/excluded", False,
        "argument-structure category (a dialectical move type); 'disagree' here flags a structural "
        "move in an argument, not an emotional-tone display - excluded from the affect family.")

# ---- IAM / Mercer talk-type taxonomies - cognitive/epistemic, not affect display ----
for c, l in [("iam1", "sharing"), ("iam2", "dissonance"), ("iam3", "negotiation"), ("iam4", "testing"),
             ("iam5", "agreement")]:
    add("IAM", c, l, "neutral/excluded", False,
        "cognitive/epistemic stance category (idea-level convergence or conflict), not a moment-level "
        "affect/emotion-display code; 'dissonance'/'agreement' index epistemic state, not tone.")
for c, l in [("disput", "disputational"), ("cumul", "cumulative"), ("explor", "exploratory")]:
    add("Mercer", c, l, "neutral/excluded", False,
        "talk-TYPE classification of a whole episode's reasoning style, not a per-window affect code.")

# ---- Bales IPA task area - excluded (task area, not socioemotional area) ----
for c, l in [("bgiveinfo", "gives information"), ("bgiveopin", "gives opinion"),
             ("bgivesug", "gives suggestion"), ("baskinfo", "asks information"),
             ("baskopin", "asks opinion"), ("basksug", "asks suggestion")]:
    add("Bales IPA", c, l, "neutral/excluded", False,
        "Bales' TASK area (categories 4-9), explicitly distinguished by Bales (1950) from the "
        "SOCIOEMOTIONAL area (1-3, 10-12) used below.")

# ---- Bales IPA socioemotional area - INCLUDED ----
add("Bales IPA", "bsolid", "shows solidarity", "positive", True,
    "Bales (1950) socioemotional-positive category 1: raises other's status, gives help, reward.")
add("Bales IPA", "btension", "shows tension release (jokes, laughs)", "positive", True,
    "Bales (1950) socioemotional-positive category 2: jokes, laughs, shows satisfaction - the "
    "closest direct proxy in this program's coded data to humor/laughter.")
add("Bales IPA", "bagree", "agrees", "positive", True,
    "Bales (1950) socioemotional-positive category 3: shows passive acceptance, understands, "
    "concurs, complies - relational warmth, not mere epistemic convergence (contrast IAM 'iam5').")
add("Bales IPA", "bdisagree", "disagrees", "negative", True,
    "Bales (1950) socioemotional-negative category 10: shows passive rejection, withholds help.")
add("Bales IPA", "btensh", "shows tension", "negative", True,
    "Bales (1950) socioemotional-negative category 11: asks for help, withdraws, shows anxiety.")
add("Bales IPA", "bantag", "shows antagonism", "negative", True,
    "Bales (1950) socioemotional-negative category 12: deflates other's status, defends/asserts "
    "self, shows hostility - the clearest conflict marker in the coded data.")

# ---- act4teams-SHORT (11 functional categories, Klunder et al. 2020) - excluded, one borderline ----
for c, l in [("namep", "names problem"), ("linkp", "links problem"), ("names", "names solution"),
             ("links", "links solution"), ("linkc", "links to consequence"),
             ("proact", "proactivity"), ("struct", "structuring"), ("ginfo", "gives information"),
             ("ktrans", "knowledge transfer")]:
    add("act4teams-SHORT", c, l, "neutral/excluded", False,
        "functional/procedural content category (Klunder et al. 2020, Table 1); not an affect-"
        "display code.")
add("act4teams-SHORT", "cprod", "counterproductivity (backbiting, complaining, blaming)",
    "negative-adjacent (excluded, reported separately)", False,
    "Klunder et al. (2020) define this as behavioral/interpersonal conduct (backbiting, putting "
    "others down, complaining, blaming), not a discrete affect-display act in the Bales/act4teams-"
    "full sense; borderline - reported as an exploratory corroborator, NOT in the confirmatory "
    "family (would double-count with 'neg'/'bantag').")
add("act4teams-SHORT", "coop", "cooperation (praising, thanking, being nice)",
    "positive-adjacent (excluded, reported separately)", False,
    "Klunder et al. (2020) define this as functional politeness/relationship-building conduct, not "
    "a discrete affect-display act; borderline - reported as an exploratory corroborator, NOT in "
    "the confirmatory family (would double-count with 'pos'/'bsolid'/'bagree').")

# ---- ISO 24617-2 dialogue acts - turn-management layer, not affect ----
for c, l in [("qset", "set-question"), ("qprop", "propositional question"), ("directive", "directive"),
             ("commissive", "commissive"), ("feedback", "feedback (grounding/acknowledgment)")]:
    add("ISO 24617-2", c, l, "neutral/excluded", False,
        "dialogue-act / turn-management category (communicative function), not an affect-valence "
        "code; 'feedback' here means grounding/acknowledgment, not emotional tone.")

# ---- act4teams-full facet coding (separate coding pass, data/act4teams/*_passA.json) - INCLUDED ----
add("act4teams (full, 4-facet)", "pos", "positive socio-emotional", "positive", True,
    "Direct facet-level positive-socioemotional code from the full act4teams scheme (Lehmann-"
    "Willenbrock & Kauffeld 2018), coded independently from the Bales pass; corr(A,B)=.65, kappa=.37 "
    "(kappa deflated by near-ubiquity - corr is the better reliability index; ACT4TEAMS_METRIC_MAP.md).")
add("act4teams (full, 4-facet)", "neg", "negative socio-emotional", "negative", True,
    "Direct facet-level negative-socioemotional code from the full act4teams scheme, coded "
    "independently from the Bales pass; corr(A,B)=.45, kappa=.45 (ACT4TEAMS_METRIC_MAP.md).")

# ---- proposed lexical markers (transcript-level, coding-free) ----
add("lexical (transcript, coding-free)", "laughter_tokens",
    "typed laughter conventions (haha/kkk+/rsrs+/huehue+/hehe)", "positive (attempted)", "NULL DATA",
    "Searched all 34 transcripts (17,488 utterances): ZERO matches for any Brazilian-Portuguese "
    "typed-laughter convention. This is an ASR transcript of SPOKEN audio, not a chat/text log - "
    "paralinguistic laughter is not lexicalized by the transcription pipeline. Excluded from the "
    "confirmatory family (no variance to test); reported as a documented negative/boundary finding, "
    "not silently dropped. See lexical_markers.py diagnostic output.")
add("lexical (transcript, coding-free)", "exclaim_density", "exclamation-mark density",
    "positive (attempted)", "NULL DATA",
    "Searched all 34 transcripts: 1 exclamation mark across 17,488 utterances. ASR transcription "
    "does not reliably preserve exclamative punctuation for spoken audio. Excluded from the "
    "confirmatory family (no variance to test); reported as a documented negative/boundary finding.")

df = pd.DataFrame(rows)
df.to_csv(f"{OUT}/socioemotional_map.csv", index=False)
n_fam = (df.in_confirmatory_family == True).sum()
print(f"wrote {OUT}/socioemotional_map.csv  ({len(df)} categories documented across 6 schemes + 2 "
      f"lexical markers; confirmatory family = {n_fam} categories: "
      f"{df[df.in_confirmatory_family==True].category_code.tolist()})")
