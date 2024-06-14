# __init__.py
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, HomeAssistantType
from .sensor import DeltaInverterDevice

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistantType, config: ConfigType):
    
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


# # __init__.py

# import logging
# from homeassistant.core import HomeAssistant
# from homeassistant.helpers.typing import ConfigType

# from .sensor import DeltaInverterDevice

# _LOGGER = logging.getLogger(__name__)

# def setup(hass: HomeAssistant, config: ConfigType):
#     if 'delta_inverter' not in config:
#         _LOGGER.error("DeltaInverter configuration missing in configuration.yaml")
#         return False  # Přidáno pro lepší zpracování chyb

#     hass.data['delta_inverter'] = {}
#     try:
#         for device_config in config['delta_inverter']['devices']:
#             device = DeltaInverterDevice(hass, device_config)
#             hass.data['delta_inverter'][device_config['name']] = device
#     except Exception as e:
#         _LOGGER.error("Error setting up Delta Inverter devices: %s", e)
#         return False  # Přidáno pro lepší zpracování chyb

#     return True




# import logging

# logger = logging.getLogger(__name__)

# def setup(hass, config):
#     hass.data['delta_inverter'] = {}
#     return True    