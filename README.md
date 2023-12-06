# MQTT-SFTP Integration Project

## Introduction

This project integrates MQTT and SSH File Transfer Protocol (SFTP) to facilitate secure file exchanges over MQTT. It utilizes OpenSSH for SFTP functionalities and Mosquitto as the MQTT broker. The architecture also incorporates Public Key Infrastructure (PKI) to ensure secure connections between an IoT device, the MQTT broker, and the SFTP server. This repository includes pre-generated key pairs for testing purposes. However, this setup is not recommended for production environments without further security measures.

![network diagram](https://i.imgur.com/hbVA7Cw.png)
## Requirements

- Python 3.11.0-6 (Compatibility with other versions such as 3.10.x or 3.12.x is not tested)
- OpenSSH (Primarily tested on Linux; Windows and macOS versions exist but are not covered here)
- OpenSSL (Primarily tested on Linux; Windows and macOS versions exist but are not covered here)
- Mosquitto (Primarily tested on Linux; Windows and macOS versions exist but are not covered here)
- Install all Python packages using the `requirements.txt` file with `sudo pip install -r requirements.txt`

## Setup 

### OpenSSH Server Installation:

1. Install OpenSSH Server and enable the `sshd` service:

    ```bash
    sudo apt/dnf install openssh-server
    sudo systemctl enable --now sshd
    ```

2. Create a dedicated SFTP user (replace "test" with the desired username):

    ```bash
    sudo adduser test
    sudo passwd test
    ```

3. Configure SSH for SFTP usage:

    Edit the SSHD configuration to enforce SFTP and disable SSH shell access for the user "test":

    ```bash
    sudo nano /etc/ssh/sshd_config
    ```

    Add or modify the following lines:

    ```
    Match User test
    ForceCommand internal-sftp
    ```

    Restart the SSH service to apply changes:

    ```bash
    sudo systemctl restart sshd
    ```

4. Test the SFTP connection from another machine:

    ```bash
    sftp test@sftp_ip
    ```

### Mosquitto Installation and Configuration:

1. Install Mosquitto on both the MQTT broker and IoT device:

    ```bash
    sudo apt/dnf install mosquitto
    sudo systemctl enable --now mosquitto
    ```

2. Edit the Mosquitto configuration file to set up the broker, allowing anonymous connections and binding to all network interfaces:

    ```bash
    sudo nano /etc/mosquitto/mosquitto.conf
    ```

    Add or modify the following lines:

    ```
    allow_anonymous true
    bind_address 0.0.0.0
    ```

3. Test the MQTT broker by subscribing to a topic on the broker and publishing from the IoT device:

    - On the MQTT broker:

    ```bash
    mosquitto_sub -h localhost -t "test/topic"
    ```

    - On the IoT device:

    ```bash
    mosquitto_pub -h broker_ip -t "test/topic" -m "hi world!"
    ```

### PKI Setup for IoT and SFTP Communication:

1. Generate RSA key pairs on the IoT device:

    ```bash
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa_iot
    ```

2. Copy the public key to the SFTP server:

    ```bash
    scp ~/.ssh/id_rsa_iot.pub test@sftp_ip:/home/test/
    ```

3. On the SFTP server, append the IoT device's public key to the `authorized_keys`:

    ```bash
    ssh test@sftp_ip 'cat >> ~/.ssh/authorized_keys' < ~/.ssh/id_rsa_iot.pub
    ```

4. Enable public key authentication and restart the SSH service:

    ```bash
    sudo nano /etc/ssh/sshd_config
    ```

    Uncomment or add:

    ```
    PubkeyAuthentication yes
    ```

    Then restart the SSH service:

    ```bash
    sudo systemctl restart sshd
    ```

5. Test the PKI setup by connecting to the SFTP server from the IoT device:

    ```bash
    ssh -i ~/.ssh/id_rsa_iot test@sftp_ip
    ```

### PKI Setup for IoT and MQTT Broker Communication:

1. On the MQTT Broker, generate the X.509 key for TLS 1.3:

    ```bash
    openssl genpkey -algorithm RSA -out mqtt_server.key
    ```

2. Create the certificate request:

    ```bash
    openssl req -new -key mqtt_server.key -out mqtt_server.csr
    ```

3. Generate a self-signed certificate

 (for testing purposes):

    ```bash
    openssl x509 -req -days 365 -in mqtt_server.csr -signkey mqtt_server.key -out mqtt_server.crt
    ```

4. Move the generated files to the Mosquitto certificates directory and adjust permissions:

    ```bash
    sudo mv mqtt_server.key mqtt_server.csr mqtt_server.crt /etc/mosquitto/certs/
    sudo chown mosquitto:mosquitto /etc/mosquitto/certs/*
    sudo chmod 400 /etc/mosquitto/certs/mqtt_server.key
    sudo chmod 444 /etc/mosquitto/certs/mqtt_server.crt
    ```

5. Transfer the .crt file to the IoT device:

    - On the IoT device:
    ```bash
    mkdir ~/.mqtt/
    scp mqtt_server@mqtt_ip:/etc/mosquitto/certs/mqtt_server.crt ~/.mqtt/
    ```

6. Configure Mosquitto to use TLS and restart the service:

    ```bash
    sudo nano /etc/mosquitto/mosquitto.conf
    ```

    Add:

    ```
    listener 8883
    certfile /etc/mosquitto/certs/mqtt_server.crt
    keyfile /etc/mosquitto/certs/mqtt_server.key
    ```

    Restart Mosquitto:

    ```bash
    sudo systemctl restart mosquitto
    ```

7. Test MQTT over TLS by subscribing on the broker and publishing from the IoT device:

    - On the broker:

    ```bash
    mosquitto_sub -h localhost -p 8883 -t test/topic/pki --cafile /etc/mosquitto/certs/mqtt_server.crt --insecure
    ```

    - On the IoT device:

    ```bash
    mosquitto_pub -h mqtt_ip -p 8883 -t test/topic/pki -m "Hello PKI!" --cafile /path/to/mqtt_server.crt --insecure
    ```

### Install Python dependencies

1. Install all Python dependencies in the requirements.txt

    ```bash
    pip3 install -r requirements.txt
    ```

2. Test installation by running the example "SFTP-PKI-TEST.py" in the test folder

    ```bash
    python3 ./test/SFTP-PKI-TEST.py
    ```
    - Note: Use the full path to the private key (usually /etc/user/.ssh/..)

## Issues 

Should you encounter any permission-related issues while transferring or accessing files, adjust the permissions accordingly. For example:

```bash
chmod -v 755 ./fileOrDirectory
```

Remember that Mosquitto does not read certificates from home directories by default. Place them in `/etc/mosquitto/certs/` or a similar directory with proper permissions. As these are self-signed certificates for testing, the `--insecure` flag is necessary to bypass certificate verification.

---
