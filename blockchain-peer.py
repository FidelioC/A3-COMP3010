import socket
import json
import uuid

# TODO:
# 1. GOSSIP
# 2. Consensus
# 3. Create Chain
# 4. Add Block

SILICON_HOST, SILICON_PORT = "130.179.28.37", 8999


def announce_gossip(gossip_conn):
    gossip_message = {
        "type": "GOSSIP",
        "host": "192.168.0.27",
        "port": 8999,
        "id": str(uuid.uuid4()),
        "name": "Hello World!",
    }
    gossip_conn.send(json.dumps(gossip_message).encode())
    return gossip_conn.recv(4096)


def gossip(host, port):
    # TODO:
    # 1. connect to one well-known host
    gossip_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    gossip_conn.connect((host, port))
    print(announce_gossip(gossip_conn))
    # 2. Reply gossip message received
    print()


def main():
    gossip(SILICON_HOST, SILICON_PORT)
    print("TODO here")


if __name__ == "__main__":
    main()
