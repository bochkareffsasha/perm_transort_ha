"""Сенсор расписания одной остановки."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_ROUTES, CONF_STOP_ID, CONF_STOP_NAME, DOMAIN
from .coordinator import PermTransportCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: PermTransportCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([PermTransportSensor(coordinator, entry)])


class PermTransportSensor(CoordinatorEntity[PermTransportCoordinator], SensorEntity):
    """Минуты до ближайшего автобуса из выбранных маршрутов."""

    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:bus-clock"

    def __init__(
        self, coordinator: PermTransportCoordinator, entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        cfg = {**entry.data, **entry.options}
        self._attr_unique_id = f"{DOMAIN}_{cfg[CONF_STOP_ID]}"
        self._attr_name = cfg.get(CONF_STOP_NAME) or f"Остановка {cfg[CONF_STOP_ID]}"

    @property
    def native_value(self) -> int | None:
        return self.coordinator.data.get("next_minutes")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        cfg = {**self._entry.data, **self._entry.options}
        data = self.coordinator.data
        return {
            "stop_id": cfg.get(CONF_STOP_ID),
            "stop_name": cfg.get(CONF_STOP_NAME),
            "tracked_routes": cfg.get(CONF_ROUTES),
            "routes": data.get("routes", {}),
            "last_update": data.get("last_update"),
        }