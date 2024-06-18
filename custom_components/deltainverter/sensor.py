import logging
import json
from datetime import timedelta
import voluptuous as vol
import serial_asyncio
import struct
import asyncio

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, DEFAULT_UPDATE_INTERVAL, ATTRIBUTES
from .data_parser import parse_data

_LOGGER = logging.getLogger(__name__)

CONF_NAME = "name"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Optional("update_interval", default=DEFAULT_UPDATE_INTERVAL): cv.positive_int,
})

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    _LOGGER.debug("Setting up platform with config: %s and discovery_info: %s", config, discovery_info)
    if discovery_info is None:
        _LOGGER.error("No configuration data received")
        return

    name = discovery_info.get(CONF_NAME)
    if not name:
        _LOGGER.error("Configuration is missing CONF_NAME")
        return

    update_interval = discovery_info.get("update_interval", DEFAULT_UPDATE_INTERVAL)
    coordinator = DeltaInverterDataUpdateCoordinator(hass, update_interval)
    await coordinator.async_refresh()

    sensors = []
    for attr in ATTRIBUTES:
        sensors.append(DeltaInverterSensor(name, attr, coordinator))
    async_add_entities(sensors)
    _LOGGER.debug("Platform setup complete with sensors: %s", sensors)


class DeltaInverterDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, update_interval):
        self._data = {}
        self.port = '/dev/ttyUSB0'
        self.baudrate = 9600
        _LOGGER.debug("Data update coordinator initialized with interval: %s seconds", update_interval)

        super().__init__(
            hass,
            _LOGGER,
            name="Delta Inverter",
            update_method=self._async_update_data,
            update_interval=timedelta(seconds=update_interval),
        )

    async def _async_update_data(self):
        _LOGGER.debug("Fetching data from serial line: %s", self.port)
        try:
            data = await self.async_send_query()
            if data:
                _LOGGER.debug("Data fetched successfully: %s", data)
                self._data = parse_data(data)
                _LOGGER.debug("Data parsed successfully: %s", self._data)
            else:
                _LOGGER.error("Error fetching data from %s", self.port)
                self._data = {}
        except Exception as e:
            _LOGGER.error("Exception occurred while fetching data: %s", e)
            raise UpdateFailed(f"Error updating data: {e}")

    def get_data(self, attribute):
        _LOGGER.debug("Getting data for attribute: %s", attribute)
        data = self._data.get(attribute, None)
        _LOGGER.debug("Data for %s: %s", attribute, data)
        return data

    async def async_send_query(self):
        address = 1
        command = 96
        sub_command = 1
        data = b''

        reader, writer = await serial_asyncio.open_serial_connection(url=self.port, baudrate=self.baudrate)
        try:
            query = self.create_query(address, command, sub_command, data)
            writer.write(query)
            _LOGGER.debug("XXXXX %s", query)
            await writer.drain()
            response = await reader.read(200)
            return response
        finally:
            writer.close()
            await writer.wait_closed()

    def calc_crc(self, data):
        crc = 0x0000
        for pos in data:
            crc ^= pos
            for _ in range(8):
                if crc & 0x0001:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc

    def create_query(self, address, command, sub_command, data=b''):
        stx = 0x02
        enq = 0x05
        etx = 0x03

        frame = struct.pack('BB', stx, enq) + struct.pack('B', address) + struct.pack('B', len(data) + 2) + struct.pack('B', command) + struct.pack('B', sub_command) + data

        crc = self.calc_crc(frame[1:])
        crc_low = crc & 0xFF
        crc_high = (crc >> 8) & 0xFF

        frame += struct.pack('BB', crc_low, crc_high) + struct.pack('B', etx)
        return frame


class DeltaInverterSensor(Entity):
    def __init__(self, name, attribute, coordinator):
        self._name = f"{name} {ATTRIBUTES[attribute]['friendly_name']}"
        self._state = None
        self._attribute = attribute
        self._coordinator = coordinator
        self.entity_id = f"sensor.{name.lower().replace(' ', '_')}_{attribute}"
        self._unique_id = f"{self.entity_id}"
        _LOGGER.debug("Sensor initialized: %s", self._name)

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return ATTRIBUTES[self._attribute]["unit_of_measurement"]

    async def async_update(self):
        _LOGGER.debug("Updating sensor: %s", self._name)
        self._state = self._coordinator.get_data(self._attribute)
        _LOGGER.debug("Updated state for %s: %s", self._name, self._state)

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.name,
            "manufacturer": "Delta",
            "model": "Inverter Model",
            "entry_type": "service",
            "configuration_url": "https://ha.matyho.cz/config/integrations/integration/deltainverter",
        }

