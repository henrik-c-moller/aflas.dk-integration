from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import AflasCoordinator
from .sensor_debug import AflasDebugSensor
from .sensor_rolling import AflasRollingUsageSensor
from .sensor_total import AflasTotalSensor
from .sensor_usage import AflasWaterUsageSensor
from .sensor_flow import AflasWaterFlowSensor
from .sensor_update_monitor import AflasLastUpdateSensor
from .utils import parse_aflas_label
from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    """
    Set up Aflas.dk sensors.

    FLOW SENSOR has been moved to sensor_flow.py.
    DAILY USAGE SENSOR is in sensor_usage.py.
    No other logic changed.
    """
    data = hass.data[DOMAIN][entry.entry_id]
    coordinators = data["coordinators"]

    entities = []

    for meter, coordinator in coordinators.items():
        # Daily usage
        entities.append(AflasWaterUsageSensor(coordinator, meter))

        # Flow (now imported from sensor_flow.py)
        entities.append(AflasWaterFlowSensor(coordinator, meter))

        # Rolling usage sensors
        entities.append(AflasRollingUsageSensor(coordinator, meter, 24))
        entities.append(AflasRollingUsageSensor(coordinator, meter, 24 * 7))
        entities.append(AflasRollingUsageSensor(coordinator, meter, 24 * 30))

        # Total meter reading
        entities.append(AflasTotalSensor(coordinator, meter))

        # Debug
        entities.append(AflasDebugSensor(coordinator, meter))
        entities.append(AflasLastUpdateSensor(coordinator, meter))

    async_add_entities(entities, True)
