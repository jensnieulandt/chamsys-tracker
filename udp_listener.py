import socket

# UDP settings
UDP_IP = "0.0.0.0"  # Listen on all available interfaces
UDP_PORT = 6549

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening on UDP port {UDP_PORT}...")

# Continuous loop to receive and log data
while True:
    data, addr = sock.recvfrom(1024)  # Buffer size of 1024 bytes
    print(f"Received from {addr}: {data.decode()}")