# import asyncio
# from datetime import timedelta
# from homeassistant.helpers.entity import Entity
# from homeassistant.helpers.event import async_track_time_interval
# import serial
# import struct
# import logging

# _LOGGER = logging.getLogger(__name__)

# async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
#     if 'delta_inverter' not in hass.data:
#         _LOGGER.error("DeltaInverter data not found in hass.data")
#         return False

#     entities = []
#     for device_name, device in hass.data['delta_inverter'].items():
#         for measurement in device.measurements:
#             entity = DeltaInverterSensor(device, measurement)
#             entities.append(entity)
#         await device.start()  # Zavolání start metody pro každé zařízení

#     async_add_entities(entities)
#     return True

# class DeltaInverterSensor(Entity):
#     def __init__(self, device, measurement):
#         self._device = device
#         self._measurement = measurement
#         self._state = None
#         self._attributes = {}

#     @property
#     def name(self):
#         return f"{self._device.name} {self._measurement}"

#     @property
#     def state(self):
#         return self._state

#     @property
#     def extra_state_attributes(self):
#         return self._attributes

#     def update(self):
#         data = self._device.get_data()
#         self._state = data.get(self._measurement)
#         self._attributes = data

# class DeltaInverterDevice:
#     def __init__(self, hass, name, port, baudrate, address, scan_interval):
#         self.hass = hass
#         self.name = name
#         self.port = port
#         self.baudrate = baudrate
#         self.address = address
#         self.scan_interval = scan_interval
#         self.measurements = ['SAP Part Number', 'SAP Serial Number']  # Add all measurements
#         self._data = {}
#         self.entities = []

#     async def start(self):
#         await self.update_data(None)
#         self._interval = async_track_time_interval(
#             self.hass, self.update_data, timedelta(seconds=self.scan_interval)
#         )

#     def get_data(self):
#         return self._data

#     async def update_data(self, _):
#         _LOGGER.info(f"Updating data for {self.name}")
#         response = await self.hass.async_add_executor_job(self.fetch_data)
#         if response:
#             self._data.update(self.parse_response(response))
#             for entity in self.entities:
#                 entity.update()
#             _LOGGER.info("Data updated successfully")
#         else:
#             _LOGGER.error(f"No data received from the device {self.name}")

#     def fetch_data(self):
#         with serial.Serial(self.port, self.baudrate, timeout=10) as ser:
#             query = self.create_query(self.address, 96, 1)
#             ser.write(query)
#             response = ser.read(200)
#             return response

#     def create_query(self, address, command, sub_command, data=b''):
#         stx = 0x02
#         enq = 0x05
#         etx = 0x03

#         # Construct the frame without CRC
#         frame = struct.pack('BB', stx, enq) + struct.pack('B', address) + struct.pack('B', len(data) + 2) + struct.pack('B', command) + struct.pack('B', sub_command) + data

#         # Calculate CRC
#         crc = self.calc_crc(frame[1:])  # Exclude the first byte (STX) from CRC calculation
#         crc_low = crc & 0xFF
#         crc_high = (crc >> 8) & 0xFF

#         # Construct the final frame with CRC
#         frame += struct.pack('BB', crc_low, crc_high) + struct.pack('B', etx)

#         return frame
    

#     def calc_crc(self, data):
#         crc = 0xFFFF
#         for byte in data:
#             crc ^= byte
#             for _ in range(8):
#                 if crc & 0x0001:
#                     crc >>= 1
#                     crc ^= 0xA001
#                 else:
#                     crc >>= 1
#         return crc

#     def parse_response(self, data):
#         results = {}
#         idx = 6  # Start of data after protocol header
#         results['SAP Part Number'] = data[idx:idx+11].decode('utf-8').strip()
#         idx += 11
#         results['SAP Serial Number'] = data[idx:idx+18].decode('utf-8').strip()
#         return results



# # sensor.py
# from homeassistant.helpers.entity import Entity
# from homeassistant.helpers.event import async_track_time_interval
# from datetime import timedelta

# import serial
# import struct
# import logging
# import asyncio




# _LOGGER = logging.getLogger(__name__)

# def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
#     _LOGGER.debug("Setting up platform for Delta Inverter")

