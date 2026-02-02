"""Define entity for companies."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import CompaniesHouseDataUpdateCoordinator


class CompaniesHouseEntity(CoordinatorEntity[CompaniesHouseDataUpdateCoordinator]):
    """Company entity."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(
        self, coordinator: CompaniesHouseDataUpdateCoordinator, key: str
    ) -> None:
        """Create a company entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.company_number}_{key}"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.company_number)},
            name=coordinator.data.get(
                "company_name", f"Company {coordinator.company_number}"
            ),
            manufacturer="Companies House UK",
            model="Company Register",
            entry_type="service",
            configuration_url=f"https://find-and-update.company-information.service.gov.uk/company/{coordinator.company_number}",
        )
