# Handy BLE client

Simple BLE client to showcase direct communication with the Handy using a handyplug-like messaging protocol.

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

The Handy simulates a handyplug-like server, to which a client can connect by establishing a Protocomm BLE session and send Google Protobuf packets on top of it. Here are a few links about these technologies:
- Protocomm overview: https://docs.espressif.com/projects/esp-idf/en/v4.0.2/api-reference/provisioning/provisioning.html
- Google Protobuf: https://developers.google.com/protocol-buffers/

A client is thus first required to establish a Protocomm session over BLE, and then send Google Protobuf packets to the `handyplug` protocomm endpoint as defined by the /handy/handyplug.proto file. The protocol definition resembles a buttplug.io syntax in the hope to provide a familiar mean to 3rd party developers and allow easy integration with the existing buttplug.io ecosystem (using the Google.Protobuf.JsonFormatter class on the protocol definition provides a near-compatible JSON representation).

The overall procedure looks like the following:
- A client connects to the Handy via BLE and establishes a Protocomm session with security profile 0. See sample code for details.
- Once the session is established, the client sends an information request (RequestServerInfo) to get the maximum allowed ping time before the connection is reset
- The client then proceeds to send Ping packets at regular intervals, to which the Handy replies with Ok messages.
- Commands like LinearCmd can now be sent.
