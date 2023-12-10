import paho.mqtt.client as mqtt
import json

<<<<<<< HEAD
# MQTT Broker Configuration
broker_address = "localhost"
broker_address = "10.0.1.214"
port = 1883
=======
# Configuration details for connecting to the MQTT broker.
broker_address = "localhost"  # The IP address or hostname of the MQTT broker.
port = 1883                  # The port on which the MQTT broker is listening.
>>>>>>> a1e5a89fa242d9b5b1e90ddfd2ceeba8d570da23

# MQTT Topics
command_topic = "iot/sftp/command"
response_topic = "iot/sftp/response"
# MQTT topics for sending commands and receiving responses.
command_topic = "iot/sftp/command"   # Topic for sending SFTP commands to the broker.
response_topic = "iot/sftp/response" # Topic for receiving responses from the broker.

# Called when the client successfully connects to the broker.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(response_topic)
    client.subscribe(response_topic)  # Subscribe to the response topic.

# Called when a message is received from the broker.
def on_message(client, userdata, msg):
    print(f"Response: {msg.payload.decode()}")
    print(f"Response: {msg.payload.decode()}")  # Print the response from the broker.

# Create an MQTT client instance.
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_connect = on_connect  # Assign the on_connect function.
client.on_message = on_message  # Assign the on_message function.

# Connect to the MQTT broker.
client.connect(broker_address, port, 60)

# Send command to download a file
# Command to be sent to the MQTT broker.
command = {
    'action': 'get',
    'remote_path': '/remote/path/to/file',
    'local_path': '/local/path/to/store'
    'action': 'get',  # Type of SFTP action ('get' for download).
    'remote_path': '/remote/path/to/file',  # Path of the file on the SFTP server.
    'local_path': '/local/path/to/store'    # Path to store the file on the IoT device.
}

# Convert the command dictionary to a JSON string and publish it to the broker.
client.publish(command_topic, json.dumps(command))

# Start the network loop in a separate thread.
client.loop_start()

# Wait for the user to press Enter before exiting.
input("Press Enter to exit...\n")

# Stop the network loop and disconnect from the broker.
client.loop_stop()
client.disconnect()
