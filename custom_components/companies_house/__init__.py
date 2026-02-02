from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .api import CompaniesHouseApiClient
from .const import CONF_COMPANY_NUMBER, CONF_API_KEY, CONF_UPDATE_INTERVAL
from .coordinator import CompaniesHouseDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    api_client = CompaniesHouseApiClient(hass, entry.data[CONF_API_KEY])

    coordinator = CompaniesHouseDataUpdateCoordinator(
        hass,
        api_client=api_client,
        company_number=entry.data[CONF_COMPANY_NUMBER],
        update_interval_minutes=entry.data[CONF_UPDATE_INTERVAL],
    )

    # initial refresh must succeed for setup to continue
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
