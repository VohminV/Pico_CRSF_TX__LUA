# CRSF LoRa Communication with Binding and Parameter Management

This project implements a CRSF (Crossfire) communication system using LoRa modules with SX127x chips. The system supports binding between transmitter (TX) and receiver (RX), as well as parameter management (frequency and power) via CRSF packets. It is designed for use with RadioMaster devices and similar setups.

## Features

- **CRSF Communication**: Full-duplex communication via a single pin using the CRSF protocol.
- **Binding Support**: TX can send binding commands, and RX processes them.
- **Parameter Management**: Update and save frequency and power settings received from the TX.
- **NVS Storage**: Save frequency and power settings persistently on the RX device.
- **Semi-Duplex Pin Switching**: Dynamically switches the CRSF pin between input and output modes.
- **LoRa Configuration**: Uses the SX127x module for robust wireless communication.

## Components Required

- ESP32 or Raspberry Pi Pico board
- SX127x LoRa module (e.g., SX1278)
- CRSF-compatible transmitter (e.g., RadioMaster TX)
- GPIO connections for LoRa SPI and CRSF pin

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/VohminV/Pico_CRSF_TX__LUA.git
   cd crsf-lora-communication
   ```

2. Install required dependencies:
   - `machine` module for GPIO and SPI
   - `sx127x` driver for LoRa communication

3. Deploy the code to your microcontroller using your preferred IDE (e.g., Thonny, VS Code with Pymakr).

## Wiring

| Pin        | Pico Pin         | Description               |
|------------|------------------|---------------------------|
| `SCK`      | GPIO2            | SPI Clock                 |
| `MOSI`     | GPIO3            | SPI MOSI                 |
| `MISO`     | GPIO4            | SPI MISO                 |
| `CS`       | GPIO5            | LoRa Chip Select          |
| `RESET`    | GPIO6            | LoRa Reset                |
| `DIO0`     | GPIO7            | LoRa Interrupt Pin        |
| `CRSF_PIN` | GPIO16           | CRSF Data Pin (semi-duplex)|

## Usage

### TX Mode (Transmitter)

1. The transmitter sends a binding command to the receiver:
   ```python
   tx_mode()
   ```
2. Sends CRSF packets with updated frequency and power settings.

### RX Mode (Receiver)

1. The receiver listens for CRSF packets and processes them:
   ```python
   packet = receive_crsf_packet()
   process_crsf_packet(packet)
   ```
2. Saves and applies frequency and power settings received from the transmitter.

### Binding Process

1. The transmitter sends a binding packet using:
   ```python
   send_crsf_packet(bind_packet)
   ```
2. The receiver acknowledges the binding and stores the binding information.

## Configuration

The following default values are used:

- Frequency: 868.0 MHz
- Power: 100 mW

These values can be updated dynamically via CRSF packets.

## File Overview

- `main.py`: Core implementation for CRSF communication and LoRa control.

## Future Improvements

- Add error checking and CRC validation for received packets.
- Expand support for additional CRSF commands.
- Integrate with more complex flight controller systems.

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please fork this repository and submit a pull request with your improvements.
