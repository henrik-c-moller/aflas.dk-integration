from __future__ import annotations

from datetime import timedelta
import asyncio
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import AflasAPI
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class AflasCoordinator(DataUpdateCoordinator):
    """
    Coordinator responsible for fetching usage for ONE specific meter.

    Includes retry-backoff logic:
        - First failure: 5 minutes
        - Second failure: 10 minutes
        - Third failure: 30 minutes
        - Then fallback to user-selected interval
    """

    BACKOFF_STEPS = [
        timedelta(minutes=5),
        timedelta(minutes=10),
        timedelta(minutes=30),
    ]

    def __init__(
        self,
        hass: HomeAssistant,
        entry,
        meter_number: str,
        update_interval_minutes: int,
    ):
        # Store references
        self.hass = hass
        self.entry = entry
        self.meter_number = meter_number

        # Extract credentials
        data = entry.data
        username = data["username"]
        password = data["password"]
        vaerknummer = data["vaerknummer"]

        # API instance bound to this meter
        self.api = AflasAPI(username, password, vaerknummer, meter_number)

        # User-selected update interval
        self.update_interval_minutes = update_interval_minutes
        self._normal_interval = timedelta(minutes=update_interval_minutes)

        # Track consecutive failures
        self._failure_count = 0

        super().__init__(
            hass,
            _LOGGER,
            name=f"Aflas.dk Water Coordinator {meter_number}",
            update_interval=self._normal_interval,
        )

    # ---------------------------------------------------------
    # INTERNAL: APPLY BACKOFF AFTER FAILURE
    # ---------------------------------------------------------
    def _apply_backoff(self):
        """Adjust update interval based on failure count."""
        if self._failure_count == 0:
            self.update_interval = self._normal_interval
            return

        index = min(self._failure_count - 1, len(self.BACKOFF_STEPS) - 1)
        new_interval = self.BACKOFF_STEPS[index]

        _LOGGER.warning(
            "Aflas.dk meter %s: applying retry backoff → next update in %s",
            self.meter_number,
            new_interval,
        )

        self.update_interval = new_interval

    # ---------------------------------------------------------
    # MAIN UPDATE METHOD
    # ---------------------------------------------------------
    async def _async_update_data(self):
        """Fetch data from Aflas.dk (runs in executor thread)."""
        try:
            result = await asyncio.to_thread(self.api.get_usage_data)

            if result is None:
                raise Exception("No data returned from Aflas.dk")

            # SUCCESS → reset backoff
            if self._failure_count > 0:
                _LOGGER.info(
                    "Aflas.dk meter %s: update succeeded → resetting backoff",
                    self.meter_number,
                )

            self._failure_count = 0
            self.update_interval = self._normal_interval

            return result

        except Exception as err:
            # FAILURE → increase counter
            self._failure_count += 1

            _LOGGER.error(
                "Aflas.dk meter %s: update failed (%s) → failure #%s",
                self.meter_number,
                err,
                self._failure_count,
            )

            # Apply retry-backoff
            self._apply_backoff()

            raise UpdateFailed(f"Aflas.dk update failed: {err}") from err

