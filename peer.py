import socket
import json
import uuid
import time
import random
# TODO:
# 1. GOSSIP (done)
# 2. Consensus
# 3. Create Chain
# 4. Add Block

# echo '{"type": "GOSSIP", "host": "130.179.28.110", "port": 8999, "id": 1, "name": "Hello World!",}' | nc -u 130.179.28.37 8999

MY_PORT = 8759
SILICON_HOST, SILICON_PORT = "silicon.cs.umanitoba.ca", 8999
TIMEOUT = 60
GOSSIP_REPEAT_DURATION = 20

class Peer:
    def __init__(self, peer_host = None, peer_port = None, peer_name = None, peer_id = None):
        self.peer_host = peer_host
        self.peer_port = peer_port
        self.peer_name = peer_name
        self.peer_id = peer_id
        self.timeout = time.time() + TIMEOUT
        self.sent_messages = []
        self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM)
        
    def to_json(self):
        return {
            "peer_host": self.peer_host,
            "peer_port": self.peer_port,
            "peer_name": self.peer_name,
            "peer_id": self.peer_id,
            "timeout": self.timeout,
        }
    
    def gossip(self, my_host, my_port):
        gossip_message = {
            "type": "GOSSIP",
            "host": my_host,
            "port": my_port,
            "id": str(uuid.uuid4()),
            "name": "jepz",
        }

        self.sock.sendto(json.dumps(gossip_message).encode(), (self.peer_host, self.peer_port))

    def forward_gossip_peer(self, message):
        if message not in self.sent_messages:
            print(f"FORWARDING MESSAGE {message} to {self.peer_name} {self.peer_id}")
            self.sock.sendto(json.dumps(message).encode(), (self.peer_host, self.peer_port))
            self.sent_messages.append(message)
        else:
            print("SENT MESSAGE DETECTED, ABORTING FORWARD MESSAGE")


    def __str__(self):
        return str(self.to_json())
    
peer_obj_list:Peer = []

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

def is_peer_myself(gossip_message, my_host, my_port):
    gossip_host = gossip_message["host"]
    gossip_port = gossip_message["port"]

    if gossip_host == my_host and gossip_port == my_port:
        return True
    else:
        return False

def send_gossip_reply(my_host, server_socket, gossip_message):
    gossip_reply = {
        "type": "GOSSIP_REPLY",
        "host": my_host,
        "port": MY_PORT,
        "name": "jepz"
    }

    host_original = gossip_message["host"]
    port_original = gossip_message["port"]
    server_socket.sendto(json.dumps(gossip_reply).encode(), (host_original,port_original))

def add_peer_list(my_host, my_port, gossip_message):
    # add peer to list if not in list and not myself
    if not is_peer_list(gossip_message) and not is_peer_myself(gossip_message, my_host, my_port):
        peer_object = Peer(gossip_message["host"], gossip_message["port"], gossip_message["name"], gossip_message["id"])
        peer_obj_list.append(peer_object)

def foward_messages(gossip_message, my_host):
    for peer in peer_obj_list:
        #ignore own messages
        if not is_peer_myself(gossip_message, my_host, MY_PORT):
            peer.forward_gossip_peer(gossip_message)

def handle_response(my_host, server_socket, json_response):
    msg_type = json_response["type"]
    if msg_type == "GOSSIP":
        print(json_response)
        print(f"CURRENT TIME: {time.time()}")
        #handle peers -> renew peer timeout or remove peer
        peer_id = json_response["id"]
        renew_timeout_peer(peer_id, peer_obj_list)
        remove_peer(peer_obj_list, time.time())
        #add peer to list if not exist in peer list
        add_peer_list(my_host, MY_PORT, json_response)
        #send back gossip reply
        send_gossip_reply(my_host, server_socket, json_response)
        #send gossip message to all peers exactly once
        foward_messages(json_response, my_host)
        print(print_peers())
    
def ping_gossip(my_host, my_port, elapsed_time):
    # gossip to 3 different random hosts from list
    if elapsed_time >= GOSSIP_REPEAT_DURATION:
        random_hosts = random.sample(peer_obj_list, 3)
        print(f"GOSSIPING TO: {random_hosts}")
        for host in random_hosts:
            host.gossip(my_host, my_port)
        return True

def my_server(my_host, my_port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        
        server_socket.bind((my_host, my_port))

        print(f"Server listening on host {my_host} and PORT {my_port}")

        #init gossip to well known host
        init_peer = Peer(SILICON_HOST, SILICON_PORT, None, None)
        init_peer.gossip(my_host, my_port)
        start_time = time.time()

        while True:
            try:
                current_time = time.time()
                elapsed_time = current_time - start_time
                print(f"ELAPSE:{elapsed_time}")
                ping = ping_gossip(my_host, my_port, elapsed_time)
                if ping:
                    print("PING GOSSIP 30 SEC")
                    start_time = time.time()

                data, addr = server_socket.recvfrom(1024)
                json_data = json.loads(data)
                print("\nReceived From ", addr)

                handle_response(my_host, server_socket, json_data)
            
            except TypeError as e:
                print(f"Type Error: {e}")


def main():
    hostname = socket.gethostname()
    # Get the IP address associated with the local hostname
    local_ip = socket.gethostbyname(hostname)
    my_server(local_ip, MY_PORT)

if __name__ == "__main__":
    main()
