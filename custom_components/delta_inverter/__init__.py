# __init__.py

import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .sensor import DeltaInverterDevice

_LOGGER = logging.getLogger(__name__)

def setup(hass: HomeAssistant, config: ConfigType):
    hass.data['delta_inverter'] = {}
    for device_config in config['delta_inverter']['devices']:
        device = DeltaInverterDevice(hass, device_config)
        hass.data['delta_inverter'][device_config['name']] = device
    return True



# import logging

# logger = logging.getLogger(__name__)

# def setup(hass, config):
#     hass.data['delta_inverter'] = {}
#     return True    