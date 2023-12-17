import getpass
import paramiko
import paho.mqtt.client as mqtt
import json

def get_input(prompt, validation_func=None):
    while True:
        user_input = input(prompt)
        if not validation_func or validation_func(user_input):
            return user_input
        print("Invalid input. Please try again.")

# MQTT Broker Configuration
broker_address = "localhost"
port = 1883

# SFTP Server Configuration
sftp_host = get_input("Enter the SFTP server IP address: ")
sftp_port = 22
sftp_username = get_input("Enter the SFTP username: ")
sftp_private_key = get_input("Enter the path to the private key: ")

command_topic = "iot/sftp/command"
response_topic = "iot/sftp/response"
file_transfer_topic = "iot/sftp/file_transfer"

passphrase = getpass.getpass("Enter the passphrase for the private key: ")

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(command_topic)

def on_message(client, userdata, msg):
    print(f"Received command: {msg.payload.decode()}")
    try:
        command = json.loads(msg.payload.decode())
        if command['action'] == 'get':
            print(f"Downloading file from {command['remote_path']} to {command['local_path']}")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            private_key = paramiko.RSAKey(filename=sftp_private_key, password=passphrase)
            ssh.connect(sftp_host, port=sftp_port, username=sftp_username, pkey=private_key)
            sftp = ssh.open_sftp()
            sftp.get(command['remote_path'], command['local_path'])
            sftp.close()
            ssh.close()
            print(f"File downloaded successfully to {command['local_path']}")

            # Reading and sending the file content to the IoT device
            with open(command['local_path'], 'rb') as file:
                file_content = file.read()
                client.publish(file_transfer_topic, file_content)
                print("File content sent to the IoT device.")

        else:
            print("Invalid command received.")
            client.publish(response_topic, "Invalid command.")

    except Exception as e:
        print(f"Error: {str(e)}")
        client.publish(response_topic, f"Error: {str(e)}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address, port, 60)
client.loop_forever()
