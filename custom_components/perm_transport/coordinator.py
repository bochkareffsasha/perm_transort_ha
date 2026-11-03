"""Координатор, который опрашивает API ГорТранса."""
from __future__ import annotations

import asyncio
import logging
import time
from datetime import timedelta
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import API_URL, DOMAIN, HEADERS, REQUEST_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class PermTransportCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Тянет расписание одной остановки и оставляет только нужные маршруты."""

    def __init__(
        self,
        hass: HomeAssistant,
        stop_id: str,
        routes: list[str],
        update_interval: timedelta,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{stop_id}",
            update_interval=update_interval,
        )
        self.stop_id = stop_id
        self.tracked_routes = routes

    async def _async_update_data(self) -> dict[str, Any]:
        url = API_URL.format(stop_id=self.stop_id)
        params = {"_": int(time.time() * 1000)}
        session = async_get_clientsession(self.hass)

        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                resp = await session.get(url, headers=HEADERS, params=params)
                resp.raise_for_status()
                raw = await resp.json(content_type=None)
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise UpdateFailed(
                f"Ошибка запроса к API для остановки {self.stop_id}: {err}"
            ) from err

        return self._parse(raw)

    def _parse(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Оставляем только нужные маршруты в удобном виде."""
        # Порядок ключей — как в настройках пользователя
        routes_str: dict[str, str] = {r: "" for r in self.tracked_routes}
        routes_min: dict[str, list[int]] = {r: [] for r in self.tracked_routes}

        for route_type in raw.get("routeTypes", []) or []:
            for route in route_type.get("routes", []) or []:
                number = str(route.get("routeNumber", "")).strip()
                if number not in routes_str:
                    continue

                times: list[str] = []
                mins: list[int] = []

                for v in route.get("vehicles") or []:
                    at = v.get("arrivalTime") or ""
                    # "18:46:26" -> "18:46"
                    short = at[:5] if len(at) >= 5 else at
                    if short:
                        times.append(short)

                    m = v.get("arrivalMinutes")
                    if isinstance(m, (int, float)):
                        mins.append(int(m))

                routes_str[number] = " ".join(times)
                routes_min[number] = mins

        flat = [m for ms in routes_min.values() for m in ms]
        next_minutes = min(flat) if flat else None

        return {
            "stop_id": self.stop_id,
            "routes": routes_str,
            "routes_minutes": routes_min,
            "next_minutes": next_minutes,
            "last_update": time.time(),
        }