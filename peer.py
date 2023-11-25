import socket
import json
import uuid
import time
import random
from collections import Counter

# TODO:
# 1. GOSSIP (done)
# 2. Consensus (done)
# 3. Create Chain
# 4. Add Block

# echo '{"type": "GOSSIP", "host": "130.179.28.110", "port": 8999, "id": 1, "name": "Hello World!",}' | nc -u 130.179.28.37 8999

MY_PORT = 8759
SILICON_HOST, SILICON_PORT = "silicon.cs.umanitoba.ca", 8999
TIMEOUT = 60
GOSSIP_REPEAT_DURATION = 20
CONSENSUS_DURATION = 10

class Peer:
    def __init__(self, peer_host = None, peer_port = None, peer_name = None, peer_id = None, sock = socket):
        self.peer_host = peer_host
        self.peer_port = peer_port
        self.peer_name = peer_name
        self.peer_id = peer_id
        self.timeout = time.time() + TIMEOUT
        self.sent_messages = []
        self.sock = sock
        
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
            "name": "duolingo",
        }

        self.sock.sendto(json.dumps(gossip_message).encode(), (self.peer_host, self.peer_port))

    def forward_gossip_peer(self, message):
        if message not in self.sent_messages:
            # print(f"FORWARDING MESSAGE {message} to {self.peer_name} {self.peer_id}")
            self.sock.sendto(json.dumps(message).encode(), (self.peer_host, self.peer_port))
            self.sent_messages.append(message)

    def send_stat(self):
        print(f"SENDING STAT MSG TO {self.peer_name, self.peer_host, self.peer_port}")
        stat_msg = {"type":"STATS"}
        self.sock.sendto(json.dumps(stat_msg).encode(), (self.peer_host, self.peer_port))

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
        "name": "duolingo"
    }

    host_original = gossip_message["host"]
    port_original = gossip_message["port"]
    server_socket.sendto(json.dumps(gossip_reply).encode(), (host_original,port_original))

def add_peer_list(my_host, my_port, gossip_message, sock):
    # add peer to list if not in list and not myself
    if not is_peer_list(gossip_message) and not is_peer_myself(gossip_message, my_host, my_port):
        peer_object = Peer(gossip_message["host"], gossip_message["port"], gossip_message["name"], gossip_message["id"], sock)
        peer_obj_list.append(peer_object)

def foward_messages(gossip_message, my_host):
    for peer in peer_obj_list:
        #ignore own messages
        if not is_peer_myself(gossip_message, my_host, MY_PORT):
            peer.forward_gossip_peer(gossip_message)

def do_gossip(my_host, server_socket, json_response):
    print("INSIDE GOSSIP")
    #handle peers -> renew peer timeout or remove peer
    print(f"CURRENT TIME: {time.time()}")
    peer_id = json_response["id"]
    renew_timeout_peer(peer_id, peer_obj_list)
    remove_peer(peer_obj_list, time.time())

    #add peer to list if not exist in peer list
    add_peer_list(my_host, MY_PORT, json_response, server_socket)

    #send back gossip reply
    send_gossip_reply(my_host, server_socket, json_response)

    #send gossip message to all peers exactly once
    foward_messages(json_response, my_host)
    # print(print_peers())

def ping_gossip(my_host, my_port, elapsed_time):
    # gossip to 3 different random hosts from list
    if elapsed_time >= GOSSIP_REPEAT_DURATION:
        random_hosts = random.sample(peer_obj_list, 3)
        # print(f"GOSSIPING TO: {random_hosts}")
        for host in random_hosts:
            host.gossip(my_host, my_port)
        return True

def send_stats():
    print("INSIDE STATS")
    # send STATs to all peers at once
    for peer in peer_obj_list:
        peer.send_stat()
    print("FINISHED SENDING STATS")

def save_stats_reply(addr, json_response, stats_replies):
    json_response["host"] = addr[0]
    json_response["port"] = addr[1]
    stats_replies.append(json_response)

