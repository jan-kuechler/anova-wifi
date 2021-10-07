"""The AnovaWifi integration."""
from __future__ import annotations

import logging

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN

from .aioanova_wifi import AnovaCooker

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["sensor"]

class AnovaDataUpdateCoordinator(DataUpdateCoordinator):
    update_failed_count = 0

    @callback
    def _schedule_refresh(self) -> None:
        if not self.last_update_success:
            self.update_failed_count += 1
        else:
            self.update_failed_count = 0

        self.update_interval = timedelta(seconds=15 if self.update_failed_count < 3 else 300)
        super()._schedule_refresh()


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the AnovaWifi component."""
    hass.data[DOMAIN] = {}

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up AnovaWifi from a config entry."""
    cooker = AnovaCooker(entry.data['device_id'])

    async def async_update_data():
        try:
            await cooker.update_state()
        except RuntimeError:
            pass
        else:
            return cooker.state

    coordinator = AnovaDataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f'{entry.data["device_id"]} updater',
        update_method=async_update_data,
        update_interval=timedelta(seconds=15)
    )

    await coordinator.async_refresh()


    async def async_svc_refresh(service):
        _LOGGER.info("Refreshing from service call")
        await coordinator.async_refresh()

    hass.services.async_register(DOMAIN, 'refresh', async_svc_refresh)

    hass.data[DOMAIN][entry.entry_id] = (cooker, coordinator)
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
