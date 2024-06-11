# sensor.py
from homeassistant.helpers.entity import Entity
import serial
import struct

def setup_platform(hass, config, add_entities, discovery_info=None):
    # Add devices
    add_entities([DeltaInverterSensor(hass)])

class DeltaInverterSensor(Entity):
    def __init__(self, hass):
        self._hass = hass
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        return 'Delta Inverter'

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    def update(self):
        # Implement your serial communication here
        # This example is simplistic and should be expanded to handle your data retrieval and parsing
        port = '/dev/ttyUSB0'  # Adjust as necessary
        baudrate = 9600
        address = 1
        command = 96
        sub_command = 1
        response = self.send_query(port, baudrate, address, command, sub_command)
        self._state, self._attributes = self.parse_response(response)

    def parse_data(data):
        results = {}
        results['SAP Part Number'] = data[0:11].decode('utf-8').strip()
        results['SAP Serial Number'] = data[11:29].decode('utf-8').strip()
        results['SAP Date Code'] = struct.unpack('>I', data[29:33])[0]
        results['SAP Revision'] = struct.unpack('>H', data[33:35])[0]
        results['Software Revision AC Control'] = struct.unpack('>H', data[35:37])[0]
        results['Software Revision DC Control'] = struct.unpack('>H', data[37:39])[0]
        results['Software Revision Display'] = struct.unpack('>H', data[39:41])[0]
        results['Software Revision ENS Control'] = struct.unpack('>H', data[41:43])[0]
        results['Solar Current at Input 1'] = struct.unpack('>H', data[43:45])[0] / 10
        results['Solar Voltage at Input 1'] = struct.unpack('>H', data[45:47])[0] / 10
        results['Solar Isolation Resistance at Input 1'] = struct.unpack('>H', data[47:49])[0]
        results['Solar Current at Input 2'] = struct.unpack('>H', data[49:51])[0] / 10
        results['Solar Voltage at Input 2'] = struct.unpack('>H', data[51:53])[0] / 10
        results['Solar Isolation Resistance at Input 2'] = struct.unpack('>H', data[53:55])[0]
        results['AC Current'] = struct.unpack('>H', data[55:57])[0] / 10
        results['AC Voltage'] = struct.unpack('>H', data[57:59])[0] / 10
        results['AC Power'] = struct.unpack('>H', data[59:61])[0]
        results['AC Frequency'] = struct.unpack('>H', data[61:63])[0] / 100
        results['Supplied AC Energy'] = struct.unpack('>I', data[63:67])[0] / 1000
        results['Inverter Runtime'] = struct.unpack('>I', data[67:71])[0]
        results['Calculated Temperature at NTC (DC Side)'] = struct.unpack('>H', data[71:73])[0] / 10
        results['Solar Input 1 MOV Resistance'] = struct.unpack('>H', data[73:75])[0]
        results['Solar Input 2 MOV Resistance'] = struct.unpack('>H', data[75:77])[0]
        results['Calculated Temperature at NTC (AC Side)'] = struct.unpack('>H', data[77:79])[0] / 10
        results['AC Voltage (AC Control)'] = struct.unpack('>H', data[79:81])[0] / 10
        results['AC Frequency (AC Control)'] = struct.unpack('>H', data[81:83])[0] / 100
        results['DC Injection Current (AC Control)'] = struct.unpack('>H', data[83:85])[0]
        results['AC Voltage (ENS Control)'] = struct.unpack('>H', data[85:87])[0] / 10
        results['AC Frequency (ENS Control)'] = struct.unpack('>H', data[87:89])[0] / 100
        results['DC Injection Current (ENS Control)'] = struct.unpack('>H', data[89:91])[0]
        results['Maximum Solar 1 Input Current'] = struct.unpack('>H', data[91:93])[0] / 10
        results['Maximum Solar 1 Input Voltage'] = struct.unpack('>H', data[93:95])[0] / 10
        results['Maximum Solar 1 Input Power'] = struct.unpack('>H', data[95:97])[0]
        results['Minimum Isolation Resistance Solar 1'] = struct.unpack('>H', data[97:99])[0]
        results['Maximum Isolation Resistance Solar 1'] = struct.unpack('>H', data[99:101])[0]
        results['Maximum Solar 2 Input Current'] = struct.unpack('>H', data[101:103])[0] / 10
        results['Maximum Solar 2 Input Voltage'] = struct.unpack('>H', data[103:105])[0] / 10
        results['Maximum Solar 2 Input Power'] = struct.unpack('>H', data[105:107])[0]
        results['Minimum Isolation Resistance Solar 2'] = struct.unpack('>H', data[107:109])[0]
        results['Maximum Isolation Resistance Solar 2'] = struct.unpack('>H', data[109:111])[0]
        results['Maximum AC Current of Today'] = struct.unpack('>H', data[111:113])[0] / 10
        results['Minimum AC Voltage of Today'] = struct.unpack('>H', data[113:115])[0] / 10
        results['Maximum AC Voltage of Today'] = struct.unpack('>H', data[115:117])[0] / 10
        results['Maximum AC Power of Today'] = struct.unpack('>H', data[117:119])[0]
        results['Minimum AC Frequency of Today'] = struct.unpack('>H', data[119:121])[0] / 100
        results['Maximum AC Frequency of Today'] = struct.unpack('>H', data[121:123])[0] / 100
        results['Supplied AC Energy'] = struct.unpack('>I', data[123:127])[0] / 1000
        results['Inverter Runtime'] = struct.unpack('>I', data[127:131])[0]
        results['Global Alarm Status'] = data[131]
        results['Status DC Input'] = data[132]
        results['Limits DC Input'] = data[133]
        results['Status AC Output'] = data[134]
        results['Limits AC Output'] = data[135]
        results['Isolation Warning Status'] = data[136]
        results['DC Hardware Failure'] = data[137]
        results['AC Hardware Failure'] = data[138]
        results['ENS Hardware Failure'] = data[139]
        results['Internal Bulk Failure'] = data[140]
        results['Internal Communications Failure'] = data[141]
        results['AC Hardware Disturbance'] = data[142]
        results['History Status Messages'] = data[143:163]

        return results    

    def calc_crc(data):
        crc = 0x0000
        for pos in data:
            crc ^= pos
            for _ in range(8):
                if (crc & 0x0001) != 0:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc


    def create_query(address, command, sub_command, data=b''):
        stx = 0x02
        enq = 0x05
        etx = 0x03

        # Construct the frame without CRC
        frame = struct.pack('BB', stx, enq) + struct.pack('B', address) + struct.pack('B', len(data) + 2) + struct.pack('B',
                                                                                                                        command) + struct.pack(
            'B', sub_command) + data

        # Calculate CRC
        crc = calc_crc(frame[1:])  # Exclude the first byte (STX) from CRC calculation
        crc_low = crc & 0xFF
        crc_high = (crc >> 8) & 0xFF

        # Construct the final frame with CRC
        frame += struct.pack('BB', crc_low, crc_high) + struct.pack('B', etx)

        return frame

    def send_query(self, port, baudrate, address, command, sub_command):
        # Open serial port
        ser = serial.Serial(port, baudrate, bytesize=8, parity='N', stopbits=1, timeout=1)

        # Create query
        query = create_query(address, command, sub_command, data)

        # Send query
        ser.write(query)

        # Read response
        response = ser.read(200)  # Increase the number of bytes to read
        ser.close()

        return response

    def parse_response(self, response):

        parsed_data = parse_data(data)
        state = parsed_data['AC Power']
        attributes = parsed_data
        return state, attributes