def do_consensus(stats_replies):
    '''
    do consensus. Return lists with the max height
    '''
    print("DOING CONSENSUS")
    
    consensus_list = get_consensus_list(stats_replies)

    for list in consensus_list:
        print(f"{list} \n")

def get_consensus_list(stats_replies):
    return find_majority_hash(find_max_height(stats_replies))

def find_max_height(stats_replies):
    # Find the maximum height
    max_height = max(entry['height'] for entry in stats_replies)
    return [entry for entry in stats_replies if entry['height'] == max_height]

def find_majority_hash(stats_replies):
    hash_counts = {}
    for entry in stats_replies:
        current_hash = entry['hash']
        hash_counts[current_hash] = hash_counts.get(current_hash, 0) + 1

    # Find the majority hash
    majority_hash = max(hash_counts, key=hash_counts.get)

    # Filter entries with the majority hash
    entries_with_majority_hash = [entry for entry in stats_replies if entry['hash'] == majority_hash]
    return entries_with_majority_hash
    
def handle_response(my_host, server_socket, json_response):
    msg_type = json_response["type"]
    if msg_type == "GOSSIP":
        do_gossip(my_host, server_socket, json_response)

def handle_consensus(my_host, server_socket, json_response):
    finish_consensus_time = time.time() + CONSENSUS_DURATION
    # send stats to all peers at once
    send_stats()
    stats_replies = []
    #timeout, doing consensus currently
    while time.time() <= finish_consensus_time:
        #get the data
        print("RECEIVING REPLIES STATS")
        data, addr = server_socket.recvfrom(1024)
        json_response = json.loads(data)
        print(f"\nReceived From {addr}, \ndata: {json_response}")
        msg_type = json_response["type"]

        # save stats_reply
        if msg_type == "STATS_REPLY":
            save_stats_reply(addr, json_response, stats_replies)
            print("STATS REPLY: ")
            for stat in stats_replies:
                print(f"{stat} \n")
        #handle other requests, but dont handle other consensus
        elif msg_type != "STATS_REPLY" and msg_type != "CONSENSUS": 
            handle_response(my_host, server_socket, json_response)
        else:
            print("CANT HANDLE OTHER CONSENSUS")
    
    #after getting all stats reply, do consensus
    do_consensus(stats_replies)

def my_server(my_host, my_port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        
        server_socket.bind((my_host, my_port))

        print(f"Server listening on host {my_host} and PORT {my_port}")

        #init gossip to well known host
        init_peer = Peer(SILICON_HOST, SILICON_PORT, None, None, server_socket)
        init_peer.gossip(my_host, my_port)
        start_time = time.time()

        #init consensus, false because can't do consensus initially
        is_consensus = False
        while True:
            try:
                #ping gossip every 30 secs
                current_time = time.time()
                elapsed_time = current_time - start_time
                print(f"ELAPSE:{elapsed_time}")
                ping = ping_gossip(my_host, my_port, elapsed_time)
                if ping:
                    print("PING GOSSIP 30 SEC")
                    start_time = time.time()

                #get the data
                data, addr = server_socket.recvfrom(1024)
                json_response = json.loads(data)
                print(f"\nReceived From {addr}, \ndata: {json_response}")
                msg_type = json_response["type"]

                #handle consensus
                if msg_type == "CONSENSUS" and not is_consensus:
                    #starting consensus
                    is_consensus = True
                    handle_consensus(my_host, server_socket, json_response)
                    print("ENDING REPLIES STATS")
                    # finished consensus
                    is_consensus = False
                else: #handle any other response
                    handle_response(my_host, server_socket, json_response)
                    
                
            except TypeError as e:
                print(f"Type Error: {e}")


def main():
    hostname = socket.gethostname()
    # Get the IP address associated with the local hostname
    local_ip = socket.gethostbyname(hostname)
    my_server(local_ip, MY_PORT)

if __name__ == "__main__":
    main()
