from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfVolume
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .utils import parse_aflas_label
from .coordinator import AflasCoordinator


class AflasWaterUsageSensor(CoordinatorEntity, SensorEntity):
    """
    Daily usage sensor (m³) for Aflas.dk.
    Moved from sensor.py without modifying logic.
    """

    _attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS
    _attr_icon = "mdi:water"

    def __init__(self, coordinator: AflasCoordinator, meter_number: str):
        super().__init__(coordinator)
        self._meter = meter_number
        self._attr_name = f"Aflas.dk Water Usage Today {meter_number}"
        self._attr_unique_id = f"aflas_usage_today_{meter_number}"

    @property
    def native_value(self):
        data = self.coordinator.data
        if not data:
            return None

        today = datetime.now().date()
        labels = data["current"].get("labels") or []

        usage = 0.0

        for label in labels:
            parsed = parse_aflas_label(label)
            if not parsed:
                continue

            start_total, end_total, start_dt, end_dt = parsed

            if end_dt.date() == today:
                delta = end_total - start_total
                if delta < 0:
                    delta = 0
                usage += delta

        return round(usage, 3)

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}
        current = data.get("current", {})
        return {
            "meter_number": self._meter,
            "labels": current.get("labels"),
        }

    @property
    def available(self):
        return self.coordinator.last_update_success
