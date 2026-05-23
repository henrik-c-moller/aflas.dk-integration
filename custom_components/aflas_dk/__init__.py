from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    from .coordinator import AflasCoordinator
    from .api import AflasAPI
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(entry.entry_id, {})

    hass.data[DOMAIN][entry.entry_id]["coordinators"] = {}

    update_interval = entry.options.get("update_interval", 60)
    hass.data[DOMAIN][entry.entry_id]["update_interval"] = update_interval

    api = AflasAPI(
        entry.data["username"],
        entry.data["password"],
        entry.data["vaerknummer"],
    )
    settings = await hass.async_add_executor_job(api.get_settings)
    meters = settings.json().get("maalerNr", [])

    if isinstance(meters, (str, int)):
        meters = [str(meters)]
    elif meters is None:
        meters = []

    if not isinstance(meters, list):
        _LOGGER.warning(
            "Aflas.dk returned unexpected meter list type %s: %s",
            type(meters).__name__,
            meters,
        )
        meters = list(meters) if hasattr(meters, "__iter__") else []

    _LOGGER.debug("Aflas.dk meters found: %s", meters)

    if not meters:
        _LOGGER.warning(
            "Aflas.dk setup completed without any meters from settings. Check credentials or the Aflas.dk API response."
        )

    for meter in meters:
        coordinator = AflasCoordinator(
            hass,
            entry,
            meter,
            update_interval_minutes=update_interval,
        )
        hass.data[DOMAIN][entry.entry_id]["coordinators"][meter] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok

