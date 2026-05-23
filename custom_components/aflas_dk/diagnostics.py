from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
):
    """
    Return diagnostics for a config entry.

    This includes:
    - Config entry data
    - Options (update interval)
    - Meter list
    - Coordinator state per meter
    - Last fetched raw data
    - Failure counters
    """

    data = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})

    diagnostics = {
        "config_entry": {
            "title": entry.title,
            "data": dict(entry.data),
            "options": dict(entry.options),
        },
        "meters": {},
    }

    # Each meter has its own coordinator
    for meter, coordinator in data.get("coordinators", {}).items():
        diagnostics["meters"][meter] = {
            "last_update_success": coordinator.last_update_success,
            "update_interval": str(coordinator.update_interval),
            "normal_interval": str(coordinator._normal_interval),
            "failure_count": coordinator._failure_count,
            "last_data": coordinator.data,
        }

    return diagnostics

