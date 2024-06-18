# Home Assistant Custom Component for Delta Inverter SI5000


[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=rnovacek&repository=homeassistant_cz_energy_spot_prices&category=integration)


This is a custom integration for Home Assistant that allows you to monitor and control a Delta Inverter via RS485 communication. The integration reads data from the inverter through a serial connection, processes it, and makes it available as sensors in Home Assistant. Below is a comprehensive guide on how to set up and configure this integration.

## Features


- **Real-time Monitoring**: Track real-time data from the Delta Inverter, such as AC power, solar voltage, and current.
- **Device Control**: Send commands to adjust settings directly from Home Assistant (future scope).
- **Extensive Sensor Support**: Supports a wide range of metrics including solar input, AC output, and device statuses.


## Prerequisites


Before you begin, ensure you have:


- Home Assistant installed and running.
- Access to the Home Assistant configuration directory.
- A Delta Inverter connected to the same network as your Home Assistant instance or accessible via a serial connection.


## Installation

1. Copy `custom_components/cz_energy_spot_prices` directory into your `custom_components` in your configuration directory.
2. Restart Home Assistant
3. Open Settings -> Devices & Services -> Integration
4. Search for "Czech Energy Spot Prices" and click the search result
5. Configure Currency and Unit of energy
6. Submit

## Configuration FIX 


| Parameter | Description                       | Example           |
|-----------|-----------------------------------|-------------------|
| `port`    | Serial port where the inverter is connected. | `/dev/ttyUSB0` |
| `baudrate`| Baud rate for the serial connection. | `9600`          |
| `address` | The address of the inverter.      | `1`               |



## Debugging


Enable detailed debug logging by adding the following to your `configuration.yaml` file:


```yaml
logger:
  default: info
  logs:
    custom_components.deltainverter: debug
```


Check the Home Assistant logs for detailed output which will help in troubleshooting.


## Contributing


Contributions to this project are welcome. You can contribute by:


- Reporting issues
- Submitting fixes
- Adding documentation


## License


This project is licensed under the MIT License - see the LICENSE file for details.


```python
import struct

def parse_data(data):
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
  
    ## and more 

    return results


# Předpokládáme, že 'data' je bajtové pole obsahující celou zprávu
data_string = b"\x02\x06\x01\xa1`\x01EOE46020145113144101003000250100310\x02\x00\x02\x00\x02\x00\x02\x00\x00\x00\x01]'\x10\x00\x00\x01['\x10\x00\x00\x00\x01\x00\x00\x00\x00\x00\x8a\x000\x00%\x00\x00\x00\x00\x00)\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\x01k\x00\xa2\x00\x01'\x10\x00\x05\x01i\x00\x9f'\x10'\x10\x00\x0b\x00\x01\x01\x18\x00\xed\x00\x00\x13\x92\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x88\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xde\x18\x03"

# Váš popis začíná číst data od 7. bajtu, takže začneme indexovat od 6 a přečteme 11 bajtů
sap_part_number = data_string[6:6+11].decode('utf-8').strip()

print("SAP Part Number:", sap_part_number)

print(parse_data(data_string))
```