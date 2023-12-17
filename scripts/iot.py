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
    if msg.topic == response_topic:
        print(f"Response: {msg.payload.decode()}")
    elif msg.topic == file_transfer_topic:
        home_dir = os.path.expanduser('~')
        file_path = os.path.join(home_dir, 'test.txt')  # This will save to '~/test.txt'
        with open(file_path, 'wb') as file:
            file.write(msg.payload)
            print(f"File saved to '{file_path}'")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_address, port, 60)

# Sending a file transfer request
remote_path = '/home/test/PKI-Test'
local_username = get_input("Enter the username of the MQTT broker device:")
local_path = '/home/'+local_username+'/testmqtt.txt'

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
