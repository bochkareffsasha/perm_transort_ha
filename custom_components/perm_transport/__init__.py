"""Настройка интеграции Perm Transport."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_ROUTES,
    CONF_SCAN_INTERVAL,
    CONF_STOP_ID,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import PermTransportCoordinator


def _cfg(entry: ConfigEntry) -> dict:
    """Совмещаем data и options (options побеждают)."""
    return {**entry.data, **entry.options}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    cfg = _cfg(entry)
    coordinator = PermTransportCoordinator(
        hass,
        stop_id=str(cfg[CONF_STOP_ID]),
        routes=list(cfg[CONF_ROUTES]),
        update_interval=timedelta(
            seconds=int(cfg.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
        ),
    )

    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_reload_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def _reload_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Перезагрузка при изменении настроек через Options."""
    await hass.config_entries.async_reload(entry.entry_id)