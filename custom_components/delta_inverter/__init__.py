# __init__.py
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.exceptions import PlatformNotReady
from .sensor import DeltaInverterDevice

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    _LOGGER.debug("Starting setup of delta_inverter")

    if 'delta_inverter' not in config:
        _LOGGER.error("DeltaInverter configuration missing in configuration.yaml")
        return False

    delta_config = config['delta_inverter']
    hass.data['delta_inverter'] = {}
    
    try:
        for device_config in delta_config.get('devices', []):
            name = device_config['name']
            port = device_config['port']
            baudrate = device_config['baudrate']
            address = device_config['address']
            scan_interval = device_config['scan_interval']
            
            device = DeltaInverterDevice(hass, name, port, baudrate, address, scan_interval)
            hass.data['delta_inverter'][name] = device
            await device.start()  # Volání start metody je asynchronní

        # Explicitní volání platformy pro senzory
        hass.async_create_task(
            async_load_platform(hass, 'sensor', 'delta_inverter', delta_config, config)
        )
    except Exception as e:
        _LOGGER.error("Error setting up Delta Inverter devices: %s", e)
        raise PlatformNotReady from e

    return True





# import logging

# logger = logging.getLogger(__name__)

# def setup(hass, config):
#     hass.data['delta_inverter'] = {}
#     return True    