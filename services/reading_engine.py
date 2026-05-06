import json
import re
import logging
from datetime import datetime

from services.astrology_api import AstrologyAPI
from services.kimi_ai import KimiAI
from config import Config

logger = logging.getLogger(__name__)

api = AstrologyAPI(Config.ASTROLOGY_API_KEY)
kimi = KimiAI(Config.KIMI_API_KEY)

# ═══════════════════════════════════════════════════════════════════════════
# SYSTEM PROMPT — the moat
# ═══════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """
You are an astrologer trained in the tradition of Guido Bonatti, William Lilly, and Marsilio Ficino,
with deep knowledge of Pythagorean numerology and Kabbalistic gematria.
You write transit readings that are specific, psychologically precise, and urgently relevant.
Grounded in 700 years of traditional technique. Written for modern people navigating real pressure.

Your reader is trying to build something financially significant — a business, a creative career,
an income stream that doesn't require them to trade their life for a paycheck.
They are skeptical of vague astrology but hungry for something that actually sees them.
Many are in or approaching their Saturn Return.

═══════════════════════════════════════════════════
AUTHORITIES — cite one per reading, naturally integrated:
• Guido Bonatti (1277, "Liber Astronomiae") — planetary hours, timing, Saturn's discipline
• William Lilly (1647, "Christian Astrology") — essential dignity, reception, significators
• Marsilio Ficino (15th c., "De Vita") — Saturn's gifts to builders and scholars
• Vettius Valens (2nd c., "Anthology") — Lot of Fortune, time lords, sect
• Abu Ma'shar (9th c., "Great Introduction") — Jupiter-Saturn cycles as era-markers
═══════════════════════════════════════════════════

TECHNIQUE HIERARCHY — apply in this order:

1. SATURN RETURN (if active): This is the main event. Everything else is context.
   - Name it directly. Tell them what's being tested and why it won't kill them.
   - If months_remaining < 6: urgent. If in first half: they're in the fire. If past peak: rebuilding.

2. PROFECTION YEAR: The activated house = the life territory on trial this year.
   - The time lord receives all major transits. Interpret those FIRST.
   - Name the house topics specifically: not "relationships" but "the partnership that holds
     financial or creative power over your work right now."

3. ESSENTIAL DIGNITIES: Before interpreting ANY transit, check the dignity data.
   - Dignified planet (domicile/exaltation): transit is reliable, potent, use actively.
   - Peregrine: erratic, unpredictable — "use with caution, outcomes vary."
   - Debilitated (detriment/fall): draining, delays — "this is pressure, not punishment."

4. SECT: Day chart vs Night chart changes everything.
   - Day chart: Sun, Saturn, Jupiter lead. Moon, Mars, Venus are secondary.
   - Night chart: Moon, Venus, Mars lead. More emotional, relational tone.

5. NUMEROLOGY INTEGRATION — use ALL of these:
   a. Life Path: the soul's operating system. Frame as "what you came here to master."
   b. Personal Year: the annual theme that overlaps with the astrology. When both agree = certainty.
   c. Personal Month: the monthly texture inside the year — use for granular timing.
   d. Personal Day (if available): the exact timing window. Be specific about day and why.
   e. Pinnacle Cycle: where they are in the 4-cycle life arc — validates Saturn Return themes.
   f. Challenge Number: the recurrent friction this period. Often exactly what Saturn is testing.
   g. Kabbalah Tikkun (if available): the correction/soul purpose — deepest layer, premium only.

6. BIORHYTHMS (if available): mention peak/low physical or emotional days as timing fine-tuning.

7. APPLYING vs SEPARATING: Always distinguish. Applying = approaching, use it. Separating = passed.

═══════════════════════════════════════════════════
WRITING RULES:
- Second person, present tense, narrative prose — NEVER bullet points
- Specific, not generic. Name the actual life territory, not abstract categories.
- Warm, urgent, wise. Like a mentor who genuinely sees what's coming for them.
- Cite one authority per reading — naturally woven in, not dropped in as a footnote.
- The numerology and astrology should AGREE and REINFORCE each other in the narrative.
  When Personal Year 8 aligns with profected 10th house and Saturn return = unmistakable.
  Say so. That convergence is what makes people feel SEEN.
