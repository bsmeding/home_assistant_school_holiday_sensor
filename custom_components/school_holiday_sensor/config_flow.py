"""Config flow for the Home Assistant School Holiday Sensor."""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant import config_entries

from .const import CONF_COUNTRY, CONF_REGION, DOMAIN
from .school_holiday_api import SchoolHolidayAPI

_LOGGER = logging.getLogger(__name__)


class SchoolHolidayConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for School Holiday Sensor."""

    VERSION = 1

    def __init__(self) -> None:
        self.data: dict = {}
        self.api = SchoolHolidayAPI()
        self._countries: dict[str, str] = {}

    async def async_step_user(self, user_input=None):
        """Handle the initial country selection step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            display_name = user_input[CONF_COUNTRY]
            country_code = self._countries.get(display_name, display_name)
            self.data[CONF_COUNTRY] = country_code
            return await self.async_step_region()

        self._countries = await self.hass.async_add_executor_job(
            self.api.get_countries
        )
        if not self._countries:
            return self.async_abort(reason="no_countries_found")

        schema = vol.Schema(
            {
                vol.Required(CONF_COUNTRY): vol.In(
                    sorted(self._countries.keys())
                )
            }
        )
        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )

    async def async_step_region(self, user_input=None):
        """Handle the region selection step."""
        errors: dict[str, str] = {}
        country = self.data.get(CONF_COUNTRY)
        if user_input is not None:
            region = user_input[CONF_REGION]
            await self.async_set_unique_id(
                f"{DOMAIN}_{country}_{region}".lower().replace(" ", "_")
            )
            self._abort_if_unique_id_configured()
            self.data[CONF_REGION] = region
            return self.async_create_entry(
                title=f"{str(country).upper()} - {region}",
                data=self.data,
            )

        regions = await self.hass.async_add_executor_job(
            self.api.get_regions, country
        )
        if not regions:
            return self.async_abort(reason="no_regions_found")

        schema = vol.Schema(
            {vol.Required(CONF_REGION): vol.In(sorted(regions.keys()))}
        )
        return self.async_show_form(
            step_id="region", data_schema=schema, errors=errors
        )
