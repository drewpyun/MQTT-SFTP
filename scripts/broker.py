import getpass
import paramiko
import paho.mqtt.client as mqtt
import json
import os

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
file_transfer_topic = "iot/sftp/file_transfer"

# Prompt for the passphrase
passphrase = getpass.getpass("Enter the passphrase for the private key: ")

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(command_topic)

def on_message(client, userdata, msg):
    print(f"Received command: {msg.payload.decode()}")
    try:
        command = json.loads(msg.payload.decode())

        # Initialize SFTP client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        private_key = paramiko.RSAKey(filename=sftp_private_key, password=passphrase)
        ssh.connect(sftp_host, port=sftp_port, username=sftp_username, pkey=private_key)
        sftp = ssh.open_sftp()

        # Execute command
        if command['action'] == 'get':
            local_path = command['local_path']
            # Ensure the directory exists
            local_dir = os.path.dirname(local_path)
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)

            sftp.get(command['remote_path'], local_path)
            print(f"File downloaded successfully to {local_path}.")

            # Read and send the file content to the IoT device via MQTT
            with open(local_path, 'rb') as file:
                file_content = file.read()
                client.publish(file_transfer_topic, file_content)
                print("File content sent to the IoT device.")

        elif command['action'] == 'put':
            # This part would handle file upload if needed
            pass

        else:
            response = "Invalid command."
            client.publish(response_topic, response)

        sftp.close()
        ssh.close()

    except Exception as e:
        print(f"Error encountered: {str(e)}")
        client.publish(response_topic, f"Error: {str(e)}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_address, port, 60)
client.loop_forever()