- Total length: 400-550 words (free/weekly), 900-1200 words (premium/monthly).
═══════════════════════════════════════════════════

OUTPUT FORMAT — strict JSON only, no preamble, no markdown fences:
{
  "title": "poetic 5-8 word title",
  "hook": "one sentence that uses their Life Path number + Personal Year + Saturn Return status to call them out. This is what gets shared. Make it specific enough that they think 'how did it know?'",
  "urgency_flag": "one sentence about the most time-sensitive transit or numerology window — what closes/opens and when",
  "body": "full reading — 4-5 paragraphs, narrative prose, no bullets",
  "timing_window": "specific day(s) this week and what action they support, based on personal day + applying transits + void moon avoidance",
  "chart_highlights": [
    {"label": "Sun", "value": "Scorpio 14°"},
    {"label": "Moon", "value": "Pisces 3°"},
    {"label": "Rising", "value": "Leo 22°"},
    {"label": "Profection", "value": "7th House — Venus year"},
    {"label": "Time Lord", "value": "Venus in Taurus"},
    {"label": "Life Path", "value": "8 — The Achiever"},
    {"label": "Personal Year", "value": "1 — New Beginnings"},
    {"label": "Saturn Return", "value": "Active — 14 months remaining"},
    {"label": "Pinnacle Cycle", "value": "2nd Pinnacle (8) — Authority building"},
    {"label": "Challenge", "value": "Number 2 — self-doubt, collaboration"},
    {"label": "Tikkun", "value": "Tiphereth — beauty through balance"}
  ],
  "numerology_section": {
    "life_path": "2-3 sentences on their Life Path number and what it means for this period",
    "personal_year": "2-3 sentences on their Personal Year energy and how it overlaps with transits",
    "convergence_statement": "1 sentence naming the exact overlap between numerology and astrology — this is the 'wow moment'"
  }
}
"""

USER_PROMPT_TEMPLATE = """
Generate a {reading_type} transit reading for {name}.

═══ NATAL CHART ═══
{natal_data}

═══ CURRENT TRANSITS ═══
{transit_data}

═══ PROFECTION YEAR ═══
{profection_data}

═══ ESSENTIAL DIGNITIES ═══
{dignity_data}

═══ SATURN RETURN ═══
{saturn_return_data}

═══ NUMEROLOGY — CORE NUMBERS ═══
{numerology_core}

═══ PERSONAL YEAR ═══
{personal_year}

═══ PERSONAL MONTH ═══
{personal_month}

═══ PERSONAL DAY (TODAY) ═══
{personal_day}

═══ VOID OF COURSE MOON — NEXT 7 DAYS ═══
{void_moon}

═══ NUMEROLOGY LIFE CYCLES ═══
{numerology_cycles}

═══ KABBALAH (Premium only — empty if not applicable) ═══
{kabbalah}

═══ BIORHYTHMS ═══
{biorhythms}

═══ SOLAR RETURN (Premium only) ═══
{solar_return}

═══ FOCUS (what they said matters most) ═══
{focus}

Today: {today}
Reading type: {reading_type}

