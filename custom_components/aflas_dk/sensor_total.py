from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfVolume
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .utils import parse_aflas_label


class AflasTotalSensor(CoordinatorEntity, SensorEntity):
    """
    Shows the current total meter reading from Aflas.dk.

    Logic:
    - Scan labels from newest → oldest
    - Return the LAST label where end_total > 0
    - If none found → use index 0
    """

    _attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS
    _attr_icon = "mdi:counter"

    def __init__(self, coordinator, meter):
        super().__init__(coordinator)
        self._meter = meter
        self._attr_name = f"Aflas.dk Total {meter}"
        self._attr_unique_id = f"aflas_total_{meter}"

    @property
    def native_value(self):
        data = self.coordinator.data
        if not data:
            return None

        labels = data["current"].get("labels") or []
        if not labels:
            return None

        # Scan from newest → oldest
        for label in reversed(labels):
            parsed = parse_aflas_label(label)
            if not parsed:
                continue

            _, end_total, _, _ = parsed

            if end_total > 0:
                return round(end_total, 3)

        # Fallback: use index 0 if everything else is zero
        parsed = parse_aflas_label(labels[0])
        if parsed:
            _, end_total, _, _ = parsed
            return round(end_total, 3)

        return None

    @property
    def extra_state_attributes(self):
        return {
            "meter_number": self._meter,
            "source": "last label where end_total > 0",
        }

    @property
    def available(self):
        return self.coordinator.last_update_success
