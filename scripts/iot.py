import paho.mqtt.client as mqtt
import json
import os

# Function to prompt user for broker address
def get_broker_address():
    return input("Enter the MQTT broker address: ")

# MQTT Broker Configuration
broker_address = get_broker_address()
port = 1883  # Default MQTT port

# MQTT Topics
command_topic = "iot/sftp/command"
response_topic = "iot/sftp/response"

# Called when the client receives CONNACK response from the server
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(response_topic)  # Subscribe to the response topic

# Called when a message has been received on a topic that the client subscribes to
def on_message(client, userdata, msg):
    print(f"Response: {msg.payload.decode()}")

# Create MQTT client instance
client = mqtt.Client()

# Assign event callbacks
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT broker
client.connect(broker_address, port, 60)

# Start the network loop in a separate thread
client.loop_start()

# Local path where the file will be stored
local_path = '/home/testlaptop-1/Documents/example.txt'

# Ensure the directory exists
local_dir = os.path.dirname(local_path)
if not os.path.exists(local_dir):
    os.makedirs(local_dir)

# Command to be sent to the broker - in this case, to download a file
command = {
    'action': 'get',  # Action type ('get' for download, 'put' for upload)
    'remote_path': '/remote/path/to/file',  # Path of the file on the SFTP server
    'local_path': local_path  # Local path where the file will be saved
}

# Publish the command to the MQTT broker
client.publish(command_topic, json.dumps(command))

# Wait for user input before exiting
input("Press Enter to exit...\n")

# Stop the network loop and disconnect from the broker
client.loop_stop()
client.disconnect()
