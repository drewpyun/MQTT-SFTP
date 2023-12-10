import paho.mqtt.client as mqtt
import json
import os

# Function definitions
def get_input(prompt, validation_func=None):
    """Prompt the user for input and validate it."""
    while True:
        user_input = input(prompt)
        if not validation_func or validation_func(user_input):
            return user_input
        print("Invalid input. Please try again.")

def valid_ip(address):
    """Validate IP addresses."""
    parts = address.split(".")
    if len(parts) != 4:
        return False
    for item in parts:
        if not item.isdigit() or not 0 <= int(item) <= 255:
            return False
    return True

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    """Handle connection to the MQTT broker."""
    print("Connected with result code " + str(rc))
    client.subscribe(response_topic)

def on_message(client, userdata, msg):
    """Handle incoming MQTT messages."""
    print(f"Response: {msg.payload.decode()}")

# MQTT Configuration
broker_address = get_input("Enter the MQTT broker's IP address: ", valid_ip)
port = 1883  # Standard MQTT port
command_topic = "iot/sftp/command"
response_topic = "iot/sftp/response"

# MQTT Client Setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address, port, 60)

# File Transfer Command Preparation
remote_path = '/home/test/PKI-Test'
local_path = '/home/testlaptop-1/Documents/Test/example.txt'
directory = os.path.dirname(local_path)

# Ensure the local directory exists and is writable
if not os.path.exists(directory):
    try:
        os.makedirs(directory)
    except PermissionError:
        print(f"Permission denied: Unable to create directory {directory}")
        exit(1)

# Send command to perform file transfer action
command = {
    'action': 'get',  # 'get' for download, 'put' for upload
    'remote_path': remote_path,
    'local_path': local_path
}
client.publish(command_topic, json.dumps(command))

# MQTT Loop
client.loop_start()
input("Press Enter to exit...\n")
client.loop_stop()
client.disconnect()
