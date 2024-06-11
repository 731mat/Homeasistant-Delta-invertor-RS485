# __init__.py

import logging

logger = logging.getLogger(__name__)

def setup(hass, config):
    hass.data['delta_inverter'] = {}
    return True