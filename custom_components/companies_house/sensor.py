from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .coordinator import CompaniesHouseDataUpdateCoordinator
from .entity import CompaniesHouseEntity


def _parse_ch_date(date_str: str | None) -> date | None:
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def safe_get(data: dict, *keys: str) -> Any | None:
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def format_address(address_data: dict | None) -> str | None:
    if not address_data:
        return None
    
    parts = [
        address_data.get("premises"),
        address_data.get("address_line_1"),
        address_data.get("address_line_2"),
        address_data.get("locality"),
        address_data.get("region"),
        address_data.get("postal_code"),
        address_data.get("country"),
    ]
    return ", ".join(part for part in parts if part)


@dataclass(frozen=True, kw_only=True)
class CompaniesHouseSensorEntityDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], StateType | date]


STATUS_OPTIONS = [
    "active",
    "dissolved",
    "liquidation",
    "receivership",
    "administration",
    "voluntary-arrangement",
    "converted-closed",
    "insolvency-proceedings",
    "registered",
    "removed",
    "closed",
    "open",
]

SENSOR_TYPES: tuple[CompaniesHouseSensorEntityDescription, ...] = (
    CompaniesHouseSensorEntityDescription(
        key="company_status",
        translation_key="company_status",
        icon="mdi:domain",
        device_class=SensorDeviceClass.ENUM,
        options=STATUS_OPTIONS,
        value_fn=lambda data: data.get("company_status"),
    ),
    CompaniesHouseSensorEntityDescription(
        key="date_of_creation",
        translation_key="date_of_creation",
        icon="mdi:calendar-star",
        device_class=SensorDeviceClass.DATE,
        value_fn=lambda data: _parse_ch_date(data.get("date_of_creation")),
    ),
    CompaniesHouseSensorEntityDescription(
        key="accounts_next_due",
        translation_key="accounts_next_due",
        icon="mdi:calendar-clock",
        device_class=SensorDeviceClass.DATE,
        value_fn=lambda data: _parse_ch_date(
            safe_get(data, "accounts", "next_accounts", "due_on")
        ),
    ),
    CompaniesHouseSensorEntityDescription(
        key="last_accounts_type",
        translation_key="last_accounts_type",
        icon="mdi:file-percent",
        value_fn=lambda data: safe_get(data, "accounts", "last_accounts", "type"),
    ),
    CompaniesHouseSensorEntityDescription(
        key="confirmation_statement_next_due",
        translation_key="confirmation_statement_next_due",
        icon="mdi:calendar-clock",
        device_class=SensorDeviceClass.DATE,
        value_fn=lambda data: _parse_ch_date(
            safe_get(data, "confirmation_statement", "next_due")
        ),
    ),
    CompaniesHouseSensorEntityDescription(
        key="company_type",
        translation_key="company_type",
        icon="mdi:briefcase-variant",
        value_fn=lambda data: data.get("type"),
    ),
    CompaniesHouseSensorEntityDescription(
        key="jurisdiction",
        translation_key="jurisdiction",
        icon="mdi:map-marker-radius",
        value_fn=lambda data: data.get("jurisdiction"),
    ),
    CompaniesHouseSensorEntityDescription(
        key="registered_office_address",
        translation_key="registered_office_address",
        icon="mdi:map-marker",
        value_fn=lambda data: format_address(data.get("registered_office_address")),
    ),
    CompaniesHouseSensorEntityDescription(
        key="sic_codes",
        translation_key="sic_codes",
        icon="mdi:tag-multiple",
        value_fn=lambda data: ", ".join(data.get("sic_codes", [])) if data.get("sic_codes") else None,
    ),
    CompaniesHouseSensorEntityDescription(
        key="last_accounts_period_end",
        translation_key="last_accounts_period_end",
        icon="mdi:calendar-arrow-left",
        device_class=SensorDeviceClass.DATE,
        value_fn=lambda data: _parse_ch_date(
            safe_get(data, "accounts", "last_accounts", "period_end_on")
        ),
    ),
    CompaniesHouseSensorEntityDescription(
        key="next_accounts_period_start",
        translation_key="next_accounts_period_start",
        icon="mdi:calendar-start",
        device_class=SensorDeviceClass.DATE,
        value_fn=lambda data: _parse_ch_date(
            safe_get(data, "accounts", "next_accounts", "period_start_on")
        ),
    ),
    CompaniesHouseSensorEntityDescription(
        key="next_accounts_period_end",
        translation_key="next_accounts_period_end",
        icon="mdi:calendar-end",
        device_class=SensorDeviceClass.DATE,
        value_fn=lambda data: _parse_ch_date(
            safe_get(data, "accounts", "next_accounts", "period_end_on")
        ),
    ),
    CompaniesHouseSensorEntityDescription(
        key="confirmation_statement_last_made",
        translation_key="confirmation_statement_last_made",
        icon="mdi:file-document-check",
        device_class=SensorDeviceClass.DATE,
        value_fn=lambda data: _parse_ch_date(
            safe_get(data, "confirmation_statement", "last_made_up_to")
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        CompaniesHouseSensor(coordinator, description) for description in SENSOR_TYPES
    )


class CompaniesHouseSensor(CompaniesHouseEntity, SensorEntity):
    entity_description: CompaniesHouseSensorEntityDescription

    def __init__(
        self,
        coordinator: CompaniesHouseDataUpdateCoordinator,
        description: CompaniesHouseSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> StateType | date:
        return self.entity_description.value_fn(self.coordinator.data)
