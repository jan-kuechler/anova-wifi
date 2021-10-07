from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TIME_SECONDS, DEVICE_CLASS_TIMESTAMP
from homeassistant.core import HomeAssistant

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from typing import Optional

from .aioanova_wifi import AnovaCooker

from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: callable):
    cooker, coordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([
        ModeSensor(coordinator, cooker),
        TimeRemainingSensor(coordinator, cooker),
    ], True)

class ModeSensor(CoordinatorEntity):
    def __init__(self, coordinator: DataUpdateCoordinator, cooker: AnovaCooker):
        super().__init__(coordinator)
        self.cooker = cooker

    @property
    def state(self):
        return self.cooker.mode

    @property
    def name(self) -> Optional[str]:
        return f'anova mode'

    @property
    def unique_id(self) -> Optional[str]:
        return f'anova_mode'

    @property
    def icon(self) -> Optional[str]:
        return 'mdi:pot-steam'

class TimeRemainingSensor(CoordinatorEntity):
    def __init__(self, coordinator: DataUpdateCoordinator, cooker: AnovaCooker):
        super().__init__(coordinator)
        self.cooker = cooker

    @property
    def unit_of_measurement(self) -> Optional[str]:
        return TIME_SECONDS

    @property
    def state(self):
        return self.cooker.time_remaining

    @property
    def name(self) -> Optional[str]:
        return f'anova time remaining'

    @property
    def unique_id(self) -> Optional[str]:
        return f'anova_time_remaining'

    @property
    def icon(self) -> Optional[str]:
        return 'mdi:timer'