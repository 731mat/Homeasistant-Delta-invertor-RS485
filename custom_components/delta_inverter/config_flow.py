import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
import homeassistant.helpers.config_validation as cv
from .const import DOMAIN, DEFAULT_UPDATE_INTERVAL
import logging

_LOGGER = logging.getLogger(__name__)

class DeltaInverterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            _LOGGER.debug("User input received: %s", user_input)
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        data_schema = {
            vol.Required(CONF_NAME, default="Delta Inverter Sensor"): str,
            vol.Optional("update_interval", default=DEFAULT_UPDATE_INTERVAL): int,
        }

        _LOGGER.debug("Displaying user input form with schema: %s", data_schema)

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(data_schema), errors=errors
        )