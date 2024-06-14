# __init__.py
import logging
from homeassistant.core import HomeAssistant
from .sensor import DeltaInverterDevice

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:

    if 'delta_inverter' not in config:
        _LOGGER.error("DeltaInverter configuration missing in configuration.yaml")
        return False  # Přidáno pro lepší zpracování chyb

    hass.data['delta_inverter'] = {}
    try:
        for device_config in config['delta_inverter']['devices']:
            device = DeltaInverterDevice(hass, device_config)
            hass.data['delta_inverter'][device_config['name']] = device
            await device.start()  # Asynchronní funkce pro zahájení aktualizaci
    except Exception as e:
        _LOGGER.error("Error setting up Delta Inverter devices: %s", e)
        return False  # Přidáno pro lepší zpracování chyb  

    return True


async def async_setup_entry(hass: HomeAssistant, entry):
    _LOGGER.info("Setting up Delta Inverter from config entry")
    device = DeltaInverterDevice(hass, entry.data)
    hass.data.setdefault('delta_inverter', {})[entry.entry_id] = device
    device.start()
    return True    




# import logging

# logger = logging.getLogger(__name__)

# def setup(hass, config):
#     hass.data['delta_inverter'] = {}
#     return True    