#      # Ensure all devices are correctly accessed
#     if 'delta_inverter' not in hass.data:
#         _LOGGER.error("DeltaInverter data not found in hass.data")
#         return

#     measurements = {
#         "SAP Part Number": {"unit": "", "device_class": None},
#         "SAP Serial Number": {"unit": "", "device_class": None},
#         "SAP Date Code": {"unit": "", "device_class": None},
#         "SAP Revision": {"unit": "", "device_class": None},
#         "Software Revision AC Control": {"unit": "", "device_class": None},
#         "Software Revision DC Control": {"unit": "", "device_class": None},
#         "Software Revision Display": {"unit": "", "device_class": None},
#         "Software Revision ENS Control": {"unit": "", "device_class": None},
#         "Solar Current at Input 1": {"unit": "A", "device_class": "current"},
#         "Solar Voltage at Input 1": {"unit": "V", "device_class": "voltage"},
#         "Solar Isolation Resistance at Input 1": {"unit": "Ω", "device_class": "resistance"},
#         "Solar Current at Input 2": {"unit": "A", "device_class": "current"},
#         "Solar Voltage at Input 2": {"unit": "V", "device_class": "voltage"},
#         "Solar Isolation Resistance at Input 2": {"unit": "Ω", "device_class": "resistance"},
#         "AC Current": {"unit": "A", "device_class": "current"},
#         "AC Voltage": {"unit": "V", "device_class": "voltage"},
#         "AC Power": {"unit": "W", "device_class": "power"},
#         "AC Frequency": {"unit": "Hz", "device_class": "frequency"},
#         "Supplied AC Energy": {"unit": "kWh", "device_class": "energy"},
#         "Inverter Runtime": {"unit": "hours", "device_class": "duration"},
#         "Calculated Temperature at NTC (DC Side)": {"unit": "°C", "device_class": "temperature"},
#         "Solar Input 1 MOV Resistance": {"unit": "Ω", "device_class": "resistance"},
#         "Solar Input 2 MOV Resistance": {"unit": "Ω", "device_class": "resistance"},
#         "Calculated Temperature at NTC (AC Side)": {"unit": "°C", "device_class": "temperature"},
#         "AC Voltage (AC Control)": {"unit": "V", "device_class": "voltage"},
#         "AC Frequency (AC Control)": {"unit": "Hz", "device_class": "frequency"},
#         "DC Injection Current (AC Control)": {"unit": "A", "device_class": "current"},
#         "AC Voltage (ENS Control)": {"unit": "V", "device_class": "voltage"},
#         "AC Frequency (ENS Control)": {"unit": "Hz", "device_class": "frequency"},
#         "DC Injection Current (ENS Control)": {"unit": "A", "device_class": "current"},
#         "Maximum Solar 1 Input Current": {"unit": "A", "device_class": "current"},
#         "Maximum Solar 1 Input Voltage": {"unit": "V", "device_class": "voltage"},
#         "Maximum Solar 1 Input Power": {"unit": "W", "device_class": "power"},
#         "Minimum Isolation Resistance Solar 1": {"unit": "Ω", "device_class": "resistance"},
#         "Maximum Isolation Resistance Solar 1": {"unit": "Ω", "device_class": "resistance"},
#         "Maximum Solar 2 Input Current": {"unit": "A", "device_class": "current"},
#         "Maximum Solar 2 Input Voltage": {"unit": "V", "device_class": "voltage"},
#         "Maximum Solar 2 Input Power": {"unit": "W", "device_class": "power"},
#         "Minimum Isolation Resistance Solar 2": {"unit": "Ω", "device_class": "resistance"},
#         "Maximum Isolation Resistance Solar 2": {"unit": "Ω", "device_class": "resistance"},
#         "Maximum AC Current of Today": {"unit": "A", "device_class": "current"},
#         "Minimum AC Voltage of Today": {"unit": "V", "device_class": "voltage"},
#         "Maximum AC Voltage of Today": {"unit": "V", "device_class": "voltage"},
#         "Maximum AC Power of Today": {"unit": "W", "device_class": "power"},
#         "Minimum AC Frequency of Today": {"unit": "Hz", "device_class": "frequency"},
#         "Maximum AC Frequency of Today": {"unit": "Hz", "device_class": "frequency"},
#         "Global Alarm Status": {"unit": "", "device_class": None},
#         "Status DC Input": {"unit": "", "device_class": None},
#         "Limits DC Input": {"unit": "", "device_class": None},
#         "Status AC Output": {"unit": "", "device_class": None},
#         "Limits AC Output": {"unit": "", "device_class": None},
#         "Isolation Warning Status": {"unit": "", "device_class": None},
#         "DC Hardware Failure": {"unit": "", "device_class": None},
#         "AC Hardware Failure": {"unit": "", "device_class": None},
#         "ENS Hardware Failure": {"unit": "", "device_class": None},
#         "Internal Bulk Failure": {"unit": "", "device_class": None},
#         "Internal Communications Failure": {"unit": "", "device_class": None},
#         "AC Hardware Disturbance": {"unit": "", "device_class": None}
#     }


