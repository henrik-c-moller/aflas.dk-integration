from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .utils import parse_aflas_label


class AflasLastUpdateSensor(CoordinatorEntity, SensorEntity):
    """
    Tracks the last 3 updates of the 'today' interval from Aflas.dk.
    """

    _attr_icon = "mdi:update"

    def __init__(self, coordinator, meter):
        super().__init__(coordinator)
        self._meter = meter
        self._attr_name = f"Aflas.dk Last Updates {meter}"
        self._attr_unique_id = f"aflas_last_updates_{meter}"

        # Store last 3 updates as list of dicts:
        # [{ "value": float, "time": datetime }, ...]
        self._history = []

        # Track last seen value
        self._last_value = None

    @property
    def native_value(self):
        """
        Returns the timestamp of the most recent update.
        """
        data = self.coordinator.data
        if not data:
            return None

        labels = data["current"].get("labels") or []
        if len(labels) < 2:
            return None

        # Today interval is always second-to-last
        parsed = parse_aflas_label(labels[-2])
        if not parsed:
            return None

        _, end_total, _, _ = parsed

        now = datetime.now()

        # First run
        if self._last_value is None:
            self._last_value = end_total
            self._history.insert(0, {"value": end_total, "time": now})
            self._history = self._history[:3]
            return now.isoformat()

        # Detect change
        if end_total != self._last_value:
            self._last_value = end_total
            self._history.insert(0, {"value": end_total, "time": now})
            self._history = self._history[:3]

        # Return timestamp of most recent update
        return self._history[0]["time"].isoformat()

    @property
    def extra_state_attributes(self):
        """
        Expose the last 3 updates as attributes.
        """
        return {
            "meter_number": self._meter,
            "updates": [
                {
                    "value": entry["value"],
                    "time": entry["time"].isoformat(),
                }
                for entry in self._history
            ],
        }

    @property
    def available(self):
        return self.coordinator.last_update_success
