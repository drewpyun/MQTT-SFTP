import paho.mqtt.client as mqtt
import json

# MQTT Broker Configuration
broker_address = "localhost"
broker_address = "10.0.1.214"
port = 1883

# MQTT Topics
command_topic = "iot/sftp/command"
response_topic = "iot/sftp/response"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(response_topic)

def on_message(client, userdata, msg):
    print(f"Response: {msg.payload.decode()}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_address, port, 60)

# Send command to download a file
command = {
    'action': 'get',
    'remote_path': '/remote/path/to/file',
    'local_path': '/local/path/to/store'
}
client.publish(command_topic, json.dumps(command))

client.loop_start()

input("Press Enter to exit...\n")
client.loop_stop()
client.disconnect()
