from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers import discovery
from .const import DOMAIN

import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    _LOGGER.debug("Setting up Delta Inverter integration")
    return True

async def async_setup_entry(hass, entry):
    _LOGGER.debug("Setting up entry for Delta Inverter integration")
    # Ensure that the sensor platform gets the configuration data.
    await discovery.async_load_platform(hass, 'sensor', DOMAIN, entry.data, entry)
    return True

async def async_unload_entry(hass, entry):
    _LOGGER.debug("Unloading entry for Delta Inverter integration")
    return True
