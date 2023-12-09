import paho.mqtt.client as mqtt
import paramiko
import json
import logging

# Logging Configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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
    logging.info(f"Connected with result code {rc}")
    client.subscribe(command_topic)

def on_message(client, userdata, msg):
    logging.info(f"Received command: {msg.payload.decode()}")
    try:
        command = json.loads(msg.payload.decode())
        logging.debug(f"Parsed command: {command}")

        # Initialize SFTP client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(sftp_host, port=sftp_port, username=sftp_username, key_filename=sftp_private_key)
        sftp = ssh.open_sftp()
        logging.debug("SFTP client initialized and connected")

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
        logging.info(f"Response published: {response}")

    except Exception as e:
        error_message = f"Error: {str(e)}"
        client.publish(response_topic, error_message)
        logging.error(error_message)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_address, port, 60)
client.loop_forever()