#     entities = []

#      # Loop over each device stored in hass.data
#     entities = []
#     for device_name, device in hass.data['delta_inverter'].items():
#         _LOGGER.debug(f"Setting up sensor for device: {device_name}")
#         for key, params in measurements.items():
#             _LOGGER.debug("Adding entity for device: %s", key)
#             entity = DeltaInverterSensor(device, key, key, params["unit"], params["device_class"])
#             entities.append(entity)
#             device.entities.append(entity)  # Přidání entity do seznamu entit zařízení

#     async_add_entities(entities, True)


# class DeltaInverterSensor(Entity):
#     def __init__(self, device, name, measurement, unit=None, device_class=None):
#         self._device = device
#         self._name = name
#         self._state = None
#         self._attributes = {}
#         self._measurement = measurement
#         self._unit = unit
#         self._device_class = device_class

#     @property
#     def should_poll(self):
#         return False  # Zajistěte, že polling je vypnutý, pokud stav aktualizuje zařízení

#     def update_state(self, state, attributes):
#         self._state = state
#         self._attributes = attributes
#         self.async_write_ha_state()  # Informuje Home Assistant o změně stavu

#     def update(self):
#         _LOGGER.debug("Updating Delta Inverter Sensor")
#         """Fetch new state data for the sensor."""
#         self._state = self._device.data.get(self._measurement)
#         if self._state is None:
#             _LOGGER.error("Failed to update sensor")


# #    def update(self):
# #        _LOGGER.debug("Updating Delta Inverter Sensor")
# #        """Aktualizace stavu entity."""
# #        self._state, self._attributes = self._device.get_status()
# #        if self._state is None:
# #            _LOGGER.error("Failed to update sensor") 


#     @property
#     def name(self):
#         """Return the display name of this sensor."""
#         return f"{self._device.name} {self._name}"

#     @property
#     def device_class(self):
#         """Return the class of this device, from DEVICE_CLASS_*."""
#         return self._device_class

#     @property
#     def unit_of_measurement(self):
#         """Return the unit of measurement."""
#         return self._unit

#     @property
#     def state(self):
#         return self._state

#     @property
#     def extra_state_attributes(self):
#         return self._attributes


# class DeltaInverterDevice:
#     def __init__(self, hass, config):
#         self.hass = hass
#         self.name = config.get('name')
#         self.port = config.get('port')
#         self.baudrate = config.get('baudrate')
#         self.address = config.get('address')
#         self.entities = []
        
#         # Zkontrolujte, že scan_interval je číslo a převeďte ho na timedelta
#         scan_interval = config.get('scan_interval', 60)  # získáte číslo v sekundách
#         self.scan_interval = timedelta(seconds=scan_interval)  # převeďte na timedelta


#         self.running = True  # Inicializujeme proměnnou pro běh smyčky

#         # Naplánování pravidelné aktualizace
#         self.update_interval = async_track_time_interval(
#             self.hass, self.update_data, self.scan_interval
#         )

#     def calc_crc(self, data):
#         crc = 0x0000
#         for pos in data:
#             crc ^= pos
#             for _ in range(8):
#                 if (crc & 0x0001) != 0:
#                     crc >>= 1
#                     crc ^= 0xA001
#                 else:
#                     crc >>= 1
#         return crc


#     def create_query(self, address, command, sub_command, data=b''):
#         stx = 0x02
#         enq = 0x05
#         etx = 0x03

#         # Construct the frame without CRC
#         frame = struct.pack('BB', stx, enq) + struct.pack('B', address) + struct.pack('B', len(data) + 2) + struct.pack('B',
#                                                                                                                         command) + struct.pack(
#             'B', sub_command) + data

#         # Calculate CRC
#         crc = self.calc_crc(frame[1:])  # Exclude the first byte (STX) from CRC calculation
#         crc_low = crc & 0xFF
#         crc_high = (crc >> 8) & 0xFF

