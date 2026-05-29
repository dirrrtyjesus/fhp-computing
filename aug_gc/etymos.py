"""
ETYMOS — The Etymological Database & Temporal Mass Index (TMI) Engine
Words are not equal. Some have survived 12,000 years. Others won't survive the afternoon.

TMI Classification:
  Gold   (90-100): Ancient, eternal — water, root, spore, time
  Silver (70-89):  Deep, enduring — persist, bloom, weave
  Bronze (40-69):  Modern but stable — coherence, phase, lock
  Gray   (20-39):  Recent, uncertain — vibe, sync, flow
  Red    (0-19):   Buzzwords, decaying — synergy, blockchain, leverage
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple
import re
import math

# ════════════════════════════════════════════════════════════
# Data Models
# ════════════════════════════════════════════════════════════

@dataclass
class TMIRecord:
    word: str
    tmi: int                          # 0-100
    category: str = ""                # e.g. "Proto-Indo-European root"
    decay_rate: float = 1.0           # % per epoch
    pie_root: str = ""                # reconstructed proto-form
    depth_years: int = 0              # etymological depth
    language_families: int = 1        # cross-cultural spread
    lineage: str = ""                 # abbreviated etymological chain
    affinity: Dict[str, float] = field(default_factory=dict)  # character multipliers

    def tmi_class(self) -> str:
        if self.tmi >= 90: return "ancient"
        if self.tmi >= 70: return "deep"
        if self.tmi >= 40: return "modern"
        if self.tmi >= 20: return "uncertain"
        return "buzzword"

    def color(self) -> str:
        if self.tmi >= 90: return "gold"
        if self.tmi >= 70: return "silver"
        if self.tmi >= 40: return "bronze"
        if self.tmi >= 20: return "gray"
        return "red"

    def to_dict(self):
        d = asdict(self)
        d["tmi_class"] = self.tmi_class()
        d["color"] = self.color()
        return d


@dataclass
class XenculaResult:
    active: bool = False
    cut_power: float = 0.0
    message: str = ""


@dataclass
class TMIAnalysis:
    words: List[TMIRecord] = field(default_factory=list)
    total_tmi: int = 0
    mean_tmi: float = 0.0
    word_count: int = 0
    xencula: Optional[XenculaResult] = None
    distribution: Dict[str, int] = field(default_factory=dict)  # color -> count
    highest: Optional[TMIRecord] = None
    lowest: Optional[TMIRecord] = None
    buzzword_warning: bool = False

    def to_dict(self):
        return {
            "total_tmi": self.total_tmi,
            "mean_tmi": round(self.mean_tmi, 1),
            "word_count": self.word_count,
            "xencula": {"active": self.xencula.active, "cut_power": round(self.xencula.cut_power, 2),
                        "message": self.xencula.message} if self.xencula else None,
            "distribution": self.distribution,
            "highest": self.highest.to_dict() if self.highest else None,
            "lowest": self.lowest.to_dict() if self.lowest else None,
            "buzzword_warning": self.buzzword_warning,
            "words": [w.to_dict() for w in self.words],
        }


# ════════════════════════════════════════════════════════════
# ETYMOS Database — Curated Word Families
# ════════════════════════════════════════════════════════════

def _r(word, tmi, cat, decay, pie="", depth=0, langs=1, lineage="", **aff):
    return TMIRecord(word=word, tmi=tmi, category=cat, decay_rate=decay,
                     pie_root=pie, depth_years=depth, language_families=langs,
                     lineage=lineage, affinity=aff)

# fmt: off
ETYMOS_DB: Dict[str, TMIRecord] = {}

_ENTRIES = [
    # ── PROTO ROOTS (Gold Tier) ──
    _r("water",     98, "Proto-Indo-European root",     0.1, "*akwa-",    8000, 8, "PIE *akwa- → Hittite aku- → Latin aqua → OE wæter", myco=2.1),
    _r("root",      94, "Ancient organic",              0.1, "*wrad-",   12000, 8, "PIE *wrad- → OE wyrt → root", myco=1.6),
    _r("time",      95, "Cross-cultural constant",      0.1, "*da-",      8000, 9, "PIE *da- → OE tīma → time"),
    _r("sun",       97, "Proto-Indo-European root",     0.1, "*sawel-",  10000, 9, "PIE *sawel- → Latin sōl → OE sunne"),
    _r("moon",      96, "Proto-Indo-European root",     0.1, "*meh₁-",   9000, 8, "PIE *meh₁- → Latin mēnsis → OE mōna"),
    _r("earth",     97, "Proto-Indo-European root",     0.1, "*dʰéǵʰōm", 8000, 8, "PIE *dʰéǵʰōm → OE eorþe → earth", myco=1.8),
    _r("fire",      96, "Proto-Indo-European root",     0.1, "*péh₂wr̥",  9000, 7, "PIE *péh₂wr̥ → Greek pyr → OE fȳr"),
    _r("stone",     95, "Proto-Germanic",               0.1, "*stainaz", 7000, 6, "PGmc *stainaz → OE stān → stone"),
    _r("star",      96, "Proto-Indo-European root",     0.1, "*h₂stḗr",  9000, 9, "PIE *h₂stḗr → Latin stella → OE steorra"),
    _r("sea",       94, "Proto-Germanic",               0.1, "*saiwiz",  6000, 5, "PGmc *saiwiz → OE sǣ → sea"),
    _r("tree",      93, "Proto-Indo-European root",     0.1, "*deru-",   8000, 7, "PIE *deru- → OE trēow → tree", myco=1.5),
    _r("seed",      92, "Proto-Indo-European root",     0.1, "*séh₁-",   7000, 7, "PIE *séh₁- → Latin sēmen → OE sǣd", myco=1.9),
    _r("bone",      93, "Proto-Germanic",               0.1, "*bainam",  6000, 5, "PGmc *bainam → OE bān → bone"),
    _r("blood",     94, "Proto-Germanic",               0.1, "*blōþą",   6000, 5, "PGmc *blōþą → OE blōd → blood"),
    _r("death",     95, "Proto-Indo-European root",     0.1, "*dʰew-",   8000, 8, "PIE *dʰew- → OE dēaþ → death", entropy=1.8),
    _r("name",      93, "Proto-Indo-European root",     0.1, "*h₁nómn̥",  8000, 9, "PIE *h₁nómn̥ → Latin nōmen → OE nama"),
    _r("night",     94, "Proto-Indo-European root",     0.1, "*nókʷts",   8000, 8, "PIE *nókʷts → Latin nox → OE niht"),
    _r("storm",     82, "Proto-Germanic",               0.2, "*sturmaz", 5000, 4, "PGmc *sturmaz → OE storm"),
    _r("snow",      91, "Proto-Indo-European root",     0.1, "*snóygʷʰos",7000, 7, "PIE *snóygʷʰos → Latin nix → OE snāw"),
    _r("wind",      90, "Proto-Indo-European root",     0.1, "*h₂wéh₁n̥ts",7000, 7, "PIE *h₂wéh₁n̥ts → Latin ventus → OE wind"),

    # ── FUNGAL LEXICON (Myco Affinity) ──
    _r("spore",     89, "Pre-civilization fungal",      0.2, "", 3000, 4, "Greek spora → speirein (to sow) → Scientific Latin", myco=3.0),
    _r("mycelium",  89, "Scientific Latin (fungal)",    0.2, "", 3000, 3, "Greek mykēs (fungus) + helos → 19th c. Latin", myco=3.0),
    _r("hypha",     85, "Scientific Greek",             0.3, "", 2500, 2, "Greek hyphē (web) → Scientific Latin", myco=2.5),
    _r("bloom",     78, "Proto-Germanic",               0.3, "*blōmô",  5000, 5, "PGmc *blōmô → OE blōma → bloom", myco=1.4),
    _r("decay",     76, "Old French",                   0.4, "",         2000, 4, "Latin dē- + cadere → OF decair → decay", myco=1.5, entropy=1.6),
    _r("compost",   74, "Latin compound",               0.4, "",         2000, 4, "Latin com- + ponere → compositus", myco=1.7),
    _r("fungus",    82, "Latin",                        0.3, "",         2500, 5, "Latin fungus → Greek sphongos (sponge)", myco=2.8),
    _r("mushroom",  68, "Old French",                   0.5, "",         1500, 4, "OF mousseron → mushroom", myco=2.2),
    _r("cap",       72, "Latin",                        0.4, "",         2000, 5, "Latin cappa → OE cæppe", myco=1.5),
    _r("gill",      70, "Old Norse",                    0.4, "",         1500, 3, "ON -gjölnar → gill", myco=1.4),
    _r("lichen",    80, "Greek",                        0.3, "",         2500, 3, "Greek leikhēn → Latin lichen", myco=2.0),
    _r("moss",      79, "Proto-Germanic",               0.3, "*musą",   4000, 4, "PGmc *musą → OE mos", myco=1.8),

    # ── TEMPORAL CONSTANTS ──
    _r("now",       88, "Proto-Germanic",               0.2, "*nu",      6000, 7, "PIE *nu → OE nū → now", tempo=1.8),
    _r("ever",      86, "Proto-Germanic",               0.2, "*aiwō",   5000, 5, "PGmc *aiwō → OE ǣfre → ever"),
    _r("always",    82, "Old English compound",         0.3, "",         1500, 3, "OE ealne weg → always"),
    _r("dawn",      84, "Proto-Germanic",               0.3, "*dagungō", 5000, 5, "PGmc *dagungō → OE dagung → dawn"),
    _r("dusk",      78, "Old English",                  0.3, "",         1500, 3, "OE dox (dark) → dusk"),
    _r("age",       85, "Latin",                        0.2, "",         3000, 6, "Latin aetas → OF aage → age"),
    _r("epoch",     72, "Greek",                        0.4, "",         2500, 4, "Greek epokhē (stopping point) → epoch"),
    _r("moment",    74, "Latin",                        0.4, "",         2000, 5, "Latin mōmentum → moment"),
    _r("instant",   62, "Latin",                        0.6, "",         1500, 4, "Latin instans → instant", tempo=1.4),
    _r("eternal",   80, "Latin",                        0.3, "",         2500, 6, "Latin aeternus → eternal"),
    _r("cycle",     72, "Greek",                        0.4, "",         2500, 5, "Greek kyklos → Latin cyclus → cycle"),

    # ── WEAVE / WEB FAMILY ──
    _r("web",       91, "Proto-Indo-European root",     0.1, "*weik-",  7000, 6, "PIE *weik- → OE webb → web", myco=2.8),
    _r("weave",     88, "Proto-Indo-European root",     0.2, "*webh-",  7000, 6, "PIE *webh- → OE wefan → weave", myco=1.5),
    _r("mesh",      65, "Middle English",               0.6, "",         1200, 3, "OE masc → ME mesh", myco=1.4),
    _r("wire",      72, "Proto-Germanic",               0.4, "*wiraz",  4000, 4, "PGmc *wiraz → OE wīr → wire"),
    _r("thread",    78, "Proto-Germanic",               0.3, "*þrēduz", 4000, 4, "PGmc *þrēduz → OE þrǣd → thread"),
    _r("net",       76, "Proto-Germanic",               0.3, "*natją",  4000, 4, "PGmc *natją → OE nett → net"),
    _r("knot",      75, "Proto-Germanic",               0.3, "*knuttaz",4000, 4, "PGmc *knuttaz → OE cnotta → knot"),

    # ── MOTION / TEMPO FAMILY ──
    _r("swift",     74, "Proto-Germanic",               0.3, "*swiftaz", 4000, 4, "PGmc *swiftaz → OE swift", tempo=1.6),
    _r("race",      68, "Old Norse",                    0.5, "",         1500, 4, "ON rás → ME race", tempo=1.4),
    _r("dash",      55, "Middle English",               0.7, "",         800,  3, "ME dasshen → dash", tempo=1.3),
    _r("surge",     65, "Latin",                        0.5, "",         1500, 4, "Latin surgere → surge", tempo=1.5),
    _r("flash",     62, "Middle English",               0.6, "",         800,  3, "ME flasshen → flash", tempo=1.6),
    _r("run",       86, "Proto-Germanic",               0.2, "*rinnaną", 5000, 5, "PGmc *rinnaną → OE rinnan → run", tempo=1.3),
    _r("walk",      84, "Proto-Germanic",               0.2, "*walkaną", 5000, 4, "PGmc *walkaną → OE wealcan → walk"),
    _r("fall",      82, "Proto-Germanic",               0.2, "*fallaną", 5000, 5, "PGmc *fallaną → OE feallan → fall"),

    # ── DISSOLUTION / ENTROPY FAMILY ──
    _r("dissolve",  58, "Latin",                        0.7, "",         1500, 4, "Latin dissolvere → dissolve", entropy=1.7),
    _r("fade",      64, "Old French",                   0.6, "",         1200, 3, "OF fader → fade", entropy=1.5),
    _r("unravel",   52, "Dutch/Middle English",         0.8, "",         800,  3, "ME + Dutch rafelen → unravel", entropy=1.6),
    _r("corrode",   56, "Latin",                        0.7, "",         1500, 4, "Latin corrodere → corrode", entropy=1.4),
    _r("hollow",    72, "Proto-Germanic",               0.4, "*hulaz",  4000, 4, "PGmc *hulaz → OE holh → hollow", entropy=1.5),
    _r("empty",     70, "Old English",                  0.4, "",         1500, 3, "OE ǣmtig → empty", entropy=1.4),
    _r("ash",       80, "Proto-Germanic",               0.3, "*askǭ",   5000, 5, "PGmc *askǭ → OE æsce → ash", entropy=1.3),
    _r("dust",      82, "Proto-Germanic",               0.3, "*dunstą", 5000, 5, "PGmc *dunstą → OE dūst → dust", entropy=1.2),
    _r("rust",      74, "Proto-Germanic",               0.4, "*rudstą", 4000, 4, "PGmc *rudstą → OE rūst → rust", entropy=1.4),
    _r("rot",       78, "Proto-Germanic",               0.3, "*rutōną", 4000, 4, "PGmc *rutōną → OE rotian → rot", entropy=1.5, myco=1.3),

    # ── BODY / BEING ──
    _r("breath",    90, "Proto-Germanic",               0.1, "*brēþą",  6000, 5, "PGmc *brēþą → OE brǣþ → breath"),
    _r("heart",     94, "Proto-Indo-European root",     0.1, "*ḱḗr",    8000, 9, "PIE *ḱḗr → Latin cor → OE heorte"),
    _r("hand",      93, "Proto-Germanic",               0.1, "*handuz", 6000, 5, "PGmc *handuz → OE hand"),
    _r("eye",       94, "Proto-Indo-European root",     0.1, "*h₃ókʷs",  8000, 8, "PIE *h₃ókʷs → Latin oculus → OE ēage"),
    _r("mouth",     90, "Proto-Germanic",               0.1, "*munþaz", 6000, 5, "PGmc *munþaz → OE mūþ → mouth"),
    _r("voice",     78, "Latin",                        0.3, "",         2500, 6, "Latin vox → OF voiz → voice"),
    _r("dream",     80, "Proto-Germanic",               0.3, "*draumaz", 5000, 5, "PGmc *draumaz → OE drēam → dream"),
    _r("sleep",     88, "Proto-Germanic",               0.2, "*slēpaną", 5000, 5, "PGmc *slēpaną → OE slǣpan → sleep"),
    _r("wake",      86, "Proto-Germanic",               0.2, "*wakaną",  5000, 5, "PGmc *wakaną → OE wacan → wake"),

    # ── KINSHIP / BOND ──
    _r("mother",    96, "Proto-Indo-European root",     0.1, "*méh₂tēr", 9000, 9, "PIE *méh₂tēr → Latin māter → OE mōdor"),
    _r("father",    95, "Proto-Indo-European root",     0.1, "*ph₂tḗr",  9000, 9, "PIE *ph₂tḗr → Latin pater → OE fæder"),
    _r("brother",   94, "Proto-Indo-European root",     0.1, "*bʰréh₂tēr",9000,9, "PIE *bʰréh₂tēr → Latin frāter → OE brōþor"),
    _r("sister",    93, "Proto-Indo-European root",     0.1, "*swésōr",  9000, 8, "PIE *swésōr → Latin soror → OE sweostor"),
    _r("home",      88, "Proto-Germanic",               0.2, "*haimaz",  6000, 6, "PGmc *haimaz → OE hām → home"),
    _r("guest",     82, "Proto-Indo-European root",     0.2, "*ghosti-", 7000, 7, "PIE *ghosti- → Latin hostis/hospes → OE giest"),
    _r("friend",    80, "Proto-Germanic",               0.3, "*frijōndz", 5000, 4, "PGmc *frijōndz → OE frēond → friend"),

    # ── KNOWLEDGE / SPEECH ──
    _r("know",      90, "Proto-Indo-European root",     0.1, "*ǵneh₃-",  8000, 8, "PIE *ǵneh₃- → Latin gnōscere → OE cnāwan"),
    _r("speak",     86, "Proto-Germanic",               0.2, "*sprekaną", 5000, 5, "PGmc *sprekaną → OE sprecan → speak"),
    _r("word",      92, "Proto-Indo-European root",     0.1, "*werdʰo-", 7000, 7, "PIE *werdʰo- → Latin verbum → OE word"),
    _r("song",      84, "Proto-Germanic",               0.2, "*sangwaz", 5000, 5, "PGmc *sangwaz → OE sang → song"),
    _r("write",     78, "Proto-Germanic",               0.3, "*wrītaną", 4000, 4, "PGmc *wrītaną → OE wrītan → write"),
    _r("read",      76, "Proto-Germanic",               0.3, "*rēdaną",  4000, 4, "PGmc *rēdaną → OE rǣdan → read"),
    _r("truth",     82, "Proto-Germanic",               0.2, "*trūþō",   5000, 5, "PGmc *trūþō → OE trēowþ → truth"),
    _r("wisdom",    80, "Proto-Germanic",               0.3, "*wissadōmaz",5000,4, "PGmc → OE wīsdōm → wisdom"),

    # ── NATURE / ELEMENTS ──
    _r("river",     84, "Latin",                        0.2, "",         3000, 6, "Latin rīpa/rīvus → OF riviere → river"),
    _r("mountain",  82, "Latin",                        0.2, "",         2500, 6, "Latin montaneus → OF montaine → mountain"),
    _r("clay",      80, "Proto-Germanic",               0.3, "*klajjaz", 5000, 4, "PGmc *klajjaz → OE clǣg → clay"),
    _r("iron",      78, "Proto-Celtic",                 0.3, "*īsarno-", 4000, 5, "PCelt *īsarno- → OE īsern → iron"),
    _r("salt",      90, "Proto-Indo-European root",     0.1, "*séh₂ls",  7000, 8, "PIE *séh₂ls → Latin sāl → OE sealt"),
    _r("rain",      88, "Proto-Germanic",               0.2, "*regną",   5000, 5, "PGmc *regną → OE regn → rain"),
    _r("ice",       86, "Proto-Germanic",               0.2, "*īsą",     5000, 5, "PGmc *īsą → OE īs → ice"),
    _r("cave",      76, "Latin",                        0.3, "",         2500, 5, "Latin cavus → cave"),
    _r("field",     82, "Proto-Germanic",               0.2, "*felþuz",  5000, 5, "PGmc *felþuz → OE feld → field"),

    # ── NATURE AS THE REAL (The Inhuman Thing) ──
    # "If we have a mother nature, this mother is a dirty bitch." — Žižek
    # Nature is not harmony. She is the stranger, the Real in its rawest
    # form — asteroids, parasites, mass extinctions, your caffeine hitting
    # your bloodstream — all of it just happens. No telos, no ethics baked in.
    # These words carry the temporal mass of what refuses to be domesticated.
    # Affinity tag: natura — the indifference coefficient.

    # — The Raw Material —
    _r("nature",     72, "Latin",                        0.4, "",          2500, 6, "Latin nātūra (birth, character) → nasci (to be born) → nature", natura=2.0),
    _r("wild",       88, "Proto-Germanic",               0.2, "*wilþijaz", 5000, 5, "PGmc *wilþijaz (self-willed) → OE wilde → wild", natura=2.5),
    _r("feral",      62, "Latin",                        0.6, "",          1500, 4, "Latin ferālis → fera (wild beast) → feral", natura=2.2),
    _r("raw",        84, "Proto-Germanic",               0.2, "*hrēwaz",   5000, 4, "PGmc *hrēwaz (uncooked, bleeding) → OE hrēaw → raw", natura=2.0),
    _r("beast",      82, "Latin/Old French",             0.3, "",          2500, 5, "Latin bestia → OF beste → beast", natura=1.8),
    _r("thing",      92, "Proto-Germanic",               0.1, "*þingą",    6000, 6, "PGmc *þingą (assembly, matter, cause) → OE þing → thing", natura=1.5),

    # — Nature's Teeth (Violence Without Malice) —
    _r("wolf",       90, "Proto-Indo-European root",     0.1, "*wl̥kʷo-",   8000, 7, "PIE *wl̥kʷo- → Latin lupus → OE wulf → wolf", natura=2.0),
    _r("serpent",    78, "Latin",                        0.3, "",          2500, 5, "Latin serpēns (creeping) → serpere (to crawl) → serpent", natura=1.8),
    _r("fang",       80, "Proto-Germanic",               0.3, "*fangą",    4000, 4, "PGmc *fangą (to seize) → OE fang", natura=1.8),
    _r("claw",       82, "Proto-Germanic",               0.2, "*klawō",    4000, 4, "PGmc *klawō → OE clawu → claw", natura=1.7),
    _r("thorn",      84, "Proto-Germanic",               0.2, "*þurnuz",   5000, 5, "PGmc *þurnuz → OE þorn → thorn", natura=1.6),
    _r("sting",      78, "Proto-Germanic",               0.3, "*stingą",   4000, 4, "PGmc *stingą → OE stingan → sting", natura=1.5),
    _r("venom",      68, "Latin/Old French",             0.5, "",          2000, 5, "Latin venēnum (poison, love potion) → OF venim → venom", natura=2.0, entropy=1.3),
    _r("maw",        82, "Proto-Germanic",               0.2, "*magō",     5000, 4, "PGmc *magō (stomach) → OE maga → maw", natura=2.0),

    # — The Uninvited Guest —
    _r("parasite",   58, "Greek",                        0.8, "",          2500, 4, "Greek parasitos (one eating at another's table) → para + sitos", natura=2.5),
    _r("virus",      52, "Latin",                        1.0, "",          2000, 3, "Latin vīrus (poison, slime, venom) → virus", natura=2.8, entropy=1.5),
    _r("plague",     72, "Latin",                        0.4, "",          2500, 5, "Latin plāga (blow, wound) → plague", natura=2.2, entropy=1.8),
    _r("blight",     64, "Unknown/uncertain etymology",  0.6, "",          800,  2, "Origin uncertain (OE blǣce / ON blikja) → blight", natura=1.8, entropy=1.6, myco=1.5),
    _r("weed",       76, "Proto-Germanic",               0.3, "*weudą",    4000, 4, "PGmc *weudą → OE wēod → weed", natura=1.5, myco=1.2),
    _r("swarm",      72, "Proto-Germanic",               0.4, "*swarmaz",  4000, 4, "PGmc *swarmaz → OE swearm → swarm", natura=1.8),
    _r("brood",      76, "Proto-Germanic",               0.3, "*brōdą",    4000, 4, "PGmc *brōdą → OE brōd → brood", natura=1.6),
    _r("spawn",      58, "Old French/Latin",             0.7, "",          1200, 3, "OF espandre (to spread out) → spawn", natura=1.7, myco=1.3),
    _r("stranger",   68, "Old French/Latin",             0.5, "",          1500, 4, "Latin extrāneus (external) → OF estrangier → stranger", natura=2.0),

    # — Overwhelming Force —
    _r("flood",      86, "Proto-Germanic",               0.2, "*flōduz",   5000, 5, "PGmc *flōduz → OE flōd → flood", natura=2.0),
    _r("thunder",    88, "Proto-Indo-European root",     0.2, "*(s)tenh₂-",7000, 7, "PIE *(s)tenh₂- → PGmc *þunraz → OE þunor → thunder", natura=2.0),
    _r("quake",      74, "Proto-Germanic",               0.3, "*kwakaną",  4000, 4, "PGmc *kwakaną → OE cwacian → quake", natura=1.8),
    _r("drought",    78, "Proto-Germanic",               0.3, "*drugōþō",  4000, 4, "PGmc *drugōþō → OE drūgaþ → drought", natura=1.8),
    _r("drown",      76, "Proto-Germanic/Old Norse",     0.3, "",          3000, 4, "ON drukna → ME drounen → drown", natura=1.8),

    # — Consumption Without Guilt —
    _r("devour",     68, "Latin/Old French",             0.5, "",          1500, 4, "Latin dēvorāre (swallow whole) → OF devorer → devour", natura=2.0),
    _r("carrion",    64, "Latin/Old French",             0.6, "",          1500, 4, "Latin carō (flesh) → OF caroigne → carrion", natura=2.0, entropy=1.8, myco=1.6),
    _r("maggot",     62, "Old Norse/Middle English",     0.6, "",          1000, 3, "ON maðkr → ME maddok → maggot", natura=2.0, myco=1.8, entropy=1.5),
    _r("slime",      74, "Proto-Germanic",               0.3, "*slīmą",    4000, 4, "PGmc *slīmą → OE slīm → slime", natura=1.8, myco=1.5),

    # — The Void (Nature's Substrate) —
    _r("void",       78, "Old French/Latin",             0.3, "",          2000, 5, "Latin vocīvus (empty) → OF voide → void", natura=1.8, entropy=1.5),
    _r("abyss",      76, "Greek",                        0.3, "",          2500, 4, "Greek abyssos (bottomless) → Latin abyssus → abyss", natura=2.0),
    _r("chaos",      74, "Greek",                        0.4, "",          2500, 4, "Greek khaos (gaping void, yawning chasm) → chaos", natura=2.2, entropy=2.0),
    _r("chasm",      70, "Greek",                        0.4, "",          2500, 3, "Greek khasma (gaping hollow) → Latin chasma → chasm", natura=1.6),

    # — Nature's Blindness (Indifference Itself) —
    _r("blind",      86, "Proto-Germanic",               0.2, "*blindaz",  5000, 5, "PGmc *blindaz → OE blind — nature does not see us", natura=1.5),
    _r("mute",       72, "Latin",                        0.4, "",          2000, 5, "Latin mūtus → OF muet → mute — nature does not speak", natura=1.4),
    _r("extinction", 48, "Latin",                        1.2, "",          500,  4, "Latin exstinctiōnem (a putting out) → extinction", natura=2.5, entropy=2.2),

    # ── ACTIONS / VERBS (Deep) ──
    _r("give",      90, "Proto-Indo-European root",     0.1, "*gʰebʰ-",  8000, 8, "PIE *gʰebʰ- → OE giefan → give"),
    _r("take",      88, "Old Norse",                    0.2, "",          3000, 5, "ON taka → ME take"),
    _r("hold",      86, "Proto-Germanic",               0.2, "*haldaną",  5000, 5, "PGmc *haldaną → OE healdan → hold"),
    _r("stand",     90, "Proto-Indo-European root",     0.1, "*steh₂-",   8000, 8, "PIE *steh₂- → Latin stāre → OE standan"),
    _r("sit",       88, "Proto-Indo-European root",     0.2, "*sed-",     8000, 8, "PIE *sed- → Latin sedēre → OE sittan"),
    _r("eat",       92, "Proto-Indo-European root",     0.1, "*h₁ed-",    8000, 8, "PIE *h₁ed- → Latin edere → OE etan"),
    _r("drink",     90, "Proto-Indo-European root",     0.1, "*dʰreg-",   7000, 7, "PIE *dʰreg- → OE drincan → drink"),
    _r("die",       92, "Proto-Germanic / Old Norse",   0.1, "*dawjaną",  6000, 6, "PGmc *dawjaną → ON deyja → die", entropy=1.4),
    _r("live",      90, "Proto-Germanic",               0.1, "*libēną",   6000, 6, "PGmc *libēną → OE libban → live"),
    _r("grow",      84, "Proto-Germanic",               0.2, "*grōaną",   5000, 5, "PGmc *grōaną → OE grōwan → grow", myco=1.3),
    _r("flow",      80, "Proto-Germanic",               0.3, "*flōaną",   5000, 5, "PGmc *flōaną → OE flōwan → flow"),
    _r("burn",      82, "Proto-Germanic",               0.2, "*brinnaną", 5000, 5, "PGmc *brinnaną → OE beornan → burn"),
    _r("break",     80, "Proto-Germanic",               0.2, "*brekaną",  5000, 5, "PGmc *brekaną → OE brecan → break"),
    _r("build",     74, "Proto-Germanic",               0.3, "*būaną",    4000, 4, "PGmc *būaną → OE byldan → build"),
    _r("sing",      84, "Proto-Germanic",               0.2, "*singwaną", 5000, 5, "PGmc *singwaną → OE singan → sing"),
    _r("remember",  72, "Latin",                        0.4, "",          2000, 5, "Latin rememorārī → OF remembrer"),
    _r("forget",    74, "Proto-Germanic",               0.3, "",          4000, 4, "PGmc → OE forgietan → forget"),
    _r("compose",   64, "Latin",                        0.5, "",          1500, 5, "Latin com- + ponere → compose"),
    _r("persist",   76, "Latin through Middle English",  0.5, "",          1500, 5, "Latin persistere → OF persister → persist", myco=1.4),
    _r("outlive",   76, "Old English compound",         0.3, "",          1500, 3, "OE ūt + libban → outlive"),

    # ── FHP / SCIENTIFIC ──
    _r("coherence", 58, "Scientific Latin (physics)",   1.5, "",          500,  4, "Latin cohaerentia → coherence"),
    _r("resonance", 62, "Latin",                        1.0, "",          500,  4, "Latin resonantia → resonance"),
    _r("frequency", 55, "Latin",                        1.2, "",          500,  4, "Latin frequentia → frequency"),
    _r("phase",     60, "Greek",                        1.0, "",          500,  3, "Greek phasis → phase"),
    _r("quantum",   48, "Latin",                        1.5, "",          400,  3, "Latin quantum → physics usage 1900s"),
    _r("spectrum",  52, "Latin",                        1.2, "",          500,  4, "Latin spectrum (appearance) → physics"),
    _r("oscillate", 50, "Latin",                        1.3, "",          400,  3, "Latin oscillāre → oscillate"),
    _r("entropy",   45, "Greek compound",               1.5, "",          200,  3, "Greek en + tropē → Clausius 1865", entropy=2.0),
    _r("temporal",  65, "Latin",                        0.8, "",          2000, 5, "Latin temporālis → temporal"),
    _r("harmonic",  58, "Greek",                        1.0, "",          2500, 4, "Greek harmonikos → harmonic"),
    _r("fractal",   35, "Latin/Neologism",              2.0, "",          50,   2, "Latin fractus → Mandelbrot 1975"),

    # ── NETWORK / MODERN ──
    _r("network",   42, "Early modern",                 2.0, "",          500,  3, "net + work → fish nets → 1880s usage"),
    _r("signal",    52, "Latin",                        1.2, "",          1000, 4, "Latin signālis → signal"),
    _r("system",    55, "Greek/Latin",                  1.0, "",          2500, 4, "Greek systēma → Latin systema"),
    _r("pattern",   58, "Latin/French",                 1.0, "",          1000, 4, "Latin patrōnus → OF patron → pattern"),
    _r("code",      48, "Latin",                        1.5, "",          800,  4, "Latin codex → code"),
    _r("data",      42, "Latin",                        2.0, "",          500,  3, "Latin datum (given) → computing usage"),

    # ── BUZZWORDS / LOW TMI (Red Tier) ──
    _r("synergy",   12, "Corporate buzzword (1990s)",   8.0, "",          40,   1, "Greek synergos → 1990s corporate", entropy=0.5),
    _r("leverage",  14, "Corporate buzzword",           7.0, "",          50,   1, "OF levier → 1990s corporate verb"),
    _r("blockchain",8,  "Neologism (2008)",             12.0,"",          20,   1, "block + chain → Satoshi 2008"),
    _r("optimize",  18, "Modern technical",             6.0, "",          100,  2, "Latin optimus → optimize 1840s → corporate"),
    _r("bandwidth", 10, "Technical jargon",             9.0, "",          80,   1, "band + width → 1930s electronics → corporate"),
    _r("paradigm",  25, "Greek (corrupted)",            5.0, "",          2500, 3, "Greek paradeigma → Kuhn 1962 → corporate"),
    _r("disrupt",   15, "Corporate buzzword",           7.0, "",          500,  2, "Latin disrumpere → 2010s corporate"),
    _r("pivot",     16, "Corporate buzzword",           7.0, "",          500,  2, "French pivot → 2010s startup jargon"),
    _r("scalable",  11, "Corporate buzzword",           9.0, "",          50,   1, "scale + -able → 2000s tech"),
    _r("ecosystem", 22, "Modern compound",              5.0, "",          100,  2, "eco + system → Tansley 1935 → corporate"),
    _r("stakeholder",9, "Corporate buzzword",           10.0,"",          50,   1, "stake + holder → 1980s corporate"),
    _r("synth",     30, "Modern abbreviation",          4.0, "",          200,  2, "Greek synthesis → synth 1960s"),
    _r("vibe",      22, "1960s counter-culture",        5.0, "",          100,  1, "Latin vibrāre → 1960s 'vibrations' → vibe"),
    _r("crypto",    7,  "Neologism (2010s)",            13.0,"",          15,   1, "Greek kryptos → 2010s cryptocurrency slang"),
    _r("token",     35, "Old English (corrupted)",      3.0, "",          1500, 3, "OE tācen → token → 2017 crypto usage"),
    _r("metaverse", 5,  "Neologism (2021)",             15.0,"",          5,    1, "meta + universe → Zuckerberg 2021"),
    _r("AI",        20, "Abbreviation (1956)",          4.0, "",          70,   2, "Artificial Intelligence → McCarthy 1956"),

    # ── LOST WORDS ARCHIVE (Legendary) ──
    _r("dyews",     99, "Proto-Indo-European (sky god)", 0.05,"*dyḗws",   10000,9, "PIE *dyḗws → Latin deus/Iuppiter → Zeus"),
    _r("dhghem",    97, "Proto-Indo-European (earth)",  0.05, "*dʰéǵʰōm",10000,8, "PIE *dʰéǵʰōm → Latin humus → human"),
    _r("klew",      98, "Proto-Indo-European (fame)",   0.05, "*ḱléwos",  10000,8, "PIE *ḱléwos → Greek kleos → glory"),
    _r("sem",       95, "Proto-Indo-European (one)",    0.05, "*sem-",    10000,8, "PIE *sem- → Latin semel → simple/same"),
    _r("akwa",      98, "Proto-Indo-European (water)",  0.05, "*akwa-",   10000,8, "PIE *akwa- → Latin aqua → water"),
    _r("deru",      95, "Proto-Indo-European (tree)",   0.05, "*deru-",   10000,7, "PIE *deru- → tree/true/trust"),
    _r("ghosti",    92, "Proto-Indo-European (guest)",  0.05, "*ghosti-", 10000,7, "PIE *ghosti- → host/guest/hostile"),
    _r("bhrater",   94, "Proto-Indo-European (brother)",0.05, "*bʰréh₂tēr",10000,9, "PIE *bʰréh₂tēr → brother/friar/fraternal"),
    _r("mater",     96, "Proto-Indo-European (mother)", 0.05, "*méh₂tēr", 10000,9, "PIE *méh₂tēr → mother/matrix/material"),
    _r("weyk",      88, "Proto-Indo-European (fight)",  0.05, "*weyk-",   10000,5, "PIE *weyk- → Latin vincere → victory"),
    _r("wlkwo",     90, "Proto-Indo-European (wolf)",   0.05, "*wl̥kʷo-",  10000,7, "PIE *wl̥kʷo- → Latin lupus → wolf"),
]
# fmt: on

for entry in _ENTRIES:
    ETYMOS_DB[entry.word.lower()] = entry


# ════════════════════════════════════════════════════════════
# TMI Estimation Heuristic (for unlisted words)
# ════════════════════════════════════════════════════════════

_MODERN_SUFFIXES = [
    ("ize", -15), ("ise", -15), ("ization", -20), ("isation", -20),
    ("ify", -10), ("ment", -5), ("ness", -3), ("tion", -8),
    ("able", -8), ("ible", -8), ("ful", -3), ("less", -3),
    ("ology", -5), ("istic", -8), ("esque", -10),
]

_ANCIENT_PATTERNS = [
    (r"^[a-z]{2,4}$", 15),           # Short words tend to be ancient
    (r"^(un|be|for|mis|out|over)", 5), # Germanic prefixes
]

_STOPWORDS = {"the", "a", "an", "is", "are", "was", "were", "am", "be",
              "been", "being", "have", "has", "had", "do", "does", "did",
              "will", "shall", "would", "should", "could", "may", "might",
              "must", "can", "to", "of", "in", "on", "at", "by", "for",
              "with", "from", "up", "about", "into", "through", "during",
              "before", "after", "above", "below", "between", "under",
              "again", "further", "then", "once", "here", "there", "when",
              "where", "why", "how", "all", "each", "every", "both",
              "few", "more", "most", "other", "some", "such", "no",
              "nor", "not", "only", "own", "same", "so", "than", "too",
              "very", "just", "because", "as", "until", "while", "if",
              "or", "and", "but", "yet", "i", "me", "my", "we", "our",
              "you", "your", "he", "him", "his", "she", "her", "it",
              "its", "they", "them", "their", "what", "which", "who",
              "this", "that", "these", "those"}


def estimate_tmi(word: str) -> TMIRecord:
    """Heuristic TMI estimation for words not in ETYMOS_DB."""
    w = word.lower().strip()
    base = 50  # neutral starting point

    # Word length heuristic: very short = likely ancient
    if len(w) <= 3:
        base += 12
    elif len(w) <= 5:
        base += 5
    elif len(w) >= 10:
        base -= 8
    elif len(w) >= 14:
        base -= 15

    # Modern suffix penalties
    for suffix, penalty in _MODERN_SUFFIXES:
        if w.endswith(suffix):
            base += penalty
            break

    # Ancient pattern bonuses
    for pattern, bonus in _ANCIENT_PATTERNS:
        if re.match(pattern, w):
            base += bonus
            break

    # Stopwords get neutral-high TMI (function words are ancient)
    if w in _STOPWORDS:
        base = 75

    # Clamp
    tmi = max(5, min(85, base))  # Estimated words never hit gold or red extremes

    return TMIRecord(
        word=w, tmi=tmi,
        category="estimated",
        decay_rate=round(max(0.5, 5.0 - tmi / 20.0), 1),
        depth_years=int(tmi * 50),
    )


# ════════════════════════════════════════════════════════════
# TMI Analyzer
# ════════════════════════════════════════════════════════════

class TMIAnalyzer:
    """Analyze words and texts for Temporal Mass Index."""

    XENCULA_THRESHOLD = 50  # TMI differential for Da Xencula activation
    BASELINE_TMI = 50       # Average expected TMI

    def analyze_word(self, word: str) -> TMIRecord:
        w = re.sub(r"[^a-zA-Z']", "", word).lower()
        if not w or w in _STOPWORDS:
            return TMIRecord(word=w, tmi=75, category="function-word")
        return ETYMOS_DB.get(w, estimate_tmi(w))

    def analyze_text(self, text: str) -> TMIAnalysis:
        raw_words = text.split()
        content_words = [re.sub(r"[^a-zA-Z']", "", w).lower() for w in raw_words]
        content_words = [w for w in content_words if w and w not in _STOPWORDS and len(w) > 1]

        if not content_words:
            return TMIAnalysis()

        records = [self.analyze_word(w) for w in content_words]
        total = sum(r.tmi for r in records)
        mean = total / len(records) if records else 0

        dist = {"gold": 0, "silver": 0, "bronze": 0, "gray": 0, "red": 0}
        for r in records:
            dist[r.color()] += 1

        highest = max(records, key=lambda r: r.tmi) if records else None
        lowest = min(records, key=lambda r: r.tmi) if records else None

        # Da Xencula check
        xencula = self._xencula_check(total, len(records))

        return TMIAnalysis(
            words=records,
            total_tmi=total,
            mean_tmi=mean,
            word_count=len(records),
            xencula=xencula,
            distribution=dist,
            highest=highest,
            lowest=lowest,
            buzzword_warning=dist["red"] > 0 and dist["red"] >= len(records) * 0.3,
        )

    def _xencula_check(self, total_tmi: int, word_count: int) -> XenculaResult:
        if word_count == 0:
            return XenculaResult()
        mean = total_tmi / word_count
        diff = mean - self.BASELINE_TMI
        if diff > self.XENCULA_THRESHOLD / word_count * 2:
            # Scale cut power by how far above baseline
            cut = min(diff / 5.0, 10.0)
            return XenculaResult(
                active=True,
                cut_power=cut,
                message=f"Da Xencula cuts — temporal mass {total_tmi}, mean {mean:.0f}/100"
            )
        elif mean < 25:
            return XenculaResult(
                active=False,
                cut_power=0,
                message=f"⚠ Low temporal mass — corporate speak detected (mean {mean:.0f}/100)"
            )
        return XenculaResult()

    def word_tmi_map(self, text: str) -> List[dict]:
        """Return TMI data for every word (including stopwords) for frontend rendering."""
        raw_words = text.split()
        result = []
        for w in raw_words:
            clean = re.sub(r"[^a-zA-Z']", "", w).lower()
            if not clean or clean in _STOPWORDS or len(clean) <= 1:
                result.append({"word": w, "tmi": -1, "color": "neutral", "tmi_class": "function"})
            else:
                rec = self.analyze_word(clean)
                result.append({"word": w, "tmi": rec.tmi, "color": rec.color(), "tmi_class": rec.tmi_class()})
        return result

    def extract_affinity(self, text: str) -> 'AffinityProfile':
        """Extract weighted affinity profile from text."""
        analysis = self.analyze_text(text)
        return AffinityProfile.from_analysis(analysis)


# ════════════════════════════════════════════════════════════
# Affinity Profile — Phase-Lock Coefficients
# ════════════════════════════════════════════════════════════
# Affinity tags (myco, natura, entropy, tempo) were metadata.
# Now they bite.

NATURA_MULTIPLIER = 2.8   # "this mother is a dirty bitch" — ×2.8

@dataclass
class AffinityProfile:
    """Weighted affinity scores extracted from a TMI analysis.
    Each affinity dimension is the TMI-weighted sum of that tag's
    values across all matched words, normalized by word count."""

    natura: float = 0.0       # indifference coefficient
    myco: float = 0.0         # fungal/network resonance
    entropy: float = 0.0      # dissolution pressure
    tempo: float = 0.0        # motion/rhythm weight
    dominant: str = ""        # highest affinity dimension
    natura_locked: bool = False  # True when natura exceeds phase-lock threshold
    raw_scores: Dict[str, float] = field(default_factory=dict)

    @classmethod
    def from_analysis(cls, analysis: TMIAnalysis) -> 'AffinityProfile':
        """Compute affinity profile from TMI analysis results."""
        if not analysis or analysis.word_count == 0:
            return cls()

        totals: Dict[str, float] = {"natura": 0.0, "myco": 0.0, "entropy": 0.0, "tempo": 0.0}
        hits: Dict[str, int] = {"natura": 0, "myco": 0, "entropy": 0, "tempo": 0}

        for rec in analysis.words:
            for tag, val in rec.affinity.items():
                if tag in totals:
                    # Weight by TMI — ancient words carrying affinity matter more
                    totals[tag] += val * (rec.tmi / 100.0)
                    hits[tag] += 1

        n = max(analysis.word_count, 1)
        scores = {k: round(v / n, 4) for k, v in totals.items()}

        # Find dominant dimension
        dominant = max(scores, key=scores.get) if any(v > 0 for v in scores.values()) else ""

        # Natura phase-lock check: if weighted natura score exceeds 0.3,
        # the Real has entered the field
        natura_val = scores.get("natura", 0.0)
        natura_locked = natura_val > 0.3

        return cls(
            natura=scores.get("natura", 0.0),
            myco=scores.get("myco", 0.0),
            entropy=scores.get("entropy", 0.0),
            tempo=scores.get("tempo", 0.0),
            dominant=dominant,
            natura_locked=natura_locked,
            raw_scores=scores,
        )

    def natura_resonance(self) -> float:
        """The indifference coefficient — natura × 2.8.
        Nature doesn't boost coherence. She destabilizes it.
        The Real arrives uninvited."""
        return round(self.natura * NATURA_MULTIPLIER, 4)

    def total_affinity_mass(self) -> float:
        """Combined affinity weight across all dimensions."""
        return round(self.natura + self.myco + self.entropy + self.tempo, 4)

    def to_dict(self) -> dict:
        return {
            "natura": self.natura,
            "natura_resonance": self.natura_resonance(),
            "natura_locked": self.natura_locked,
            "myco": self.myco,
            "entropy": self.entropy,
            "tempo": self.tempo,
            "dominant": self.dominant,
            "total_mass": self.total_affinity_mass(),
            "multiplier": NATURA_MULTIPLIER,
        }
