"""Scheduled task for polling API."""

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import CompaniesHouseApiClient
from .const import _LOGGER, DOMAIN


class CompaniesHouseDataUpdateCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator for data updating."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        api_client: CompaniesHouseApiClient,
        company_number: str,
        update_interval_minutes: int,
    ) -> None:
        """Create a update task from company number and intervals."""
        self.api_client = api_client
        self.company_number = company_number

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{company_number}",
            update_interval=timedelta(minutes=update_interval_minutes),
        )

    async def _async_update_data(self) -> dict:
        try:
            return await self.api_client.get_company_profile(self.company_number)
        except ValueError as err:
            error_msg = str(err)
            if error_msg == "invalid_auth":
                raise ConfigEntryAuthFailed("Invalid API Key") from err
            if error_msg == "company_not_found":
                raise UpdateFailed(f"Company {self.company_number} not found") from err
            if error_msg == "bad_request":
                raise UpdateFailed("API returned Bad Request") from err

            raise UpdateFailed(f"Error communicating with API: {err}") from err
