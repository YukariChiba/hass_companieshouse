"""Sensor for binary values."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import CompaniesHouseDataUpdateCoordinator
from .entity import CompaniesHouseEntity


def safe_get(data: dict, *keys: str) -> Any | None:
    """Safely get nested dictionary values."""
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


@dataclass(frozen=True, kw_only=True)
class CompaniesHouseBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Sensor entity description class."""

    value_fn: Callable[[dict[str, Any]], bool | None]


BINARY_SENSOR_TYPES: tuple[CompaniesHouseBinarySensorEntityDescription, ...] = (
    CompaniesHouseBinarySensorEntityDescription(
        key="accounts_overdue",
        translation_key="accounts_overdue",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda data: safe_get(data, "accounts", "next_accounts", "overdue"),
    ),
    CompaniesHouseBinarySensorEntityDescription(
        key="confirmation_statement_overdue",
        translation_key="confirmation_statement_overdue",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda data: safe_get(data, "confirmation_statement", "overdue"),
    ),
    CompaniesHouseBinarySensorEntityDescription(
        key="has_insolvency_history",
        translation_key="has_insolvency_history",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda data: data.get("has_insolvency_history"),
    ),
    CompaniesHouseBinarySensorEntityDescription(
        key="can_file",
        translation_key="can_file",
        value_fn=lambda data: data.get("can_file"),
    ),
    CompaniesHouseBinarySensorEntityDescription(
        key="registered_office_is_in_dispute",
        translation_key="registered_office_is_in_dispute",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda data: data.get("registered_office_is_in_dispute"),
    ),
    CompaniesHouseBinarySensorEntityDescription(
        key="undeliverable_registered_office_address",
        translation_key="undeliverable_registered_office_address",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda data: data.get("undeliverable_registered_office_address"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensors from a config entry."""
    coordinator = entry.runtime_data
    async_add_entities(
        CompaniesHouseBinarySensor(coordinator, description)
        for description in BINARY_SENSOR_TYPES
    )


class CompaniesHouseBinarySensor(CompaniesHouseEntity, BinarySensorEntity):
    """Sensor entity class."""

    entity_description: CompaniesHouseBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: CompaniesHouseDataUpdateCoordinator,
        description: CompaniesHouseBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self.entity_description.value_fn(self.coordinator.data)
