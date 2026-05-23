from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import AflasCoordinator
from .const import DOMAIN


class AflasDebugSensor(CoordinatorEntity, SensorEntity):
    """
    Debug sensor for Aflas.dk.

    Exposes:
    - Raw API data
    - Coordinator state
    - Failure counters
    - Update intervals
    - Meter number
    """

    _attr_entity_category = "diagnostic"
    _attr_icon = "mdi:bug"

    def __init__(self, coordinator: AflasCoordinator, meter_number: str):
        super().__init__(coordinator)
        self._meter = meter_number

        self._attr_name = f"Aflas.dk Debug {meter_number}"
        self._attr_unique_id = f"aflas_debug_{meter_number}"

    @property
    def native_value(self):
        """Return a simple status string."""
        return "OK" if self.coordinator.last_update_success else "ERROR"

    @property
    def extra_state_attributes(self):
        """Return detailed debug information."""
        c = self.coordinator

        return {
            "meter_number": self._meter,
            "last_update_success": c.last_update_success,
            "failure_count": c._failure_count,
            "update_interval": str(c.update_interval),
            "normal_interval": str(c._normal_interval),
            "last_data": c.data,
        }

    @property
    def available(self):
        return True  # Always available for debugging

