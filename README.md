# MQTT-SFTP

## Introduction
This is a Project to utilize both MQTT and SSH FTP (SFTP) protocols to allow for secure file exchanges over MQTT.
This project utilizes the popular OpenSSH suite to handle SFTP client-server functionality, and Mosquitto for the local MQTT Broker.
This project will also utilize Public Key Infrastructure between the IoT Device and MQTT Broker, as well as the MQTT Broker and the SFTP Server. Three pairs of PKI Certs are required and pre-generated for testing purposes. Please do not use this implementation as-is for production networks.



## Requirements
OpenSSH (Can run on Windows/MacOS but primarily tested and documented for Linux)
Mosquitto (Can run on Windows/MacOS but primarily tested and documented for Linux)

## Setup 
An SSH FTP (SFTP) server must first be created. 


## Installation:

### Installing OpenSSH Server:
sudo apt/dnf/etc. install openssh-server
sudo systemctl enable sshd
sudo systemctl start sshd
sudo systemctl status sshd

Creating SFTP User (Replace "test" with your desired username):
sudo adduser test
sudo passwd test

Configuring SSH for SFTP:
sudo vi/vim/nano /etc/ssh/sshd_config
Please configure the SSH for your own use. 
For testing I only put the lines below to prevent root access from user "test:
Match User test
ForceCommand internal-sftp

Restart SSH Service after configuration:
sudo systemctl restart sshd
sudo systemctl status sshd

Testing Connection:
On another device use the command "sftp test@server_ip"

### PKI Key Generation

