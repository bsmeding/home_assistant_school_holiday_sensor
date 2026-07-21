"""School holiday sensor platform."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_COUNTRY, CONF_NAME, CONF_REGION
from .school_holiday_api import SchoolHolidayAPI

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up school holiday sensor from a config entry."""
    country = config_entry.data.get(CONF_COUNTRY)
    region = config_entry.data.get(CONF_REGION)
    name = config_entry.data.get(CONF_NAME) or "School Holiday"
    if not country or not region:
        _LOGGER.error("Missing country or region in config entry")
        return

    api = SchoolHolidayAPI()
    async_add_entities([SchoolHolidaySensor(api, country, region, name)], True)


class SchoolHolidaySensor(SensorEntity):
    """Sensor that reports whether today is a school holiday."""

    _attr_icon = "mdi:beach"

    def __init__(
        self, api: SchoolHolidayAPI, country: str, region: str, name: str
    ) -> None:
        self._api = api
        self._country = country
        self._region = region
        self._attr_name = name
        self._attr_native_value = None
        self._attr_extra_state_attributes = {}
        self._attr_unique_id = (
            f"school_holiday_{country}_{region}".lower().replace(" ", "_")
        )

    async def async_update(self) -> None:
        """Fetch holiday status for today."""
        try:
            data = await self.hass.async_add_executor_job(
                self._api.get_holidays, self._country, self._region
            )
            if data:
                # Keep boolean native value for existing automations/templates.
                self._attr_native_value = bool(
                    data.get("current_holiday_status", False)
                )
                self._attr_extra_state_attributes = data
            else:
                self._attr_native_value = None
                self._attr_extra_state_attributes = {"error": "No holiday data found"}
        except Exception as err:  # noqa: BLE001 - surface failure on entity
            self._attr_native_value = None
            self._attr_extra_state_attributes = {"error": type(err).__name__}
            _LOGGER.exception(
                "Error updating school holidays for %s - %s",
                self._country,
                self._region,
            )
