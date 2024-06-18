from homeassistant.const import CONF_NAME

DOMAIN = "deltainverter"
DEFAULT_UPDATE_INTERVAL = 20

ATTRIBUTES = {
    "value": {"friendly_name": "Value", "unit_of_measurement": "unit"},
    "attribute1": {"friendly_name": "Attribute 1", "unit_of_measurement": "unit1"},
    "attribute2": {"friendly_name": "Attribute 2", "unit_of_measurement": "unit2", "state_class": "measurement", "device_class": "power"},
    "attribute3": {"friendly_name": "Attribute 3", "unit_of_measurement": "unit3"},
}
