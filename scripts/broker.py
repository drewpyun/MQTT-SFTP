import getpass
import paramiko
import paho.mqtt.client as mqtt
import json
import logging

# Enable logging for more detailed debug output
logging.basicConfig(level=logging.DEBUG)

# MQTT Broker Configuration
broker_address = "localhost"
port = 1883

# SFTP Server Configuration
sftp_host = '10.0.1.194'
sftp_port = 22
sftp_username = 'test'
sftp_private_key = '/home/testlaptop/.ssh/id_rsa_mqtt'

# MQTT Topics
command_topic = "iot/sftp/command"
response_topic = "iot/sftp/response"

# Prompt for the passphrase
passphrase = getpass.getpass("Enter the passphrase for the private key: ")

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(command_topic)

def on_message(client, userdata, msg):
    try:
        print(f"Received command: {msg.payload.decode()}")
        command = json.loads(msg.payload.decode())

        # Initialize SFTP client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        private_key = paramiko.RSAKey(filename=sftp_private_key, password=passphrase)
        ssh.connect(sftp_host, port=sftp_port, username=sftp_username, pkey=private_key)
        sftp = ssh.open_sftp()

        # Execute command
        if command['action'] == 'get':
            print(f"Downloading file from {command['remote_path']} to {command['local_path']}")
            sftp.get(command['remote_path'], command['local_path'])
            response = "File downloaded successfully."
        elif command['action'] == 'put':
            print(f"Uploading file from {command['local_path']} to {command['remote_path']}")
            sftp.put(command['local_path'], command['remote_path'])
            response = "File uploaded successfully."
        else:
            response = "Invalid command."

        sftp.close()
        ssh.close()

    except Exception as e:
        print(f"Error encountered: {e}")
        response = f"Error: {e}"

    client.publish(response_topic, response)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_address, port, 60)
client.loop_forever()
