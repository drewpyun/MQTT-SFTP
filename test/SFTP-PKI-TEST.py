import json
import os
import paramiko

config_file = 'sftp_config.json'

def load_config():
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return {'ip': [], 'username': [], 'password': [], 'private_key_path': []}

def save_config(config):
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)

config = load_config()

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

ip = get_config('IP of the SFTP server', 'ip')
username = get_config('username of the SFTP server', 'username')
password = get_config('password of the SFTP server', 'password')
private_key_path = get_config('path of the private key', 'private_key_path')

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        private_key = paramiko.RSAKey(filename=private_key_path)
        ssh.connect(ip, username=username, pkey=private_key)
        print("Connected using key-based authentication.")
    except paramiko.PasswordRequiredException:
        passphrase = input("Enter the passphrase for the private key: ")
        private_key = paramiko.RSAKey(filename=private_key_path, password=passphrase)
        ssh.connect(ip, username=username, pkey=private_key)
        print("Connected using key-based authentication with passphrase.")
    except Exception as e:
        print(f"Failed to use key-based authentication: {e}")
        ssh.connect(ip, username=username, password=password)
        print("Connected using password-based authentication.")

    sftp = ssh.open_sftp()
    current_directory = sftp.getcwd()
    response = sftp.listdir()
    print(f"SFTP connection established using PKI")
    print(f"List of files and directories in {current_directory}: {response}")
    sftp.close()
    ssh.close()
except Exception as e:
    print(f"An error occurred: {e}")
