import paramiko  # Import the Paramiko library for SSH and SFTP
from getpass import getpass  # Import the getpass library for securely entering passwords

# Initialize the SSH client
ssh = paramiko.SSHClient()  # Create an SSH client object
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Auto-add the server's public key

# Initialize a flag for successful authentication
authentication_success = False

# Collect user input for server connection details
server_ip = input("Please enter the SFTP server IP: ")  # Server IP address
username = input("Please enter the username of the SFTP server: ")  # SSH username
private_key_path = input("Please enter the full path to your private key: ")  # Path to the private SSH key

try:
    # First Authentication Attempt: Without passphrase
    # Load the private key from the provided file path
    private_key = paramiko.RSAKey(filename=private_key_path)
    # Use the private key to attempt SSH connection
    ssh.connect(server_ip, username=username, pkey=private_key)
    # If successful, print a message and update the flag
    print("Successfully authenticated using PKI without passphrase.")
    authentication_success = True

except paramiko.AuthenticationException:
    # Handle case where the first authentication attempt fails
    print("Authentication failed without passphrase. Please enter passphrase for your key.")
    # Ask for the passphrase for the private key
    key_passphrase = getpass("Enter the passphrase for your key: ")

    try:
        # Second Authentication Attempt: With passphrase
        # Load the private key again, this time with the passphrase
        private_key = paramiko.RSAKey(filename=private_key_path, password=key_passphrase)
        # Re-attempt the SSH connection with the passphrase
        ssh.connect(server_ip, username=username, pkey=private_key)
        # If successful, print a message and update the flag
        print("Successfully authenticated using PKI with passphrase.")
        authentication_success = True
    
    except paramiko.AuthenticationException:
        # Handle case where both authentication attempts fail
        print("Authentication failed again, even with passphrase. Please check your credentials or PKI setup.")

except paramiko.SSHException as e:
    # Handle general SSH exceptions
    print(f"SSH error: {e}")

except Exception as e:
    # Handle other unexpected exceptions
    print(f"An unexpected error occurred: {e}")

# Check if any authentication was successful
if authentication_success:
    # Open an SFTP session on the already-established SSH connection
    sftp = ssh.open_sftp()
    # Create an empty file named 'PKI-Test' on the remote server
    with sftp.file('PKI-Test', 'w') as f:
        f.write('')
    # Confirm that the file was created
    print("Successfully created an empty file named 'PKI-Test' on the SFTP server.")
    # Close the SFTP session
    sftp.close()

# Close the SSH connection regardless of outcome
ssh.close()
