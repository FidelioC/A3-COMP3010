import socket
import json
import uuid
# TODO:
# 1. GOSSIP
# 2. Consensus
# 3. Create Chain
# 4. Add Block

# echo '{"type": "GOSSIP", "host": "130.179.28.110", "port": 8999, "id": 1, "name": "Hello World!",}' | nc -u 130.179.28.37 8999

MY_HOST, MY_PORT = "130.179.28.127", 8759
SILICON_HOST, SILICON_PORT = "silicon.cs.umanitoba.ca", 8999


def announce_network(my_host, my_port, known_socket):
    gossip_message = {
        "type": "GOSSIP",
        "host": my_host,
        "port": my_port,
        "id": str(uuid.uuid4()),
        "name": "da!",
    }

    known_socket.sendto(json.dumps(gossip_message).encode(), (SILICON_HOST, SILICON_PORT))

def gossip(my_host, my_port):
    # TODO:
    # 1. connect to one well-known host
    known_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    announce_network(my_host, my_port, known_socket)
    # 2. Reply gossip message received
    print()

def my_server(my_host,my_port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind((my_host, my_port))

        print(f"Server listening on host {my_host} and PORT {my_port}")
        gossip(my_host, my_port)

        while True:

            data, addr = server_socket.recvfrom(1024)

            print("\nReceived From ", addr)
            print(data.decode())

def main():
    my_server(MY_HOST, MY_PORT)

if __name__ == "__main__":
    main()
