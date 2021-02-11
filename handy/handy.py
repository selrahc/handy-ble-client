# Copyright 2021 Sweet Tech AS
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# TODO: Get rid of Transport_BLE class in the future. Only use BLE_Bluez_Client.

import enum
import random
import security
import transport
import threading
from . import handyplug_pb2 as handyplug

class BLEClient:

    class State(enum.Enum):
        CONNECTED = 1
        DISCONNECTED = 2

    class PingTimer(threading.Thread):
        def __init__(self, timeout, client):
            threading.Thread.__init__(self)
            self.timeout = timeout
            self.stopevent = threading.Event()
            self.client = client

        def run(self):
            self.sendping()
            while not self.stopevent.wait(self.timeout):
                self.sendping()

        def stop(self):
            if self.is_alive():
                self.stopevent.set()
                self.join()

        def sendping(self):
            req_payload = handyplug.Payload()
            req_message = req_payload.Messages.add()
            req_message.Ping.Id = random.randint(0, 4294967295)
            req = req_payload.SerializeToString()
            enc_req = self.client.security_ctx.encrypt_data(
                req.decode('latin-1'))
            enc_resp = self.client.bletransport.send_data(
                "handyplug", enc_req)
            resp = self.client.security_ctx.decrypt_data(
                enc_resp.encode('latin-1'))
            resp_payload = handyplug.Payload()
            resp_payload.ParseFromString(resp)
            ok = False
            for resp_message in resp_payload.Messages:
                if resp_message.HasField("Ok") and resp_message.Ok.Id == req_message.Ping.Id:
                    ok = True
                    break
                print(f'Received unexpected message in Ping response, ignoring')
            if not ok:
                raise RuntimeError(
                    f"Incorrect response to Ping (Type:{resp_message.WhichOneof('Message')} resp_id:{resp_message.Ok.Id} req_id:resp_id:{req_message.Ping.Id})")

    def __init__(self, devname, pingtime=3):
        self.devname = devname
        self.state = self.State.DISCONNECTED
        self.maxpingtime = 0
        self.pingtime = pingtime
        self.security_ctx = None
        self.bletransport = None
        self.ping_timer = None

    def connect(self):
        # Only do stuff if we are disconnected
        if self.state is self.State.CONNECTED:
            print("Already connected")
        else:
            try:
                # Initialize BLE connection (yuch, damn espressif it could be better)
                print("Initializing BLE connection")
                self.bletransport = transport.Transport_BLE(devname=self.devname,
                                                            service_uuid='',
                                                            nu_lookup={})

                # Initialize protocomm session with appropriate security scheme
                print("Establishing protocomm session")
                self.security_ctx = security.Security0(False)
                req = self.security_ctx.security_session('')
                resp = self.bletransport.send_data('prov-session', req)
                if not resp:
                    raise RuntimeError(
                        "Could not establish protocomm session (is security scheme correct?")

                # Request server information
                print("Requesting handyplug server information")
                req_payload = handyplug.Payload()
                req_message = req_payload.Messages.add()
                req_message.RequestServerInfo.Id = random.randint(
                    0, 4294967295)
                req = req_payload.SerializeToString()
                enc_req = self.security_ctx.encrypt_data(req.decode('latin-1'))
                enc_resp = self.bletransport.send_data(
                    "handyplug", enc_req)
                resp = self.security_ctx.decrypt_data(
                    enc_resp.encode('latin-1'))

                # Parse information from response
                print("Parsing response")
                resp_payload = handyplug.Payload()
                resp_payload.ParseFromString(resp)
                resp_isok = False
                for resp_message in resp_payload.Messages:
                    if resp_message.HasField("ServerInfo") and resp_message.ServerInfo.Id == req_message.RequestServerInfo.Id:
                        print(
                            f"Received connection information (ServerName:{resp_message.ServerInfo.ServerName} MessageVersion:{resp_message.ServerInfo.MessageVersion} MaxPingTime:{resp_message.ServerInfo.MaxPingTime})")
                        self.maxpingtime = resp_message.ServerInfo.MaxPingTime
                        resp_isok = True
                        break
                    print(f'Received unexpected message in response, ignoring')
                if not resp_isok:
                    raise RuntimeError(
                        "Received incorrect response to RequestServerInfo request")

                # Initialize and start ping timer
                print("Starting ping timer")
                # Creating a new timer is necessary due to the way the threading API works
                self.ping_timer = self.PingTimer(self.pingtime, self)
                self.ping_timer.start()

                # Done!
                self.state = self.State.CONNECTED
                print(f"Connected to {self.devname}")

            except RuntimeError as e:
                print(e)
                self.disconnect()

    def disconnect(self):
        if self.ping_timer:
            self.ping_timer.stop()
        if self.bletransport:
            self.bletransport.disconnect()
        self.state = self.State.DISCONNECTED
        print(f"Disconnected from {self.devname}")

    def send_data(self, data):
        if self.state is self.State.DISCONNECTED:
            raise RuntimeError(
                f"Cannot send data to {self.devname} while disconnected")
        request = self.security_ctx.encrypt_data(data.decode('latin-1'))
        response = self.bletransport.send_data(
            "handyplug", request)
        return self.security_ctx.decrypt_data(response.encode('latin-1'))
