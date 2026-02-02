"""Config flow for setting up."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .api import CompaniesHouseApiClient
from .const import (
    CONF_API_KEY,
    CONF_COMPANY_NUMBER,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)


class CompaniesHouseConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Companies House integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY].strip()
            company_number = user_input[CONF_COMPANY_NUMBER].strip().upper()

            try:
                client = CompaniesHouseApiClient(self.hass, api_key)
                # validate
                info = await client.get_company_profile(company_number)

                await self.async_set_unique_id(company_number)
                self._abort_if_unique_id_configured()

                data = {
                    CONF_API_KEY: api_key,
                    CONF_COMPANY_NUMBER: company_number,
                    CONF_UPDATE_INTERVAL: user_input.get(
                        CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                    ),
                }

                return self.async_create_entry(
                    title=info.get("company_name", company_number), data=data
                )

            except ValueError as err:
                error_type = str(err)
                if error_type in ["invalid_auth", "company_not_found", "bad_request"]:
                    errors["base"] = error_type
                else:
                    errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"

        schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): str,
                vol.Required(CONF_COMPANY_NUMBER): str,
                vol.Optional(
                    CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL
                ): vol.All(vol.Coerce(int), vol.Range(min=1)),
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
