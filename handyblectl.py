#!/usr/bin/env python
#
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

import random 
from PyInquirer import prompt
import buttplug_io
import handy

def linearcmd_build(duration,position):
    # Add message to payload
    payload = buttplug_io.Payload()
    message = payload.Messages.add()
    message.LinearCmd.Id = random.randint(0,4294967295)
    message.LinearCmd.DeviceIndex = 0
    vector = message.LinearCmd.Vectors.add()
    vector.Index = 0
    vector.Duration = duration
    vector.Position = position
    # Convert payload to string
    return payload.SerializeToString()

def inputvalidator(input,lowvalue,highvalue,outtype):
    try:
        return outtype(input)>=lowvalue and outtype(input)<=highvalue
    except ValueError:
        return "Invalid input"

def main():

    # Create a new handy BLE client object
    print("Creating new Handy BLE client")
    handyclient = handy.BLEClient("The Handy")

    # Ask for commands
    while True:
        questions = [
            {
                'type': 'list',
                'name': 'command',
                'message': 'Choose a command',
                'choices': [
                    'Connect',
                    'Disconnect',
                    'LinearCmd'
                ]
            }
        ]
        answer = prompt(questions)

        if (answer['command'] == "Connect"):
            print("Attempting BLE connection")
            try:
                handyclient.connect()
            except RuntimeError as e:
                print(e)
        elif (answer['command'] == "Disconnect"):
            print("Disconnecting")
            try:
                handyclient.disconnect()
            except RuntimeError as e:
                print(e)
        elif (answer['command'] == "LinearCmd"):
            questions = [
                {
                    'type': 'input',
                    'name': 'duration',
                    'message': 'Duration? (ms)',
                    'validate': lambda val: inputvalidator(val,0,4294967295,int)
                },
                {
                    'type': 'input',
                    'name': 'position',
                    'message': 'Position? (0=0%, 1=100%)',
                    'validate': lambda val: inputvalidator(val,0,1,float)
                }
            ]
            answer = prompt(questions)

            request = linearcmd_build(int(answer['duration']),float(answer['position']))
            try:
                response = handyclient.send_data(request)
            except RuntimeError as e:
                print(e)

if __name__ == '__main__':
    main()