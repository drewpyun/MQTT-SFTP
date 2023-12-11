import paho.mqtt.client as mqtt
import json
import os

# Function to prompt for broker's IP address
def get_broker_address():
    return input("Enter the MQTT broker's IP address: ")

# MQTT Broker Configuration
broker_address = get_broker_address()
port = 1883

# MQTT Topics
command_topic = "iot/sftp/command"
response_topic = "iot/sftp/response"
file_transfer_topic = "iot/sftp/file_transfer"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe([response_topic, file_transfer_topic])

def on_message(client, userdata, msg):
    if msg.topic == response_topic:
        print(f"Response: {msg.payload.decode()}")
    elif msg.topic == file_transfer_topic:
        print("Received file content.")
        local_path = '/local/path/to/save/file'  # Update with your path
        try:
            with open(local_path, 'wb') as file:
                file.write(msg.payload)
                print(f"File successfully saved to {local_path}")
        except Exception as e:
            print(f"Error saving file: {e}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_address, port, 60)

# Define and send the file transfer command
remote_path = '/remote/path/to/file'  # Update with the file path on the SFTP server
local_path = '/local/path/to/save/file'  # Update with the path where the file should be saved
command = {'action': 'get', 'remote_path': remote_path, 'local_path': local_path}
client.publish(command_topic, json.dumps(command))

client.loop_start()
input("Press Enter to exit...\n")
client.loop_stop()
client.disconnect()
