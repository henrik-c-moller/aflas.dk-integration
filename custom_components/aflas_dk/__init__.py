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
    login_resp = await hass.async_add_executor_job(api.login)
    if login_resp.status_code != 302:
        _LOGGER.warning(
            "Aflas.dk login failed during setup: status=%s response=%s",
            login_resp.status_code,
            login_resp.text[:200],
        )
        _LOGGER.debug(
            "Aflas.dk login response headers=%s cookies=%s",
            login_resp.headers,
            api.session.cookies.get_dict(),
        )
        return False

    settings_resp = await hass.async_add_executor_job(api.get_settings)
    try:
        js = settings_resp.json()
    except Exception as err:
        raw_response = settings_resp.text
        _LOGGER.warning(
            "Aflas.dk settings response was not valid JSON: %s",
            err,
        )
        _LOGGER.debug(
            "Aflas.dk raw settings response: %s",
            raw_response,
        )
        js = {}

    meters = js.get("maalerNr", [])

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

    _LOGGER.debug(
        "Aflas.dk settings status=%s response_json=%s",
        settings_resp.status_code,
        js,
    )
    if not meters:
        _LOGGER.warning(
            "Aflas.dk setup could not find any meters. Check credentials or the Aflas.dk API response."
        )
        _LOGGER.warning(
            "Aflas.dk raw settings response (status %s): %s",
            settings_resp.status_code,
            settings_resp.text,
        )
        return False

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

