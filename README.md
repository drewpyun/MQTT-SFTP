# MQTT-SFTP
This is a Project to utilize both MQTT and SSH FTP (SFTP) protocols to allow for secure file exchanges over MQTT.
This project utilizes the popular OpenSSH suite to handle SFTP client-server functionality.

## Requirements
OpenSSH (Can run on Windows/MacOS but primarily tested and documented for Linux)
Mosquitto (Can run on Windows/MacOS but primarily tested and documented for Linux)

## Setup 
An SSH FTP (SFTP) must first be created. 


## Install
Installing OpenSSH Server:
sudo apt/dnf/etc. install openssh-server
sudo systemctl enable sshd
sudo systemctl start sshd
sudo systemctl status sshd

Creating SFTP User (Replace "test" with your desired username)
sudo adduser test
sudo passwd test

Configuring SSH for SFTP:
sudo vi/vim/nano /etc/ssh/sshd_config
Find the line "Sub