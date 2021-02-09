# Handy BLE client

Simple BLE client to showcase direct communication with the Handy using a buttplug.io-like messaging protocol.

Direct BLE communication with the Handy is available starting with firmware 3.0.0-beta2. BLE can be activated by long-pressing the WiFi button until the LED becomes blue.

While intended as a cross-platform tool, currently the BLE client **only works on Linux** via BlueZ and DBus. Windows and MacOS backends implementations are welcome contributions.

## Linux setup

First install the necessary python requirements with:

`pip install -r requirements.txt`

`pip install -r requirements_linux_extra.txt`

Then start the client with:

`python handybleclient.py`

## Protocol details

Starting with firmware 3.0.0-beta2, the Handy can communicate via BLE and accept commands from a client to move its stroker.

The Handy simulates a buttplug.io-like server, to which a client can connect by establishing a Protocomm BLE session and send Google Protobuf packets on top of it. Here are a few links about these technologies:
- Protocomm overview: https://docs.espressif.com/projects/esp-idf/en/v4.0.2/api-reference/provisioning/provisioning.html
- Google Protobuf: https://developers.google.com/protocol-buffers/

A client is thus first required to establish a Protocomm session over BLE, and then send Google Protobuf packets to the `buttplug.io` protocomm endpoint as defined by the /buttplug_io/buttplug_io.proto file. The protocol definition resembles the original buttplug.io syntax in the hope that it will provide a familiar syntax to 3rd party developers, as well as improve compatibility with the existing buttplug.io ecosystem (using the Google.Protobuf.JsonFormatter class on the protocol definition provides a JSON representation which can be easily manipulated to be fully compatible with the original specification).

Once the Protocomm session is established, the client is required to perform the usual buttplug.io handshake procedure (RequestServerInfo->ServerInfo) and regularly send Ping packets.

For obvious reasons, only the LinearCmd directive is internally supported. Other commands will return an error.
