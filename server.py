import socket

UDP_IP = "localhost"
UDP_PORT = 8125

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print("[RECEIVED MESSAGE]: %s" % data.decode('utf-8'))