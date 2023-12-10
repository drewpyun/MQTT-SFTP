import os
import paho.mqtt.client as mqtt
import json

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
remote_path = '/home/test/PKI-Test'  # Ensure this file exists on the SFTP server
directory = '/home/testlaptop-1/Documents/Test'
local_file = 'example.txt'
local_path = os.path.join(directory, local_file)

# Check if the directory exists and is writable
if not os.path.exists(directory):
    try:
        os.makedirs(directory)
        print(f"Directory '{directory}' created successfully.")
    except OSError as error:
        print(f"Failed to create directory '{directory}'. Error: {error}")
        exit(1)
elif not os.access(directory, os.W_OK):
    print(f"Directory '{directory}' is not writable. Check permissions.")
    exit(1)
else:
    print(f"Directory '{directory}' is writable.")

# Prepare the local file for writing
try:
    with open(local_path, 'w') as file:
        file.write('')  # Create an empty file or reset an existing file
    print(f"File '{local_file}' prepared for writing in '{directory}'.")
except OSError as error:
    print(f"Failed to prepare file '{local_file}' in '{directory}'. Error: {error}")
    exit(1)

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
