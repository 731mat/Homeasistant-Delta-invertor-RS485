# Home Assistant Custom Component for Delta Inverter


This custom component for Home Assistant enables integration with the Delta Inverter, allowing you to monitor various parameters such as AC power, solar input, and more directly from your Home Assistant instance.


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


1. **Clone the Repository**


   Navigate to your Home Assistant configuration directory and clone this repository into the `custom_components` directory. If the directory does not exist, create it.


   ```bash
   cd /path/to/your/homeassistant/config
   mkdir -p custom_components
   cd custom_components
   git clone https://github.com/yourusername/delta_inverter.git
   ```


2. **Configure the Component**


   Add the following lines to your `configuration.yaml` file:


   ```yaml
   sensor:
     - platform: delta_inverter
       port: /dev/ttyUSB0
       baudrate: 9600
       address: 1
   ```


   Replace `/dev/ttyUSB0` with your inverter's connection port, and adjust other parameters as necessary.


## Configuration


| Parameter | Description                       | Example           |
|-----------|-----------------------------------|-------------------|
| `port`    | Serial port where the inverter is connected. | `/dev/ttyUSB0` |
| `baudrate`| Baud rate for the serial connection. | `9600`          |
| `address` | The address of the inverter.      | `1`               |


## Usage


Once installed and configured, the component will automatically fetch data from your Delta Inverter and create sensor entities in Home Assistant. These entities can be used in automation, scripts, or viewed directly in the UI.


## Debugging


Enable detailed debug logging by adding the following to your `configuration.yaml` file:


```yaml
logger:
  default: info
  logs:
    custom_components.delta_inverter: debug
```


Check the Home Assistant logs for detailed output which will help in troubleshooting.


## Contributing


Contributions to this project are welcome. You can contribute by:


- Reporting issues
- Submitting fixes
- Adding documentation


## License


This project is licensed under the MIT License - see the LICENSE file for details.