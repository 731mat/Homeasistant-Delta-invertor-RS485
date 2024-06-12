import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

@config_entries.HANDLERS.register('delta_inverter')
class DeltaInverterConfigFlow(config_entries.ConfigFlow, domain='delta_inverter'):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Zde přidejte logiku pro ověření vstupů
            return self.async_create_entry(title="Delta Inverter", data=user_input)

        data_schema = vol.Schema({
            vol.Required('port', default='/dev/ttyUSB0'): str,
            vol.Required('baudrate', default=9600): int,
            vol.Required('address', default=1): int,
        })

        return self.async_show_form(
            step_id='user', data_schema=data_schema, errors=errors
        )
