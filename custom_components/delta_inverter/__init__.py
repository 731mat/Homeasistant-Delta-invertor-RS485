# __init__.py
def setup(hass, config):
    hass.data['delta_inverter'] = {}
    return True