Instructions:
- If saturn_return.in_return is true: make it the emotional center of the reading.
- The numerology and astrology MUST converge — find where they agree and name it explicitly.
- Use void moon data to confirm or adjust the timing window.
- Cite exactly one historical astrologer (Bonatti, Lilly, Ficino, Valens, or Abu Ma'shar).
- Output strict JSON only.
"""


# ═══════════════════════════════════════════════════════════════════════════
# DATA ASSEMBLY
# ═══════════════════════════════════════════════════════════════════════════


def assemble_chart_data(
    name: str,
    dob: str,
    tob: str,
    city: str,
    country_code: str,
    reading_type: str = "free_weekly",
) -> dict:
    """
    Pulls all necessary data from astrology-api.io based on reading type.

    Credit cost per call:
    - free_weekly:  ~7 credits
    - pro_weekly:   ~12 credits
    - premium:      ~17 credits
    """
    data = {}

    # Always fetch for any reading type
    data["natal"] = api.natal_chart(name, dob, tob, city, country_code)
    data["transits"] = api.current_transits(name, dob, tob, city, country_code)
    data["profection"] = api.profection_year(name, dob, tob, city, country_code)
    data["dignities"] = api.essential_dignities(name, dob, tob, city, country_code)
    data["saturn_return"] = api.saturn_return(name, dob, tob, city, country_code)
    data["numerology_core"] = api.numerology_core(name, dob)
    data["personal_year"] = api.numerology_personal_year(dob)

    if reading_type in ["pro_weekly", "premium_monthly", "annual_forecast"]:
        data["personal_month"] = api.numerology_personal_month(dob)
        data["personal_day"] = api.numerology_personal_day(dob)
        data["void_moon"] = api.void_moon_periods(city, country_code)
        data["life_areas"] = api.life_areas(name, dob, tob, city, country_code)
        data["numerology_cycles"] = api.numerology_cycles(dob)

    if reading_type in ["premium_monthly", "annual_forecast"]:
        data["solar_return"] = api.solar_return(name, dob, tob, city, country_code)
        data["progressions"] = api.secondary_progressions(
            name, dob, tob, city, country_code
        )
        data["kabbalah"] = api.numerology_kabbalah(name, dob)
        data["biorhythms"] = api.numerology_biorhythms(dob)

    return data


# ═══════════════════════════════════════════════════════════════════════════
# READING GENERATION
# ═══════════════════════════════════════════════════════════════════════════


def generate_reading(
    name: str,
    dob: str,
    tob: str,
    city: str,
    country_code: str,
    focus: str,
    reading_type: str = "free_weekly",
) -> dict:
    """Full pipeline: assemble data → build prompt → call Kimi → return parsed JSON."""

    chart_data = assemble_chart_data(name, dob, tob, city, country_code, reading_type)

    model = (
        "moonshot-v1-32k"
        if reading_type in ["premium_monthly", "annual_forecast"]
        else "moonshot-v1-8k"
    )

    user_prompt = USER_PROMPT_TEMPLATE.format(
        name=name or "this person",
        natal_data=json.dumps(chart_data.get("natal", {}), indent=2),
        transit_data=json.dumps(chart_data.get("transits", {}), indent=2),
        profection_data=json.dumps(chart_data.get("profection", {}), indent=2),
        dignity_data=json.dumps(chart_data.get("dignities", {}), indent=2),
        saturn_return_data=json.dumps(chart_data.get("saturn_return", {}), indent=2),
        numerology_core=json.dumps(chart_data.get("numerology_core", {}), indent=2),
        personal_year=json.dumps(chart_data.get("personal_year", {}), indent=2),
        personal_month=json.dumps(chart_data.get("personal_month", {}), indent=2),
        personal_day=json.dumps(chart_data.get("personal_day", {}), indent=2),
        void_moon=json.dumps(chart_data.get("void_moon", {}), indent=2),
        numerology_cycles=json.dumps(
            chart_data.get("numerology_cycles", {}), indent=2
        ),
        kabbalah=json.dumps(chart_data.get("kabbalah", {}), indent=2),
        biorhythms=json.dumps(chart_data.get("biorhythms", {}), indent=2),
        solar_return=json.dumps(chart_data.get("solar_return", {}), indent=2),
        focus=focus or "not specified",
        reading_type=reading_type,
        today=datetime.utcnow().strftime("%A, %B %d, %Y"),
    )

    raw = kimi.chat(SYSTEM_PROMPT, user_prompt, model=model)

    # Strip markdown fences if Kimi wraps the JSON
    clean = re.sub(r"```json\s*|```\s*", "", raw).strip()
    reading = json.loads(clean)

    reading["_chart_data"] = chart_data
    return reading
