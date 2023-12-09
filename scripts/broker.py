import paho.mqtt.client as mqtt
import paramiko
import json

# MQTT Broker Configuration
broker_address = "localhost"
port = 1883

# SFTP Server Configuration
sftp_host = 'sftp_server_ip'
sftp_port = 22
sftp_username = 'username'
sftp_private_key = '/path/to/private/key'

# MQTT Topics
command_topic = "iot/sftp/command"
response_topic = "iot/sftp/response"

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
        ssh.connect(sftp_host, port=sftp_port, username=sftp_username, key_filename=sftp_private_key)
        sftp = ssh.open_sftp()

        # Execute command
        if command['action'] == 'get':
            sftp.get(command['remote_path'], command['local_path'])
            response = "File downloaded successfully."
        elif command['action'] == 'put':
            sftp.put(command['local_path'], command['remote_path'])
            response = "File uploaded successfully."
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
