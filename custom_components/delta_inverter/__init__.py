# __init__.py

import logging

logger = logging.getLogger(__name__)

#def setup(hass, config, add_entities, discovery_info=None):
#    hass.data['delta_inverter'] = {}
#    return True

async def async_setup(hass, config):
    """Set up the Delta Inverter component from configuration.yaml (if any)."""
    hass.data.setdefault('delta_inverter', {})
    
    return True

async def async_setup_entry(hass, entry):
    """Set up Delta Inverter from a config entry."""
    hass.data['delta_inverter'][entry.entry_id] = entry.data

    # Optional: Setup platforms
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, 'sensor')
    )

    return True    

async def async_unload_entry(hass, entry):
    """Handle removal of an entry."""
    # Unload platforms
    await hass.config_entries.async_forward_entry_unload(entry, 'sensor')
    # Remove saved data
    del hass.data['delta_inverter'][entry.entry_id]

    return True    