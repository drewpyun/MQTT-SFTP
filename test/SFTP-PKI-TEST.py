import json
import os

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
        try:
            choice = int(input("Enter your choice: "))
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

print(f"Selected configurations: IP: {ip}, Username: {username}, Password: {password}, Private Key Path: {private_key_path}")
