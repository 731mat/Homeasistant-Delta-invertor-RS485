# sensor.py
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_time_interval

import serial
import struct
import logging
import asyncio



_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    devices = hass.data['delta_inverter']
    entities = []
    for device_name, device in devices.items():
        entity = DeltaInverterSensor(device)
        device.entities.append(entity)
        entities.append(entity)
    add_entities(entities, True)


class DeltaInverterSensor(Entity):
    def __init__(self, device):
        self._device = device
        self._state = None
        self._attributes = {}

    @property
    def should_poll(self):
        return False  # Zajistěte, že polling je vypnutý, pokud stav aktualizuje zařízení

    def update_state(self, state, attributes):
        self._state = state
        self._attributes = attributes
        self.async_write_ha_state()  # Informuje Home Assistant o změně stavu

    @property
    def name(self):
        return self._device.name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes


class DeltaInverterDevice:
    def __init__(self, hass, config):
        self.hass = hass
        self.name = config.get('name')
        self.port = config.get('port')
        self.baudrate = config.get('baudrate')
        self.address = config.get('address')
        self.entities = []
        self.scan_interval = config.get('scan_interval', 60)
        self.running = True  # Inicializujeme proměnnou pro běh smyčky

        # Naplánování pravidelné aktualizace
        self.update_interval = async_track_time_interval(
            self.hass, self.update_data, self.scan_interval
        )

    def start(self):
        """Spuštění zařízení pro pravidelné aktualizace."""
        _LOGGER.info(f"Starting DeltaInverterDevice for {self.name}")
        self.hass.async_add_job(self.update_data())


    async def update_data(self, now=None):
        """Získá data ze zařízení a aktualizuje entity."""
        data = self.send_query()
        if data is not None:
            state, attributes = self.parse_response(data)
            for entity in self.entities:
                entity.update_state(state, attributes)


    def async_will_remove_from_hass(self):
        """Odstranění časovače při odstranění zařízení z HA."""
        self.update_interval()  # Zrušení naplánované aktualizace
            

    def send_query(self):
        with serial.Serial(self.port, self.baudrate, timeout=10) as ser:
            # Example: send a specific command; adjust as needed
            query = b'\x01\x03\x00\x00\x00\x0A\xC5\xCD'
            ser.write(query)
            return ser.read(200)

    def parse_response(self, response):

        if len(response) < 3:
         return 99999, []

        data_length = response[3]
        data = response[4:data_length+4]

        parsed_data = self.parse_data(response)
        state = parsed_data['AC Power']
        attributes = parsed_data
        return state, attributes


    def parse_data(self,data):
        results = {}
        idx = 6  # Začátek dat za hlavičkou protokolu
        results['SAP Part Number'] = data[idx:idx+11].decode('utf-8').strip()
        idx += 11
        results['SAP Serial Number'] = data[idx:idx+18].decode('utf-8').strip()
        idx += 18
        results['SAP Date Code'] = struct.unpack('>I', data[idx:idx+4])[0]
        idx += 4
        results['SAP Revision'] = struct.unpack('>H', data[idx:idx+2])[0]
        idx += 2
        results['Software Revision AC Control'] = struct.unpack('>H', data[idx:idx+2])[0]
        idx += 2
        results['Software Revision DC Control'] = struct.unpack('>H', data[idx:idx+2])[0]
        idx += 2
        results['Software Revision Display'] = struct.unpack('>H', data[idx:idx+2])[0]
        idx += 2
        results['Software Revision ENS Control'] = struct.unpack('>H', data[idx:idx+2])[0]
        idx += 2
        results['Solar Current at Input 1'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
        idx += 2
        results['Solar Voltage at Input 1'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
        idx += 2
        results['Solar Isolation Resistance at Input 1'] = struct.unpack('>H', data[idx:idx+2])[0]
        idx += 2
        results['Solar Current at Input 2'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
        idx += 2
        results['Solar Voltage at Input 2'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
        idx += 2
        results['Solar Isolation Resistance at Input 2'] = struct.unpack('>H', data[idx:idx+2])[0]
        idx += 2
        results['AC Current'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
        idx += 2
        results['AC Voltage'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
        idx += 2
        results['AC Power'] = struct.unpack('>H', data[idx:idx+2])[0]
        idx += 2
        results['AC Frequency'] = struct.unpack('>H', data[idx:idx+2])[0] / 100
        idx += 2
        results['Supplied AC Energy'] = struct.unpack('>I', data[idx:idx+4])[0] / 1000
        idx += 4
        results['Inverter Runtime'] = struct.unpack('>I', data[idx:idx+4])[0]
        idx += 4
        results['Calculated Temperature at NTC (DC Side)'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
        idx += 2
        results['Solar Input 1 MOV Resistance'] = struct.unpack('>H', data[idx:idx+2])[0]
        idx += 2
        results['Solar Input 2 MOV Resistance'] = struct.unpack('>H', data[idx:idx+2])[0]
        idx += 2
        results['Calculated Temperature at NTC (AC Side)'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
        idx += 2
        results['AC Voltage (AC Control)'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
        idx += 2
        results['AC Frequency (AC Control)'] = struct.unpack('>H', data[idx:idx+2])[0] / 100
        idx += 2
        results['DC Injection Current (AC Control)'] = struct.unpack('>H', data[idx:idx+2])[0]
        idx += 2
        results['AC Voltage (ENS Control)'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
        idx += 2
        results['AC Frequency (ENS Control)'] = struct.unpack('>H', data[idx:idx+2])[0] / 100
        idx += 2
        results['DC Injection Current (ENS Control)'] = struct.unpack('>H', data[idx:idx+2])[0]
        idx += 2
        # Maximální proud vstupu Solar 1
        results['Maximum Solar 1 Input Current'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
        idx += 2
        # Maximální napětí vstupu Solar 1
        results['Maximum Solar 1 Input Voltage'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
        idx += 2
        # Maximální výkon vstupu Solar 1
        results['Maximum Solar 1 Input Power'] = struct.unpack('>H', data[idx:idx+2])[0]
        idx += 2
        # Minimální izolační odpor Solar 1
        results['Minimum Isolation Resistance Solar 1'] = struct.unpack('>H', data[idx:idx+2])[0]
        idx += 2
        # Maximální izolační odpor Solar 1
        results['Maximum Isolation Resistance Solar 1'] = struct.unpack('>H', data[idx:idx+2])[0]
        idx += 2
        # Maximální proud vstupu Solar 2
        results['Maximum Solar 2 Input Current'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
        idx += 2
        # Maximální napětí vstupu Solar 2
        results['Maximum Solar 2 Input Voltage'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
        idx += 2
        # Maximální výkon vstupu Solar 2
        results['Maximum Solar 2 Input Power'] = struct.unpack('>H', data[idx:idx+2])[0]
        idx += 2
        # Minimální izolační odpor Solar 2
        results['Minimum Isolation Resistance Solar 2'] = struct.unpack('>H', data[idx:idx+2])[0]
        idx += 2
        # Maximální izolační odpor Solar 2
        results['Maximum Isolation Resistance Solar 2'] = struct.unpack('>H', data[idx:idx+2])[0]
        idx += 2
        # Maximální proud AC dneška
        results['Maximum AC Current of Today'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
        idx += 2
        # Minimální napětí AC dneška
        results['Minimum AC Voltage of Today'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
        idx += 2
        # Maximální napětí AC dneška
        results['Maximum AC Voltage of Today'] = struct.unpack('>H', data[idx:idx+2])[0] / 10
        idx += 2
        # Maximální výkon AC dneška
        results['Maximum AC Power of Today'] = struct.unpack('>H', data[idx:idx+2])[0]
        idx += 2
        # Minimální frekvence AC dneška
        results['Minimum AC Frequency of Today'] = struct.unpack('>H', data[idx:idx+2])[0] / 100
        idx += 2
        # Maximální frekvence AC dneška
        results['Maximum AC Frequency of Today'] = struct.unpack('>H', data[idx:idx+2])[0] / 100
        idx += 2
        # Dodaná energie AC
        results['Supplied AC Energy'] = struct.unpack('>I', data[idx:idx+4])[0] / 1000
        idx += 4
        # Doba provozu invertoru
        results['Inverter Runtime'] = struct.unpack('>I', data[idx:idx+4])[0]
        idx += 4
        # Globální stav poplachu
        results['Global Alarm Status'] = data[idx]
        idx += 1
        # Stav DC vstupu
        results['Status DC Input'] = data[idx]
        idx += 1
        # Limity DC vstupu
        results['Limits DC Input'] = data[idx]
        idx += 1
        # Stav AC výstupu
        results['Status AC Output'] = data[idx]
        idx += 1
        # Limity AC výstupu
        results['Limits AC Output'] = data[idx]
        idx += 1
        # Stav varování izolace
        results['Isolation Warning Status'] = data[idx]
        idx += 1
        # Porucha hardwaru DC
        results['DC Hardware Failure'] = data[idx]
        idx += 1
        # Porucha hardwaru AC
        results['AC Hardware Failure'] = data[idx]
        idx += 1
        # Porucha hardwaru ENS
        results['ENS Hardware Failure'] = data[idx]
        idx += 1
        # Porucha interního bloku
        results['Internal Bulk Failure'] = data[idx]
        idx += 1
        # Porucha interní komunikace
        results['Internal Communications Failure'] = data[idx]
        idx += 1
        # Porucha hardwaru AC
        results['AC Hardware Disturbance'] = data[idx]
        idx += 1

        return results 



# # sensor.py
# from homeassistant.helpers.entity import Entity
# import serial
# import struct
# import logging
# import json


# logger = logging.getLogger(__name__)

# def setup_platform(hass, config, add_entities, discovery_info=None):
#     # Add devices
#     add_entities([DeltaInverterSensor(hass)])

# class DeltaInverterSensor(Entity):
#     def __init__(self, hass):
#         self._hass = hass
#         self._state = None
#         self._attributes = {}

#     @property
#     def name(self):
#         return 'Delta Inverter'

#     @property
#     def state(self):
#         return self._state

#     @property
#     def extra_state_attributes(self):
#         return self._attributes

#     def update(self):
#         # Implement your serial communication here
#         # This example is simplistic and should be expanded to handle your data retrieval and parsing
#         port = '/dev/ttyUSB0'  # Adjust as necessary
#         baudrate = 9600
#         address = 1
#         command = 96
#         sub_command = 1
#         response = self.send_query(port, baudrate, address, command, sub_command)
#         self._state, self._attributes = self.parse_response(response)

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
    
#     def parse_data_old_notUsage(self, data):
#         results = {}
#         results['SAP Part Number'] = data[0:11].decode('utf-8').strip()
#         results['SAP Serial Number'] = data[11:29].decode('utf-8').strip()
#         results['SAP Date Code'] = struct.unpack('>I', data[29:33])[0]
#         results['SAP Revision'] = struct.unpack('>H', data[33:35])[0]
#         results['Software Revision AC Control'] = struct.unpack('>H', data[35:37])[0]
#         results['Software Revision DC Control'] = struct.unpack('>H', data[37:39])[0]
#         results['Software Revision Display'] = struct.unpack('>H', data[39:41])[0]
#         results['Software Revision ENS Control'] = struct.unpack('>H', data[41:43])[0]
#         results['Solar Current at Input 1'] = struct.unpack('>H', data[43:45])[0] / 10
#         results['Solar Voltage at Input 1'] = struct.unpack('>H', data[45:47])[0] / 10
#         results['Solar Isolation Resistance at Input 1'] = struct.unpack('>H', data[47:49])[0]
#         results['Solar Current at Input 2'] = struct.unpack('>H', data[49:51])[0] / 10
#         results['Solar Voltage at Input 2'] = struct.unpack('>H', data[51:53])[0] / 10
#         results['Solar Isolation Resistance at Input 2'] = struct.unpack('>H', data[53:55])[0]
#         results['AC Current'] = struct.unpack('>H', data[55:57])[0] / 10
#         results['AC Voltage'] = struct.unpack('>H', data[57:59])[0] / 10
#         results['AC Power'] = struct.unpack('>H', data[59:61])[0]
#         results['AC Frequency'] = struct.unpack('>H', data[61:63])[0] / 100
#         results['Supplied AC Energy'] = struct.unpack('>I', data[63:67])[0] / 1000
#         results['Inverter Runtime'] = struct.unpack('>I', data[67:71])[0]
#         results['Calculated Temperature at NTC (DC Side)'] = struct.unpack('>H', data[71:73])[0] / 10
#         results['Solar Input 1 MOV Resistance'] = struct.unpack('>H', data[73:75])[0]
#         results['Solar Input 2 MOV Resistance'] = struct.unpack('>H', data[75:77])[0]
#         results['Calculated Temperature at NTC (AC Side)'] = struct.unpack('>H', data[77:79])[0] / 10
#         results['AC Voltage (AC Control)'] = struct.unpack('>H', data[79:81])[0] / 10
#         results['AC Frequency (AC Control)'] = struct.unpack('>H', data[81:83])[0] / 100
#         results['DC Injection Current (AC Control)'] = struct.unpack('>H', data[83:85])[0]
#         results['AC Voltage (ENS Control)'] = struct.unpack('>H', data[85:87])[0] / 10
#         results['AC Frequency (ENS Control)'] = struct.unpack('>H', data[87:89])[0] / 100
#         results['DC Injection Current (ENS Control)'] = struct.unpack('>H', data[89:91])[0]
#         results['Maximum Solar 1 Input Current'] = struct.unpack('>H', data[91:93])[0] / 10
#         results['Maximum Solar 1 Input Voltage'] = struct.unpack('>H', data[93:95])[0] / 10
#         results['Maximum Solar 1 Input Power'] = struct.unpack('>H', data[95:97])[0]
#         results['Minimum Isolation Resistance Solar 1'] = struct.unpack('>H', data[97:99])[0]
#         results['Maximum Isolation Resistance Solar 1'] = struct.unpack('>H', data[99:101])[0]
#         results['Maximum Solar 2 Input Current'] = struct.unpack('>H', data[101:103])[0] / 10
#         results['Maximum Solar 2 Input Voltage'] = struct.unpack('>H', data[103:105])[0] / 10
#         results['Maximum Solar 2 Input Power'] = struct.unpack('>H', data[105:107])[0]
#         results['Minimum Isolation Resistance Solar 2'] = struct.unpack('>H', data[107:109])[0]
#         results['Maximum Isolation Resistance Solar 2'] = struct.unpack('>H', data[109:111])[0]
#         results['Maximum AC Current of Today'] = struct.unpack('>H', data[111:113])[0] / 10
#         results['Minimum AC Voltage of Today'] = struct.unpack('>H', data[113:115])[0] / 10
#         results['Maximum AC Voltage of Today'] = struct.unpack('>H', data[115:117])[0] / 10
#         results['Maximum AC Power of Today'] = struct.unpack('>H', data[117:119])[0]
#         results['Minimum AC Frequency of Today'] = struct.unpack('>H', data[119:121])[0] / 100
#         results['Maximum AC Frequency of Today'] = struct.unpack('>H', data[121:123])[0] / 100
#         results['Supplied AC Energy'] = struct.unpack('>I', data[123:127])[0] / 1000
#         results['Inverter Runtime'] = struct.unpack('>I', data[127:131])[0]
#         results['Global Alarm Status'] = data[131]
#         results['Status DC Input'] = data[132]
#         results['Limits DC Input'] = data[133]
#         results['Status AC Output'] = data[134]
#         results['Limits AC Output'] = data[135]
#         results['Isolation Warning Status'] = data[136]
#         results['DC Hardware Failure'] = data[137]
#         results['AC Hardware Failure'] = data[138]
#         results['ENS Hardware Failure'] = data[139]
#         results['Internal Bulk Failure'] = data[140]
#         results['Internal Communications Failure'] = data[141]
#         results['AC Hardware Disturbance'] = data[142]
#         #results['History Status Messages'] = data[143:163]

#         return results    

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

#     def send_query(self, port, baudrate, address, command, sub_command, data=b''):
#         # Open serial port
#         ser = serial.Serial(port, baudrate, bytesize=8, parity='N', stopbits=1, timeout=1)

#         # Create query
#         query = self.create_query(address, command, sub_command, data)

#         # Send query
#         ser.write(query)

#         # Read response
#         response = ser.read(200)  # Increase the number of bytes to read
#         ser.close()

#         logger.info('responseee %s', str(response))
#         logger.debug('response %s', str(response))

#         return response

#     def parse_response(self, response):

#         if len(response) < 3:
#             return 99999, []

#         data_length = response[3]
#         data = response[4:data_length+4]

#         parsed_data = self.parse_data(response)
#         state = parsed_data['AC Power']
#         attributes = parsed_data
#         return state, attributes
