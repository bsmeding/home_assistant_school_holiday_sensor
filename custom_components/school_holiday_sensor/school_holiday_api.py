"""School holiday data loader (local YAML files)."""

from __future__ import annotations

import logging
import os
import re
from datetime import date, datetime
from pathlib import Path

import yaml

_LOGGER = logging.getLogger(__name__)

HOLIDAY_DIR = Path(__file__).resolve().parent / "holidays"
_COUNTRY_RE = re.compile(r"^[a-z]{2}$")


class SchoolHolidayAPI:
    """Load and query school holiday YAML files."""

    def get_countries(self) -> dict[str, str]:
        """Return available countries (based on YAML files in the holidays folder)."""
        countries: dict[str, str] = {}
        if not HOLIDAY_DIR.is_dir():
            return countries
        for path in sorted(HOLIDAY_DIR.glob("*.yaml")):
            country_code = path.stem.lower()
            if _COUNTRY_RE.fullmatch(country_code):
                countries[country_code.upper()] = country_code
        return countries

    def get_regions(self, country: str) -> dict[str, str]:
        """Return regions defined in the YAML file for the given country."""
        regions: dict[str, str] = {}
        data = self._load_country(country)
        if not data:
            return regions
        for region in data:
            name = region.get("name")
            if name:
                regions[name] = name
        return regions

    @staticmethod
    def parse_date(value: str) -> date:
        """Parse a holiday date from ISO or DD-MM-YYYY format."""
        for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Invalid date format: {value}")

    def get_holidays(self, country: str, region: str) -> dict:
        """Return holiday info for today and upcoming dates."""
        today = date.today()
        data = self._load_country(country)
        if not data:
            return {}

        for reg in data:
            if reg.get("name") != region:
                continue

            upcoming = []
            current = None

            for holiday in reg.get("holidays", []):
                try:
                    start = self.parse_date(holiday["date_from"])
                    end = self.parse_date(holiday["date_till"])
                except (KeyError, TypeError, ValueError) as err:
                    _LOGGER.warning(
                        "Skipping invalid holiday entry in %s/%s: %s",
                        country,
                        region,
                        err,
                    )
                    continue

                if start <= today <= end:
                    current = holiday.get("name")
                elif start > today:
                    upcoming.append(
                        {
                            "name": holiday.get("name"),
                            "starts_in_days": (start - today).days,
                            "date_from": str(start),
                            "date_till": str(end),
                        }
                    )

            return {
                "current_holiday_status": current is not None,
                "current_holiday": current or "None",
                "upcoming_holidays": sorted(
                    upcoming, key=lambda item: item["starts_in_days"]
                ),
            }

        return {}

    def _country_file(self, country: str) -> Path | None:
        """Resolve a country YAML path, rejecting path traversal."""
        if not isinstance(country, str):
            return None
        code = country.strip().lower()
        if not _COUNTRY_RE.fullmatch(code):
            _LOGGER.warning("Rejected invalid country code: %r", country)
            return None
        path = (HOLIDAY_DIR / f"{code}.yaml").resolve()
        try:
            path.relative_to(HOLIDAY_DIR.resolve())
        except ValueError:
            _LOGGER.warning("Rejected path outside holiday dir: %s", path)
            return None
        return path

    def _load_country(self, country: str) -> list | None:
        """Load and return a country holiday YAML list, or None."""
        path = self._country_file(country)
        if path is None or not path.is_file():
            return None
        with open(path, encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        if not isinstance(data, list):
            _LOGGER.error("Holiday file %s root must be a list", path)
            return None
        return data
