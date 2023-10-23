import json
import os
import paramiko

config_file = 'sftp_config.json'

# Function to load existing configurations
def load_config():
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return {'ip': [], 'username': [], 'password': [], 'private_key_path': []}

# Function to save configurations
def save_config(config):
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)

# Load existing configurations
config = load_config()

# Function to get configuration from the user
def get_config(prompt, key):
    while True:
        print(f"What is the {prompt}?")
        for index, value in enumerate(config[key]):
            print(f"{index + 1}) {value}")
        print(f"{len(config[key]) + 1}) Add new {prompt}")
        
        choice_str = input("Enter your choice: ")
        
        try:
            choice = int(choice_str)
            if choice == len(config[key]) + 1:
                new_value = input(f"Enter new {prompt}: ")
                config[key].append(new_value)
                save_config(config)
                return new_value
            else:
                return config[key][choice - 1]
        except (ValueError, IndexError):
            print("Invalid choice, please try again.")

# Get user inputs
ip = get_config('IP of the SFTP server', 'ip')
username = get_config('username of the SFTP server', 'username')
password = get_config('password of the SFTP server', 'password')
private_key_path = get_config('path of the private key', 'private_key_path')

# Connect to the SFTP server
try:
    try:
        private_key = paramiko.RSAKey(filename=private_key_path)
    except paramiko.PasswordRequiredException:
        passphrase = input("Enter the passphrase for the private key: ")
        private_key = paramiko.RSAKey(filename=private_key_path, password=passphrase)
        
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username=username, pkey=private_key)
    sftp = ssh.open_sftp()
    response = sftp.listdir()
    print("SFTP connection established using PKI")
    print(f"List of files and directories: {response}")
    sftp.close()
    ssh.close()
except Exception as e:
    print(f"An error occurred: {e}")
