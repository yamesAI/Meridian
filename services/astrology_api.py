import requests
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AstrologyAPI:
    """
    Full wrapper for astrology-api.io Ultra+ plan.
    Covers: natal charts, transits, profections, traditional techniques,
    numerology (core, personal year, cycles, Kabbalah), Saturn return,
    solar/lunar returns, secondary progressions, biorhythms.
    """

    BASE_URL = "https://api.astrology-api.io/api/v3"

    def __init__(self, api_key: str):
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def _post(self, endpoint: str, body: dict) -> dict:
        url = f"{self.BASE_URL}{endpoint}"
        try:
            r = requests.post(url, headers=self.headers, json=body, timeout=20)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.Timeout:
            raise Exception(f"Astrology API timeout on {endpoint}")
        except requests.exceptions.HTTPError as e:
            raise Exception(
                f"Astrology API error {r.status_code} on {endpoint}: {r.text}"
            )

    def _birth_subject(
        self, name: str, dob: str, tob: str, city: str, country_code: str
    ) -> dict:
        """Build the standard subject object from user inputs."""
        dt = datetime.strptime(dob, "%Y-%m-%d")
        hour, minute = 0, 0
        if tob:
            t = datetime.strptime(tob, "%H:%M")
            hour, minute = t.hour, t.minute
        return {
            "name": name or "User",
            "birth_data": {
                "year": dt.year,
                "month": dt.month,
                "day": dt.day,
                "hour": hour,
                "minute": minute,
                "city": city,
                "country_code": country_code,
            },
        }

    # ─── NATAL CHART ────────────────────────────────────────────────────────

    def natal_chart(
        self,
        name: str,
        dob: str,
        tob: str,
        city: str,
        country_code: str,
        house_system: str = "P",
    ) -> dict:
        return self._post(
            "/charts/natal",
            {
                "subject": self._birth_subject(name, dob, tob, city, country_code),
                "options": {
                    "house_system": house_system,
                    "active_points": [
                        "Sun",
                        "Moon",
                        "Mercury",
                        "Venus",
                        "Mars",
                        "Jupiter",
                        "Saturn",
                        "Uranus",
                        "Neptune",
                        "Pluto",
                        "Ascendant",
                        "Midheaven",
                        "North Node",
                        "South Node",
                        "Chiron",
                        "Part of Fortune",
                    ],
                },
            },
        )

    # ─── CURRENT TRANSITS ────────────────────────────────────────────────────

    def current_transits(
        self,
        name: str,
        dob: str,
        tob: str,
        city: str,
        country_code: str,
        target_date: datetime = None,
    ) -> dict:
        if target_date is None:
            target_date = datetime.utcnow()
        return self._post(
            "/charts/transit",
            {
                "subject": self._birth_subject(name, dob, tob, city, country_code),
                "transit_date": {
                    "year": target_date.year,
                    "month": target_date.month,
                    "day": target_date.day,
                    "hour": target_date.hour,
                    "minute": 0,
                },
                "options": {
                    "active_points": [
                        "Sun",
                        "Moon",
                        "Mercury",
                        "Venus",
                        "Mars",
                        "Jupiter",
                        "Saturn",
                        "Uranus",
                        "Neptune",
                        "Pluto",
                    ],
                    "orb_set": "tight",
                },
            },
        )

    # ─── PROFECTIONS ─────────────────────────────────────────────────────────

    def profection_year(
        self, name: str, dob: str, tob: str, city: str, country_code: str
    ) -> dict:
        return self._post(
            "/traditional/profections",
            {
                "subject": self._birth_subject(name, dob, tob, city, country_code),
                "options": {"include_interpretation": True},
            },
        )

    # ─── ESSENTIAL DIGNITIES ─────────────────────────────────────────────────

    def essential_dignities(
        self, name: str, dob: str, tob: str, city: str, country_code: str
    ) -> dict:
        return self._post(
            "/traditional/essential-dignities",
            {"subject": self._birth_subject(name, dob, tob, city, country_code)},
        )

    # ─── SATURN RETURN ───────────────────────────────────────────────────────

    def saturn_return(
        self, name: str, dob: str, tob: str, city: str, country_code: str
    ) -> dict:
        return self._post(
            "/traditional/saturn-return",
            {"subject": self._birth_subject(name, dob, tob, city, country_code)},
        )

    # ─── SOLAR RETURN ────────────────────────────────────────────────────────

    def solar_return(
        self,
        name: str,
        dob: str,
        tob: str,
        city: str,
        country_code: str,
        year: int = None,
    ) -> dict:
        if year is None:
            year = datetime.utcnow().year
        return self._post(
            "/charts/solar-return",
            {
                "subject": self._birth_subject(name, dob, tob, city, country_code),
                "year": year,
            },
        )

    # ─── LUNAR RETURN ────────────────────────────────────────────────────────

    def lunar_return(
        self, name: str, dob: str, tob: str, city: str, country_code: str
    ) -> dict:
        return self._post(
            "/charts/lunar-return",
            {"subject": self._birth_subject(name, dob, tob, city, country_code)},
        )

    # ─── SECONDARY PROGRESSIONS ──────────────────────────────────────────────

    def secondary_progressions(
        self, name: str, dob: str, tob: str, city: str, country_code: str
    ) -> dict:
        return self._post(
            "/charts/secondary-progressions",
            {"subject": self._birth_subject(name, dob, tob, city, country_code)},
        )

    # ─── ELECTIONAL TIMING ───────────────────────────────────────────────────

    def electional_timing(
        self,
        city: str,
        country_code: str,
        event_type: str = "business_launch",
        days: int = 14,
    ) -> dict:
        today = datetime.utcnow()
        end = today + timedelta(days=days)
        return self._post(
            "/traditional/electional",
            {
                "location": {"city": city, "country_code": country_code},
                "date_range": {
                    "start_date": {
                        "year": today.year,
                        "month": today.month,
                        "day": today.day,
                    },
                    "end_date": {
                        "year": end.year,
                        "month": end.month,
                        "day": end.day,
                    },
                },
                "event_type": event_type,
                "options": {
                    "avoid_void_moon": True,
                    "prefer_waxing_moon": True,
                    "avoid_retrograde_mercury": True,
                },
            },
        )

    # ─── VOID OF COURSE MOON ─────────────────────────────────────────────────

    def void_moon_periods(
        self,
        city: str,
        country_code: str,
        timezone: str = "UTC",
        days: int = 7,
    ) -> dict:
        today = datetime.utcnow()
        end = today + timedelta(days=days)
        return self._post(
            "/traditional/void-moon",
            {
                "location": {"city": city, "country_code": country_code},
                "date_range": {
                    "start_date": {
                        "year": today.year,
                        "month": today.month,
                        "day": today.day,
                    },
                    "end_date": {
                        "year": end.year,
                        "month": end.month,
                        "day": end.day,
                    },
                },
                "options": {"timezone": timezone, "precision": 2},
            },
        )

    # ─── PLANETARY HOURS ─────────────────────────────────────────────────────

    def planetary_hours(self, city: str, country_code: str, date: datetime = None) -> dict:
        if date is None:
            date = datetime.utcnow()
        return self._post(
            "/traditional/planetary-hours",
            {
                "location": {"city": city, "country_code": country_code},
                "date": {"year": date.year, "month": date.month, "day": date.day},
            },
        )

    # ─── LIFE AREAS ──────────────────────────────────────────────────────────

    def life_areas(
        self, name: str, dob: str, tob: str, city: str, country_code: str
    ) -> dict:
        return self._post(
            "/insights/life-areas",
            {"subject": self._birth_subject(name, dob, tob, city, country_code)},
        )

    # ═══════════════════════════════════════════════════════════════════════
    # NUMEROLOGY — all from API
    # ═══════════════════════════════════════════════════════════════════════

    def numerology_core(self, full_name: str, dob: str) -> dict:
        """
        Core numbers: Life Path, Destiny, Soul Urge, Personality, Maturity.
        dob: YYYY-MM-DD  |  full_name: birth name for accurate calculations
        """
        return self._post(
            "/numerology/core-numbers",
            {"name": full_name, "birth_date": dob},
        )

    def numerology_personal_year(self, dob: str, year: int = None) -> dict:
        if year is None:
            year = datetime.utcnow().year
        return self._post(
            "/numerology/personal-year",
            {"birth_date": dob, "year": year},
        )

    def numerology_personal_month(
        self, dob: str, year: int = None, month: int = None
    ) -> dict:
        now = datetime.utcnow()
        return self._post(
            "/numerology/personal-month",
            {
                "birth_date": dob,
                "year": year or now.year,
                "month": month or now.month,
            },
        )

    def numerology_personal_day(self, dob: str, target_date: str = None) -> dict:
        if target_date is None:
            target_date = datetime.utcnow().strftime("%Y-%m-%d")
        return self._post(
            "/numerology/personal-day",
            {"birth_date": dob, "date": target_date},
        )

    def numerology_cycles(self, dob: str) -> dict:
        """Pinnacle Cycles, Challenge Numbers, Life Periods — the full life arc."""
        return self._post("/numerology/cycles", {"birth_date": dob})

    def numerology_kabbalah(self, full_name: str, dob: str) -> dict:
        """Kabbalistic numerology — gematria, Tikkun, Tree of Life. 2 credits."""
        return self._post(
            "/numerology/kabbalah",
            {"name": full_name, "birth_date": dob},
        )

    def numerology_biorhythms(self, dob: str, target_date: str = None) -> dict:
        if target_date is None:
            target_date = datetime.utcnow().strftime("%Y-%m-%d")
        return self._post(
            "/numerology/biorhythms",
            {"birth_date": dob, "target_date": target_date},
        )
