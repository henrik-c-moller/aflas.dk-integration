from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfVolume
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .utils import parse_aflas_label
from .coordinator import AflasCoordinator


class AflasWaterFlowSensor(CoordinatorEntity, SensorEntity):
    """
    Flow sensor (m³/h) for Aflas.dk.
    Moved from sensor.py without modifying logic.
    """

    _attr_native_unit_of_measurement = f"{UnitOfVolume.CUBIC_METERS}/h"
    _attr_icon = "mdi:water-pump"

    def __init__(self, coordinator: AflasCoordinator, meter_number: str):
        super().__init__(coordinator)
        self._meter = meter_number
        self._attr_name = f"Aflas.dk Water Flow {meter_number}"
        self._attr_unique_id = f"aflas_flow_{meter_number}"

    @property
    def native_value(self):
        data = self.coordinator.data
        if not data:
            return None

        labels = data["current"].get("labels") or []
        if len(labels) < 2:
            return None

        p1 = parse_aflas_label(labels[-2])
        p2 = parse_aflas_label(labels[-1])

        if not p1 or not p2:
            return None

        s1, e1, _, dt1 = p1
        s2, e2, _, dt2 = p2

        delta_usage = (e2 - s2) - (e1 - s1)
        if delta_usage < 0:
            delta_usage = 0

        delta_hours = (dt2 - dt1).total_seconds() / 3600
        if delta_hours <= 0:
            return None

        return round(delta_usage / delta_hours, 4)

    @property
    def extra_state_attributes(self):
        return {
            "meter_number": self._meter,
            "calculation": "flow = Δusage / Δhours",
        }

    @property
    def available(self):
        return self.coordinator.last_update_success
