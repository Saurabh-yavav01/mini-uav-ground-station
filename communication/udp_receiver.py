import socket
import json


HOST = "127.0.0.1"
PORT = 5005


# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind socket to IP and port
sock.bind((HOST, PORT))

print("================================")
print("       GCS UDP RECEIVER")
print("================================")
print(f"Listening on {HOST}:{PORT}")
print("Waiting for UAV telemetry...\n")


while True:

    # Receive data
    data, address = sock.recvfrom(4096)

    # Convert bytes to text
    message = data.decode("utf-8")

    # Convert JSON text to Python dictionary
    telemetry = json.loads(message)

    print("Telemetry received:")
    print(telemetry)
    print()