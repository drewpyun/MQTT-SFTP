import paho.mqtt.client as mqtt
import json
import os

# Function to prompt the user for input and validate it
def get_input(prompt, validation_func=None):
    while True:
        user_input = input(prompt)
        if not validation_func or validation_func(user_input):
            return user_input
        print("Invalid input. Please try again.")

# Function to validate IP addresses
def valid_ip(address):
    parts = address.split(".")
    if len(parts) != 4:
        return False
    for item in parts:
        if not item.isdigit() or not 0 <= int(item) <= 255:
            return False
    return True

# Prompt user for the MQTT broker's IP address
broker_address = get_input("Enter the MQTT broker's IP address: ", valid_ip)
port = 1883  # Standard MQTT port

# MQTT Topics
command_topic = "iot/sftp/command"
response_topic = "iot/sftp/response"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(response_topic)

def on_message(client, userdata, msg):
    print(f"Response: {msg.payload.decode()}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_address, port, 60)

# Define local and remote paths for the file transfer
remote_path = '/home/test/PKI-Test'
local_path = '/home/testlaptop/testmqtt.txt'

# Send command to perform file transfer action
command = {
    'action': 'get',  # 'get' for download, 'put' for upload
    'remote_path': remote_path,
    'local_path': local_path
}
client.publish(command_topic, json.dumps(command))

client.loop_start()

input("Press Enter to exit...\n")
client.loop_stop()
client.disconnect()
