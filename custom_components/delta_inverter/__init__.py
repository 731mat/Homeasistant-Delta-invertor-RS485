# __init__.py

import logging

logger = logging.getLogger(__name__)

def setup(hass, config, add_entities, discovery_info=None):
    hass.data['delta_inverter'] = {}
    return True
