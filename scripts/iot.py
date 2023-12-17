import paho.mqtt.client as mqtt
import json
import os

# Function definitions for user input and IP address validation...

def valid_ip(address):
    parts = address.split(".")
    if len(parts) != 4:
        return False
    for item in parts:
        if not item.isdigit() or not 0 <= int(item) <= 255:
            return False
    return True

broker_address = get_input("Enter the MQTT broker's IP address: ", valid_ip)
port = 1883
command_topic = "iot/sftp/command"
response_topic = "iot/sftp/response"
file_transfer_topic = "iot/sftp/file_transfer"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe([(response_topic, 0), (file_transfer_topic, 0)])

def on_message(client, userdata, msg):
    print(f"Response: {msg.payload.decode()}")
    if msg.topic == file_transfer_topic:
        with open(local_path, 'wb') as file:
            file.write(msg.payload)
            print("File received and saved.")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_address, port, 60)
remote_path = '/home/test/PKI-Test'
local_path = '/home/testlaptop/testmqtt.txt'

command = {
    'action': 'get',
    'remote_path': remote_path,
    'local_path': local_path
}
client.publish(command_topic, json.dumps(command))
client.loop_start()
input("Press Enter to exit...\n")
client.loop_stop()
client.disconnect()
