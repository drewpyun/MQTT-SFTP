import getpass
import paramiko
import paho.mqtt.client as mqtt
import json
import os

broker_address = "localhost"
port = 1883

sftp_host = '10.0.1.194'
sftp_port = 22
sftp_username = 'test'
sftp_private_key = '/home/testlaptop/.ssh/id_rsa_mqtt'

command_topic = "iot/sftp/command"
response_topic = "iot/sftp/response"

passphrase = getpass.getpass("Enter the passphrase for the private key: ")

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(command_topic)

def on_message(client, userdata, msg):
    print(f"Received command: {msg.payload.decode()}")
    try:
        command = json.loads(msg.payload.decode())

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        private_key = paramiko.RSAKey(filename=sftp_private_key, password=passphrase)
        ssh.connect(sftp_host, port=sftp_port, username=sftp_username, pkey=private_key)
        sftp = ssh.open_sftp()

        if command['action'] == 'get':
            local_dir = os.path.dirname(command['local_path'])
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)
            sftp.get(command['remote_path'], command['local_path'])
            response = "File downloaded successfully."
        else:
            response = "Invalid command."

        sftp.close()
        ssh.close()

        client.publish(response_topic, response)

    except Exception as e:
        client.publish(response_topic, f"Error: {str(e)}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_address, port, 60)
client.loop_forever()
