# __init__.py
import logging
from homeassistant.core import HomeAssistant
from .sensor import DeltaInverterDevice

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:

    _LOGGER.debug("Starting setup of delta_inverter")

    if 'delta_inverter' not in config:
        _LOGGER.error("DeltaInverter configuration missing in configuration.yaml")
        return False  # Přidáno pro lepší zpracování chyb

    _LOGGER.debug("DeltaInverter configuration found: %s", config['delta_inverter'])


    hass.data['delta_inverter'] = {}
    try:
        for device_config in config['delta_inverter']['devices']:
            device = DeltaInverterDevice(hass, device_config)
            hass.data['delta_inverter'][device_config['name']] = device
            device.start()
    except Exception as e:
        _LOGGER.error("Error setting up Delta Inverter devices: %s", e)
        return False  # Přidáno pro lepší zpracování chyb  

    return True




# import logging

# logger = logging.getLogger(__name__)

# def setup(hass, config):
#     hass.data['delta_inverter'] = {}
#     return True    