#         # Construct the final frame with CRC
#         frame += struct.pack('BB', crc_low, crc_high) + struct.pack('B', etx)

#         return frame


#     def start(self):
#         """Spuštění zařízení pro pravidelné aktualizace."""
#         _LOGGER.info(f"Starting DeltaInverterDevice for {self.name}")
#         self.hass.async_create_task(self.update_data())


#     async def update_data(self, now=None):
#         _LOGGER.debug("Running update_data for %s", self.name)
#         data = self.send_query()
#         if data is not None:
#             _LOGGER.debug("Data received from device: %s", data)
#             parsed_data = self.parse_data(data)
#             for entity in self.entities:
#                 state = parsed_data.get(entity._measurement)
#                 attributes = {'last_update': now.isoformat()}  # Přidání dalších atributů podle potřeby
#                 entity.update_state(state, attributes)
#         else:
#             _LOGGER.error("No data received from the device")





#     def async_will_remove_from_hass(self):
#         """Odstranění časovače při odstranění zařízení z HA."""
#         self.update_interval()  # Zrušení naplánované aktualizace
            

#     def send_query(self):

#         address = 1
#         command = 96
#         sub_command = 1
#         data=b''

#         with serial.Serial(self.port, self.baudrate, timeout=10) as ser:
#             query = self.create_query(address, command, sub_command, data)
#             ser.write(query)
#             return ser.read(200)



