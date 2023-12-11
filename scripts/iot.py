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
response_topic = "iot/sftp/response"
file_transfer_topic = "iot/sftp/file_transfer"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(response_topic)
    client.subscribe(file_transfer_topic)

def on_message(client, userdata, msg):
    if msg.topic == response_topic:
        print(f"Response: {msg.payload.decode()}")
    elif msg.topic == file_transfer_topic:
        # File content received, write it to a local file
        local_path = '/path/to/destination/file'  # Update this path as needed
        with open(local_path, 'wb') as file:
            file.write(msg.payload)
            print(f"File received and saved to {local_path}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_address, port, 60)

client.loop_start()
input("Press Enter to exit...\n")
client.loop_stop()
client.disconnect()
