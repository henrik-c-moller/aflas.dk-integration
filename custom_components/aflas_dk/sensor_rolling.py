from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfVolume
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import AflasCoordinator
from .utils import parse_aflas_label


class AflasRollingUsageSensor(CoordinatorEntity, SensorEntity):
    """
    Rolling usage sensor for Aflas.dk.

    Computes usage over:
    - last 24 hours
    - last 7 days
    - last 30 days
    """

    _attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS
    _attr_icon = "mdi:chart-line"

    def __init__(self, coordinator: AflasCoordinator, meter: str, window_hours: int):
        super().__init__(coordinator)
        self._meter = meter
        self._window_hours = window_hours

        label = (
            "24h" if window_hours == 24 else
            "7d" if window_hours == 24 * 7 else
            "30d"
        )

        self._attr_name = f"Aflas.dk Water Usage {label} {meter}"
        self._attr_unique_id = f"aflas_usage_{label}_{meter}"

    @property
    def native_value(self):
        """Compute rolling usage."""
        data = self.coordinator.data
        if not data:
            return None

        current = data.get("current", {})
        labels = current.get("labels") or []
        usage = current.get("usage") or []

        if not labels or not usage:
            return None

        cutoff = datetime.now() - timedelta(hours=self._window_hours)

        total = 0.0

        for i, label in enumerate(labels):
            parsed = parse_aflas_label(label)
            if not parsed:
                continue

            start_dt, end_dt = parsed

            # Only count usage where the END timestamp is within the window
            if end_dt >= cutoff:
                try:
                    total += float(usage[i])
                except Exception:
                    continue

        return round(total, 3)

    @property
    def extra_state_attributes(self):
        return {
            "meter_number": self._meter,
            "window_hours": self._window_hours,
            "window_label": (
                "24h" if self._window_hours == 24 else
                "7d" if self._window_hours == 24 * 7 else
                "30d"
            ),
        }

    @property
    def available(self):
        return self.coordinator.last_update_success

