import socket
import json
import uuid
import time
# TODO:
# 1. GOSSIP
    # - gossip to 3 random peers
# 2. Consensus
# 3. Create Chain
# 4. Add Block

# echo '{"type": "GOSSIP", "host": "130.179.28.110", "port": 8999, "id": 1, "name": "Hello World!",}' | nc -u 130.179.28.37 8999

MY_PORT = 8759
SILICON_HOST, SILICON_PORT = "silicon.cs.umanitoba.ca", 8999
EAGLE_HOST, EAGLE_PORT = "eagle.cs.umanitoba.ca", 8999
ROBIN_HOST, ROBIN_PORT = "robin.cs.umanitoba.ca", 8999
MY_PEER_ID = str(uuid.uuid4())
TIMEOUT = 60

class Peer:
    def __init__(self, peer_host = None, peer_port = None, peer_name = None, peer_id = None):
        self.peer_host = peer_host
        self.peer_port = peer_port
        self.peer_name = peer_name
        self.peer_id = peer_id
        self.timeout = time.time() + TIMEOUT

    def to_json(self):
        return {
            "peer_host": self.peer_host,
            "peer_port": self.peer_port,
            "peer_name": self.peer_name,
            "peer_id": self.peer_id,
            "timeout": self.timeout,
        }
    
    def __str__(self):
        return str(self.to_json())
    
peer_obj_list = []

def renew_timeout_peer(peer_id, peer_list):
    renew_peer:Peer = get_peer(peer_id, peer_list)
    if renew_peer != None:
        print(f"RENEW TIMEOUT PEER with peer id: {renew_peer.peer_name}")
        renew_peer.timeout = time.time() + TIMEOUT

def get_peer(peer_id, list):
    for peer in list:
        # print(f"PEER_ID {peer_id} and peer.peer_id {peer.peer_id}")
        if str(peer.peer_id) == str(peer_id):
            return peer
    
    return None

def remove_peer(peer_list, time):
    for peer in peer_list:
        if check_timeout(peer, time):
            print("REMOVING PEER")
            peer_list.remove(peer)

def check_timeout(curr_peer:Peer, time):
    # if current time > timeout time timeout has passed
    if time > curr_peer.timeout:
        return True
    else:
        return False

def print_peers():
    print("CURRENT PEERS IN THE LIST:")
    for peer in peer_obj_list:
        if peer != None:
            print(peer)

# check if peer inside list
def is_peer_list(gossip_message):
    gossip_id = gossip_message["id"]
    for peer in peer_obj_list:
        if peer.peer_id == gossip_id:
            return True #true if duplicate
        
    #false if doesn't exist
    return False 

def send_gossip_reply(my_host, known_socket, gossip_message):
    gossip_reply = {
        "type": "GOSSIP_REPLY",
        "host": my_host,
        "port": MY_PORT,
        "name": "jepz"
    }

    host_original = gossip_message["host"]
    port_original = gossip_message["port"]
    known_socket.sendto(json.dumps(gossip_reply).encode(), (host_original,port_original))

def add_peer_list(gossip_message):
    # add peer to list
    if not is_peer_list(gossip_message):
        peer_object = Peer(gossip_message["host"], gossip_message["port"], gossip_message["name"], gossip_message["id"])
        peer_obj_list.append(peer_object)

def announce_network(my_host, my_port, known_socket, known_host, known_port):
    gossip_message = {
        "type": "GOSSIP",
        "host": my_host,
        "port": my_port,
        "id": MY_PEER_ID,
        "name": "jepz",
    }

    known_socket.sendto(json.dumps(gossip_message).encode(), (known_host, known_port))

def gossip(my_host, my_port, known_socket, known_host, known_port):
    # TODO:
    # 1. connect to one well-known host
    announce_network(my_host, my_port, known_socket, known_host, known_port)
    # 2. Reply gossip message received
    print()

def handle_response(my_host, known_socket, json_response):
    msg_type = json_response["type"]
    if msg_type == "GOSSIP":
        print(json_response)
        print(f"CURRENT TIME: {time.time()}")
        #handle peers -> renew peer timeout or remove peer
        peer_id = json_response["id"]
        renew_timeout_peer(peer_id, peer_obj_list)
        remove_peer(peer_obj_list, time.time())
        #add peer to list if not exist in peer list
        add_peer_list(json_response)
        #send back gossip reply
        send_gossip_reply(my_host, known_socket, json_response)
        print(print_peers())
    elif msg_type == "GOSSIP_REPLY":
        print("handle reply here")
    

def ping_gossip(my_host, my_port, known_socket, elapsed_time):
    duration = 20
    # gossip to 3 different well-known hosts 
    if elapsed_time >= duration:
        gossip(my_host, my_port, known_socket, SILICON_HOST, SILICON_PORT)
        gossip(my_host, my_port, known_socket, EAGLE_HOST, EAGLE_PORT)
        gossip(my_host, my_port, known_socket, ROBIN_HOST, ROBIN_PORT)
        return True

def my_server(my_host, my_port):
    known_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        
        server_socket.bind((my_host, my_port))

        print(f"Server listening on host {my_host} and PORT {my_port}")

        #init gossip
        ping_gossip(my_host, my_port, known_socket, 100)
        start_time = time.time()

        while True:
            try:
                current_time = time.time()
                elapsed_time = current_time - start_time
                print(f"ELAPSE:{elapsed_time}")
                ping = ping_gossip(my_host, my_port, known_socket, elapsed_time)
                if ping:
                    print("PING GOSSIP 30 SEC")
                    start_time = time.time()

                data, addr = server_socket.recvfrom(1024)
                json_data = json.loads(data)
                print("\nReceived From ", addr)

                handle_response(my_host, known_socket, json_data)
            
            except TypeError as e:
                print(f"Type Error: {e}")


def main():
    hostname = socket.gethostname()
    # Get the IP address associated with the local hostname
    local_ip = socket.gethostbyname(hostname)
    my_server(local_ip, MY_PORT)

if __name__ == "__main__":
    main()
