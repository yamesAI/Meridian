import requests
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Pythagorean letter values for local numerology calculations
_LETTER_VALUES = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
    'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8,
}

_SEPHIROT = {
    1: "Keter", 2: "Chokmah", 3: "Binah", 4: "Chesed",
    5: "Geburah", 6: "Tiphereth", 7: "Netzach", 8: "Hod",
    9: "Yesod", 11: "Da'at", 22: "The Fool's Path", 33: "The Master Teacher",
}


def _reduce(n: int, keep_masters: bool = True) -> int:
    """Reduce to single digit, preserving master numbers 11, 22, 33."""
    while n > 9:
        if keep_masters and n in (11, 22, 33):
            break
        n = sum(int(d) for d in str(n))
    return n


class AstrologyAPI:
    """
    Wrapper for astrology-api.io v3.
    API endpoints verified against the official Postman collection.
    Personal Year/Month/Day, Saturn Return, and Kabbalah are computed locally
    — no corresponding API endpoints exist.
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
        except requests.exceptions.HTTPError:
            raise Exception(
                f"Astrology API {r.status_code} on {endpoint}: {r.text}"
            )

    def _birth_subject(
        self, name: str, dob: str, tob: str, city: str, country_code: str
    ) -> dict:
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

    # ─── NATAL CHART ─────────────────────────────────────────────────────────
    # POST /api/v3/charts/natal

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
                    "zodiac_type": "Tropic",
                    "active_points": [
                        "Sun", "Moon", "Mercury", "Venus", "Mars",
                        "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
                        "Ascendant", "Midheaven", "North Node", "South Node",
                        "Chiron", "Part of Fortune",
                    ],
                    "precision": 2,
                },
            },
        )

    # ─── CURRENT TRANSITS ────────────────────────────────────────────────────
    # POST /api/v3/charts/transit

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
                "transit_time": {
                    "datetime": {
                        "year": target_date.year,
                        "month": target_date.month,
                        "day": target_date.day,
                        "hour": target_date.hour,
                        "minute": 0,
                        "second": 0,
                        "city": city,
                        "country_code": country_code,
                    }
                },
                "options": {
                    "house_system": "P",
                    "zodiac_type": "Tropic",
                    "active_points": [
                        "Sun", "Moon", "Mercury", "Venus", "Mars",
                        "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
                    ],
                    "precision": 2,
                },
            },
        )

    # ─── PROFECTIONS ─────────────────────────────────────────────────────────
    # POST /api/v3/traditional/profections

    def profection_year(
        self, name: str, dob: str, tob: str, city: str, country_code: str
    ) -> dict:
        return self._post(
            "/traditional/profections",
            {
                "subject": self._birth_subject(name, dob, tob, city, country_code),
                "options": {
                    "years_ahead": 5,
                    "include_timeline": True,
                    "current_year_focus": True,
                },
            },
        )

    # ─── ESSENTIAL DIGNITIES ─────────────────────────────────────────────────
    # POST /api/v3/traditional/dignities

    def essential_dignities(
        self, name: str, dob: str, tob: str, city: str, country_code: str
    ) -> dict:
        return self._post(
            "/traditional/dignities",
            {
                "subject": self._birth_subject(name, dob, tob, city, country_code),
                "options": {
                    "include_asteroids": False,
                    "include_fixed_stars": True,
                    "dignity_system": "traditional",
                },
            },
        )

    # ─── SOLAR RETURN ────────────────────────────────────────────────────────
    # POST /api/v3/charts/solar-return

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
                "return_year": year,
                "options": {
                    "house_system": "P",
                    "zodiac_type": "Tropic",
                    "active_points": [
                        "Sun", "Moon", "Mercury", "Venus", "Mars",
                        "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
                    ],
                    "precision": 2,
                },
            },
        )

    # ─── LUNAR RETURN ────────────────────────────────────────────────────────
    # POST /api/v3/charts/lunar-return

    def lunar_return(
        self, name: str, dob: str, tob: str, city: str, country_code: str
    ) -> dict:
        return self._post(
            "/charts/lunar-return",
            {
                "subject": self._birth_subject(name, dob, tob, city, country_code),
                "return_date": datetime.utcnow().strftime("%Y-%m-%d"),
                "options": {
                    "house_system": "P",
                    "zodiac_type": "Tropic",
                    "active_points": [
                        "Sun", "Moon", "Mercury", "Venus", "Mars",
                        "Jupiter", "Saturn",
                    ],
                    "precision": 2,
                },
            },
        )

    # ─── SECONDARY PROGRESSIONS ──────────────────────────────────────────────
    # POST /api/v3/charts/progressions

    def secondary_progressions(
        self, name: str, dob: str, tob: str, city: str, country_code: str
    ) -> dict:
        return self._post(
            "/charts/progressions",
            {
                "subject": self._birth_subject(name, dob, tob, city, country_code),
                "target_date": datetime.utcnow().strftime("%Y-%m-%d"),
                "progression_type": "secondary",
                "options": {
                    "house_system": "P",
                    "zodiac_type": "Tropic",
                    "active_points": [
                        "Sun", "Moon", "Mercury", "Venus", "Mars",
                        "Jupiter", "Saturn",
                    ],
                    "precision": 2,
                },
            },
        )

    # ─── VOID OF COURSE MOON ─────────────────────────────────────────────────
    # POST /api/v3/lunar/void-of-course

    def void_moon_periods(
        self, city: str, country_code: str, days: int = 7
    ) -> dict:
        now = datetime.utcnow()
        return self._post(
            "/lunar/void-of-course",
            {
                "datetime_location": {
                    "year": now.year,
                    "month": now.month,
                    "day": now.day,
                    "hour": now.hour,
                    "minute": 0,
                    "second": 0,
                    "city": city,
                    "country_code": country_code,
                },
                "days_ahead": days,
                "use_modern_planets": False,
            },
        )

    # ─── NUMEROLOGY — API-backed ──────────────────────────────────────────────

    def numerology_core(self, full_name: str, dob: str) -> dict:
        """Core numbers: Life Path, Destiny, Soul Urge, Personality, Maturity.
        POST /api/v3/numerology/core-numbers
        """
        dt = datetime.strptime(dob, "%Y-%m-%d")
        return self._post(
            "/numerology/core-numbers",
            {
                "subject": {
                    "name": full_name,
                    "birth_data": {
                        "year": dt.year,
                        "month": dt.month,
                        "day": dt.day,
                        "hour": 0,
                        "minute": 0,
                        "city": "New York",
                        "country_code": "US",
                    },
                },
                "options": {
                    "system": "pythagorean",
                    "target_year": datetime.utcnow().year,
                },
            },
        )

    def numerology_cycles(self, full_name: str, dob: str) -> dict:
        """Pinnacle Cycles, Challenge Numbers, Life Periods.
        POST /api/v3/numerology/comprehensive
        """
        dt = datetime.strptime(dob, "%Y-%m-%d")
        return self._post(
            "/numerology/comprehensive",
            {
                "subject": {
                    "name": full_name,
                    "birth_data": {
                        "year": dt.year,
                        "month": dt.month,
                        "day": dt.day,
                        "hour": 0,
                        "minute": 0,
                        "city": "New York",
                        "country_code": "US",
                    },
                },
                "options": {
                    "include_cycles": True,
                    "include_interpretations": True,
                },
            },
        )

    def numerology_biorhythms(self, dob: str) -> dict:
        """Physical/emotional/intellectual biorhythm cycles.
        POST /api/v3/insights/wellness/biorhythms
        """
        dt = datetime.strptime(dob, "%Y-%m-%d")
        return self._post(
            "/insights/wellness/biorhythms",
            {
                "subject": {
                    "name": "User",
                    "birth_data": {
                        "year": dt.year,
                        "month": dt.month,
                        "day": dt.day,
                        "hour": 0,
                        "minute": 0,
                        "city": "New York",
                        "country_code": "US",
                    },
                },
                "options": {"language": "en"},
            },
        )

    # ─── NUMEROLOGY — LOCAL CALCULATIONS ─────────────────────────────────────
    # No API endpoints exist for Personal Year/Month/Day, Saturn Return,
    # or Kabbalah. Computed locally using standard Pythagorean methodology.

    def numerology_personal_year(self, dob: str, year: int = None) -> dict:
        if year is None:
            year = datetime.utcnow().year
        dt = datetime.strptime(dob, "%Y-%m-%d")
        raw = dt.month + dt.day + sum(int(d) for d in str(year))
        personal_year = _reduce(raw)
        return {"year": year, "personal_year": personal_year}

    def numerology_personal_month(
        self, dob: str, year: int = None, month: int = None
    ) -> dict:
        now = datetime.utcnow()
        year = year or now.year
        month = month or now.month
        py = self.numerology_personal_year(dob, year)["personal_year"]
        return {
            "year": year,
            "month": month,
            "personal_year": py,
            "personal_month": _reduce(py + month),
        }

    def numerology_personal_day(self, dob: str, target_date: str = None) -> dict:
        if target_date is None:
            target_date = datetime.utcnow().strftime("%Y-%m-%d")
        dt = datetime.strptime(target_date, "%Y-%m-%d")
        pm_data = self.numerology_personal_month(dob, dt.year, dt.month)
        return {
            "date": target_date,
            "personal_year": pm_data["personal_year"],
            "personal_month": pm_data["personal_month"],
            "personal_day": _reduce(pm_data["personal_month"] + dt.day),
        }

    def saturn_return(self, dob: str) -> dict:
        """
        Estimates Saturn return window from birth date using the ~29.46-year cycle.
        Saturn return is considered active within 1.5 years of peak on either side.
        No API endpoint exists; derived from orbital mechanics.
        """
        SATURN_CYCLE = 29.46
        WINDOW = 1.5

        birth_dt = datetime.strptime(dob, "%Y-%m-%d")
        now = datetime.utcnow()

        birth_frac = birth_dt.year + birth_dt.timetuple().tm_yday / 365.25
        now_frac = now.year + now.timetuple().tm_yday / 365.25
        age = now_frac - birth_frac

        return_num = max(1, round(age / SATURN_CYCLE))
        peak_frac = birth_frac + return_num * SATURN_CYCLE
        dist = now_frac - peak_frac
        in_return = abs(dist) <= WINDOW

        if dist < 0:
            phase = "approaching" if in_return else "between_returns"
        elif abs(dist) < 0.25:
            phase = "active_peak"
        else:
            phase = "completing" if in_return else "between_returns"

        return {
            "return_number": return_num,
            "in_return": in_return,
            "peak_approximate_year": round(peak_frac, 1),
            "months_remaining": max(0, round(-dist * 12)) if dist < 0 else 0,
            "months_since_peak": round(dist * 12) if dist > 0 else 0,
            "phase": phase,
        }

    def numerology_kabbalah(self, full_name: str, dob: str) -> dict:
        """
        Basic Kabbalistic numerology (Pythagorean gematria → Tikkun/Sephira).
        No API endpoint exists; computed locally.
        """
        letters = ''.join(c for c in full_name.upper() if c.isalpha())
        total = sum(_LETTER_VALUES.get(c, 0) for c in letters)
        tikkun = _reduce(total)
        return {
            "gematria_sum": total,
            "tikkun_number": tikkun,
            "tikkun_sephira": _SEPHIROT.get(tikkun, "Malkuth"),
        }
