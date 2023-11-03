# MQTT-SFTP

## Introduction
This is a Project to utilize both MQTT and SSH FTP (SFTP) protocols to allow for secure file exchanges over MQTT.
This project utilizes the popular OpenSSH suite to handle SFTP client-server functionality, and Mosquitto for the local MQTT Broker.
This project will also utilize Public Key Infrastructure between the IoT Device and MQTT Broker, as well as the MQTT Broker and the SFTP Server. Three pairs of PKI Certs are required and pre-generated for testing purposes. Please do not use this implementation as-is for production networks.



## Requirements
Python 3.11.0-6 (untested on other verisons such as 3.10.- or 3.12.-)
OpenSSH (Can run on Windows/MacOS but primarily tested and documented for Linux)
OpenSSL (Can run on Windows/MacOS but primarily tested and documented for Linux)
Mosquitto (Can run on Windows/MacOS but primarily tested and documented for Linux)
All python packages can be installed using the requirements.txt file using `sudo pip install -r requirements.txt`

## Setup 
1) An SSH FTP (SFTP) server must first be created. 
2) Keypairs must then be generated for the IoT device, SFTP server, and the MQTT broker.
3) Enable Public Key authentication on the SFTP server.
4) Setup the MQTT broker.

## Installation

### Installing OpenSSH Server:
```
sudo apt/dnf/etc. install openssh-server
sudo systemctl enable sshd
sudo systemctl start sshd
sudo systemctl status sshd
```

Creating SFTP User (Replace "test" with your desired username):
```
sudo adduser test
sudo passwd test
```
Configuring SSH for SFTP:
```
sudo vi/vim/nano /etc/ssh/sshd_config
```
Please configure the SSH for your own use. 
For testing I only put the lines below to prevent root access from user "test":
```
Match User test
ForceCommand internal-sftp
```
Restart SSH Service after configuration:
```
sudo systemctl restart sshd
sudo systemctl status sshd
```
Testing Connection:
On another device use the command `sftp test@server_ip`

### Installing Mosquitto 
For this project, we will be using Mosquitto as the MQTT Broker.
On BOTH the MQTT Broker device and the IoT device, install Mosquitto using these commands: 
```
sudo apt/dnf/etc. install mosquitto
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
sudo systemctl status mosquitto
```
To configure the MQTT Broker, on the MQTT Broker device, edit the mosquitto configuration file:
`sudo vi/vim/nano /etc/mosquitto/mosquitto.conf`
For testing purposes, allow anonymous login by changing the line `# allow_anonymous` to `allow_anonymous true`
To route over the local IP network (it is localhost on default) add the line `bind_address 0.0.0.0` under the "Listeners" section
To test, we need the MQTT Broker device to listen to a topic, and the IoT device to publish to a topic.
On the MQTT Broker device run this command: `mosquitto_sub -h localhost -t "test/topic"`
On the IoT Device run this command: `mosquitto_pub -h broker_ip -t "test/topic" -m "hi world!"`

### IoT <-> SFTP PKI Key Generation
On the IoT Device, generate the key pairs. 
`ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa_iot`

Send the public key (id_rsa_iot.pub) to the SFTP server using this command:
`scp ~/.ssh/id_rsa_iot.pub test@your_server_ip:/home/test/` where "test" is the SFTP username created.

Now SSH to the SFTP file server and add the public key to the authorized_key file.
```
ssh test@serverIP
cat id_rsa_iot.pub >> ~/.ssh/authorized_keys
```
Enable Public Key authentication by modifying the sshd_config on the SFTP server:
`sudo vi/vim/nano /etc/ssh/sshd_config` 
Uncomment the line `#PubkeyAuthentication yes`.
Restart the SFTP server
`sudo systemctl restart sshd`
Test the PKI implementation by SSH from the IoT device to the SFTP server:
`ssh -i ~/.ssh/id_rsa_iot test@serverIP`
Test the PKI implementation by running the `SFTP-PKI-TEST.py` file in the test subdirectory.

### IoT <-> MQTT Broker Key Generation
On the MQTT Broker device, generate the private X.509 key for TLS 1.3
`openssl genpkey -algorithm RSA -out mqtt_server.key`
Next, generate the certificate request using the private key
`openssl req -new -key mqtt_server.key -out mqtt_server.csr`
Finally, create the self-signed certificate using the private key and the certificate request.
Note: This is only recommended for a test environemnt. For a production environment, you should have your certificate signed by a certificate authority (CA).
`openssl x509 -req -days 365 -in mqtt_server.csr -signkey mqtt_server.key -out mqtt_server.crt`
After generation of the X.509 .key, the certificate request .csr, and the self-signed certificate .crt, move them to /etc/mosquitto/certs/
```
sudo mkdir /etc/mosquitto/certs/
mv mqtt_server.key /etc/mosquitto/certs/
mv mqtt_server.csr /etc/mosquitto/certs/
mv mqtt_server.cst /etc/mosquitto/certs/
```
Make sure they have the proper permissions for the default Mosquitto user to read.
```
sudo chown mosquitto:mosquitto /etc/mosquitto/certs/
sudo chmod 400 /etc/mosquitto/certs/mqtt_server.key
sudo chmod 444 /etc/mosquitto/certs/mqtt_server.crt
```
Next, configure Mosquitto to use the key and the self-signed certificate.

`sudo vi/vim/nano /etc/mosquitto/mosquitto.conf`
Uncomment `#listener` to `listener 8883 ` to listen on port 8883. (Recommended for TLS)
Uncomment `#certfile` to `certfile /etc/mosquitto/certs/mqtt_server.crt`
Uncomment `#keyfile` to `keyfile /etc/mosquitto/certs/mqtt_server.key`

Restart the Mosquitto server `sudo systemctl restart mosquitto`
Check the status of the server `sudo systemctl status mosquitto`

To test MQTT using TLS 1.3:
Send the 

## Issues 
If you have any Permission denied messages when moving/sending/copying files, make sure the directories and files have proper permissions. Permissions can be changed with chmod `chmod -v -r 755 ./fileOrdirectory` for example.
Mosquitto does not read certificates in home directory. Make sure to put them in another directory like /etc/mosquitto/certs for example, and assign the proper permissions. By default, let user "mosquitto:mosquitto" allow to read the cert files.