#     def parse_data(self,data):
#         results = {}
#         idx = 6  # Začátek dat za hlavičkou protokolu
#         results['SAP Part Number'] = data[idx:idx+11].decode('utf-8').strip()
#         idx += 11
#         results['SAP Serial Number'] = data[idx:idx+18].decode('utf-8').strip()
#         idx += 18
#         results['SAP Date Code'] = struct.unpack('>I', data[idx:idx+4])[0]
#         idx += 4
#         results['SAP Revision'] = struct.unpack('>H', data[idx:idx+2])[0]
#         idx += 2
#         results['Software Revision AC Control'] = struct.unpack('>H', data[idx:idx+2])[0]
#         idx += 2
#         results['Software Revision DC Control'] = struct.unpack('>H', data[idx:idx+2])[0]
#         idx += 2
#         results['Software Revision Display'] = struct.unpack('>H', data[idx:idx+2])[0]
#         idx += 2
#         results['Software Revision ENS Control'] = struct.unpack('>H', data[idx:idx+2])[0]
#         idx += 2
#         results['Solar Current at Input 1'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
#         idx += 2
#         results['Solar Voltage at Input 1'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
#         idx += 2
#         results['Solar Isolation Resistance at Input 1'] = struct.unpack('>H', data[idx:idx+2])[0]
#         idx += 2
#         results['Solar Current at Input 2'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
#         idx += 2
#         results['Solar Voltage at Input 2'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
#         idx += 2
#         results['Solar Isolation Resistance at Input 2'] = struct.unpack('>H', data[idx:idx+2])[0]
#         idx += 2
#         results['AC Current'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
#         idx += 2
#         results['AC Voltage'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
#         idx += 2
#         results['AC Power'] = struct.unpack('>H', data[idx:idx+2])[0]
#         idx += 2
#         results['AC Frequency'] = struct.unpack('>H', data[idx:idx+2])[0] / 100
#         idx += 2
#         results['Supplied AC Energy'] = struct.unpack('>I', data[idx:idx+4])[0] / 1000
#         idx += 4
#         results['Inverter Runtime'] = struct.unpack('>I', data[idx:idx+4])[0]
#         idx += 4
#         results['Calculated Temperature at NTC (DC Side)'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
#         idx += 2
#         results['Solar Input 1 MOV Resistance'] = struct.unpack('>H', data[idx:idx+2])[0]
#         idx += 2
#         results['Solar Input 2 MOV Resistance'] = struct.unpack('>H', data[idx:idx+2])[0]
#         idx += 2
#         results['Calculated Temperature at NTC (AC Side)'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
#         idx += 2
#         results['AC Voltage (AC Control)'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
#         idx += 2
#         results['AC Frequency (AC Control)'] = struct.unpack('>H', data[idx:idx+2])[0] / 100
#         idx += 2
#         results['DC Injection Current (AC Control)'] = struct.unpack('>H', data[idx:idx+2])[0]
#         idx += 2
#         results['AC Voltage (ENS Control)'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
#         idx += 2
#         results['AC Frequency (ENS Control)'] = struct.unpack('>H', data[idx:idx+2])[0] / 100
#         idx += 2
#         results['DC Injection Current (ENS Control)'] = struct.unpack('>H', data[idx:idx+2])[0]
#         idx += 2
#         # Maximální proud vstupu Solar 1
#         results['Maximum Solar 1 Input Current'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
#         idx += 2
#         # Maximální napětí vstupu Solar 1
#         results['Maximum Solar 1 Input Voltage'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
#         idx += 2
#         # Maximální výkon vstupu Solar 1
#         results['Maximum Solar 1 Input Power'] = struct.unpack('>H', data[idx:idx+2])[0]
#         idx += 2
#         # Minimální izolační odpor Solar 1
#         results['Minimum Isolation Resistance Solar 1'] = struct.unpack('>H', data[idx:idx+2])[0]
#         idx += 2
#         # Maximální izolační odpor Solar 1
#         results['Maximum Isolation Resistance Solar 1'] = struct.unpack('>H', data[idx:idx+2])[0]
#         idx += 2
#         # Maximální proud vstupu Solar 2
#         results['Maximum Solar 2 Input Current'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
#         idx += 2
#         # Maximální napětí vstupu Solar 2
#         results['Maximum Solar 2 Input Voltage'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
#         idx += 2
#         # Maximální výkon vstupu Solar 2
#         results['Maximum Solar 2 Input Power'] = struct.unpack('>H', data[idx:idx+2])[0]
#         idx += 2
#         # Minimální izolační odpor Solar 2
#         results['Minimum Isolation Resistance Solar 2'] = struct.unpack('>H', data[idx:idx+2])[0]
#         idx += 2
#         # Maximální izolační odpor Solar 2
#         results['Maximum Isolation Resistance Solar 2'] = struct.unpack('>H', data[idx:idx+2])[0]
#         idx += 2
#         # Maximální proud AC dneška
#         results['Maximum AC Current of Today'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
#         idx += 2
#         # Minimální napětí AC dneška
#         results['Minimum AC Voltage of Today'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
#         idx += 2
#         # Maximální napětí AC dneška
#         results['Maximum AC Voltage of Today'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
#         idx += 2
#         # Maximální výkon AC dneška
#         results['Maximum AC Power of Today'] = struct.unpack('>H', data[idx:idx+2])[0]
#         idx += 2
#         # Minimální frekvence AC dneška
#         results['Minimum AC Frequency of Today'] = struct.unpack('>H', data[idx:idx+2])[0] / 100
#         idx += 2
#         # Maximální frekvence AC dneška
#         results['Maximum AC Frequency of Today'] = struct.unpack('>H', data[idx:idx+2])[0] / 100
#         idx += 2
#         # Dodaná energie AC
#         results['Supplied AC Energy'] = struct.unpack('>I', data[idx:idx+4])[0] / 1000
#         idx += 4
#         # Doba provozu invertoru
#         results['Inverter Runtime'] = struct.unpack('>I', data[idx:idx+4])[0]
#         idx += 4
#         # Globální stav poplachu
#         results['Global Alarm Status'] = data[idx]
#         idx += 1
#         # Stav DC vstupu
#         results['Status DC Input'] = data[idx]
#         idx += 1
#         # Limity DC vstupu
#         results['Limits DC Input'] = data[idx]
#         idx += 1
#         # Stav AC výstupu
#         results['Status AC Output'] = data[idx]
#         idx += 1
#         # Limity AC výstupu
#         results['Limits AC Output'] = data[idx]
#         idx += 1
#         # Stav varování izolace
#         results['Isolation Warning Status'] = data[idx]
#         idx += 1
#         # Porucha hardwaru DC
#         results['DC Hardware Failure'] = data[idx]
#         idx += 1
#         # Porucha hardwaru AC
#         results['AC Hardware Failure'] = data[idx]
#         idx += 1
#         # Porucha hardwaru ENS
#         results['ENS Hardware Failure'] = data[idx]
#         idx += 1
#         # Porucha interního bloku
#         results['Internal Bulk Failure'] = data[idx]
#         idx += 1
#         # Porucha interní komunikace
#         results['Internal Communications Failure'] = data[idx]
#         idx += 1
#         # Porucha hardwaru AC
#         results['AC Hardware Disturbance'] = data[idx]
#         idx += 1

#         return results 


