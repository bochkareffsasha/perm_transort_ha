"""UI-настройка интеграции Perm Transport."""
from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    API_URL,
    CONF_ROUTES,
    CONF_SCAN_INTERVAL,
    CONF_STOP_ID,
    CONF_STOP_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    HEADERS,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
    REQUEST_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)


async def _validate_stop(hass, stop_id: str) -> bool:
    """Проверяем, что сервер вообще знает такую остановку (HTTP 200)."""
    session = async_get_clientsession(hass)
    try:
        async with asyncio.timeout(REQUEST_TIMEOUT):
            resp = await session.get(
                API_URL.format(stop_id=stop_id),
                headers=HEADERS,
                params={"_": int(time.time() * 1000)},
            )
            return resp.status == 200
    except (aiohttp.ClientError, asyncio.TimeoutError):
        return False


def _parse_routes(value: str) -> list[str]:
    return [r.strip() for r in value.replace(",", " ").split() if r.strip()]


class PermTransportConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Мастер добавления остановки."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            stop_id = str(user_input[CONF_STOP_ID]).strip()
            routes = _parse_routes(str(user_input[CONF_ROUTES]))

            if not stop_id.isdigit():
                errors["base"] = "invalid_stop_id"
            elif not routes:
                errors["base"] = "no_routes"
            else:
                ok = await _validate_stop(self.hass, stop_id)
                if not ok:
                    errors["base"] = "cannot_connect"
                else:
                    await self.async_set_unique_id(f"{DOMAIN}_{stop_id}")
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=user_input[CONF_STOP_NAME] or f"Остановка {stop_id}",
                        data={
                            CONF_STOP_NAME: user_input[CONF_STOP_NAME]
                            or f"Остановка {stop_id}",
                            CONF_STOP_ID: stop_id,
                            CONF_ROUTES: routes,
                            CONF_SCAN_INTERVAL: int(
                                user_input.get(
                                    CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                                )
                            ),
                        },
                    )

        schema = vol.Schema(
            {
                vol.Required(CONF_STOP_NAME): str,
                vol.Required(CONF_STOP_ID): str,
                vol.Required(CONF_ROUTES): str,
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): vol.All(
                    int, vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)
                ),
            }
        )
        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return PermTransportOptionsFlow()


class PermTransportOptionsFlow(config_entries.OptionsFlow):
    """Изменение настроек без переустановки."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={
                    CONF_STOP_NAME: user_input[CONF_STOP_NAME],
                    CONF_ROUTES: _parse_routes(str(user_input[CONF_ROUTES])),
                    CONF_SCAN_INTERVAL: int(user_input[CONF_SCAN_INTERVAL]),
                },
            )

        cfg = {**self.config_entry.data, **self.config_entry.options}
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_STOP_NAME, default=cfg.get(CONF_STOP_NAME, "")
                ): str,
                vol.Required(
                    CONF_ROUTES,
                    default=", ".join(cfg.get(CONF_ROUTES, [])),
                ): str,
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=cfg.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ): vol.All(
                    int, vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)