import socket
import json
import uuid
import time
import random
import hashlib
import argparse
import sys





SILICON_HOST, SILICON_PORT = "silicon.cs.umanitoba.ca", 8999
TIMEOUT = 60
GOSSIP_REPEAT_DURATION = 20
CONSENSUS_REPEAT_DURATION = 60
CONSENSUS_DURATION = 1
GETBLOCK_DURATION = 1
ALLBLOCKS_DURATION = 10
DIFFICULTY = 8

SOCKET_TIMEOUT = 10

consensus_peers = []
my_chain = []
my_chain_valid = []
chain_valid = False
blacklisted_peers = []

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
            "name": "Bowser Jr.",
        }

        self.sock.sendto(json.dumps(gossip_message).encode(), (self.peer_host, self.peer_port))

    def forward_gossip_peer(self, message):
        '''
        FORWARDING MESSAGE EXACTLY ONCE, 
        BY KEEPING TRACK OF THE SENT MESSAGES
        '''
        if message not in self.sent_messages:
            # print(f"FORWARDING MESSAGE {message} to {self.peer_name} {self.peer_id}")
            self.sock.sendto(json.dumps(message).encode(), (self.peer_host, self.peer_port))
            self.sent_messages.append(message)

    def send_stat(self):
        print(f"SENDING STAT MSG TO {self.peer_name, self.peer_host, self.peer_port}")
        stat_msg = {"type":"STATS"}
        self.sock.sendto(json.dumps(stat_msg).encode(), (self.peer_host, self.peer_port))

    def send_getblock(self, block_height):
        get_block_msg = {"type": "GET_BLOCK", "height": block_height}
        print(f"SENDING GET_BLOCK MSG: {get_block_msg} TO {self.peer_name, self.peer_host, self.peer_port}")

        self.sock.sendto(json.dumps(get_block_msg).encode(), (self.peer_host, self.peer_port))

    def __str__(self):
        return str(self.to_json())
    
peer_obj_list:Peer = []

def to_blacklist(addr, blacklisted_list):
    if addr not in blacklisted_list:
        blacklisted_list.append(addr)

def block_format(json_response):
    block = {
        "hash": json_response["hash"],
        "height": json_response["height"],
        "messages": json_response["messages"],
        "minedBy": json_response["minedBy"],
        "nonce": json_response["nonce"],
        "timestamp": json_response["timestamp"]
    }
    return block

def print_list(my_list):
    for entry in my_list:
        if entry != None:
            print(entry)

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

def get_peer_by_addr(peer_host, peer_port):
    for peer in peer_obj_list:
        if peer.peer_host == peer_host and peer.peer_port == peer_port:
            return peer
    
    return None

# ============ README: CLEAN PEERS CODE =====================
def renew_timeout_peer(peer_id, peer_list):
    renew_peer:Peer = get_peer(peer_id, peer_list)
    if renew_peer != None:
        # print(f"RENEW TIMEOUT PEER with peer id: {renew_peer.peer_name}")
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
#==============================================================

#=========================README: GOSSIPING CODE HERE =======================
def send_gossip_reply(my_host, my_port, server_socket, gossip_message):
    '''
    SENDING GOSSIP REPLY TO OTHER PEER
    '''
    gossip_reply = {
        "type": "GOSSIP_REPLY",
        "host": my_host,
        "port": my_port,
        "name": "Bowser Jr."
    }

    host_original = gossip_message["host"]
    port_original = gossip_message["port"]
    server_socket.sendto(json.dumps(gossip_reply).encode(), (host_original,port_original))

def add_peer_list(my_host, my_port, gossip_message, sock):
    # add peer to list if not in list and not myself
    if not is_peer_list(gossip_message) and not is_peer_myself(gossip_message, my_host, my_port):
        exist_peer = get_peer_by_addr(gossip_message["host"], gossip_message["port"])
        # don't want to have two same peers with different id
        if exist_peer:
            peer_obj_list.remove(exist_peer)
        
        peer_object = Peer(gossip_message["host"], gossip_message["port"], gossip_message["name"], gossip_message["id"], sock)
        peer_obj_list.append(peer_object)

def foward_messages(gossip_message, my_host, my_port):
    '''
    FORWARDING MESSAGES TO ALL PEERS
    '''
    for peer in peer_obj_list:
        #ignore own messages
        if not is_peer_myself(gossip_message, my_host, my_port):
            peer.forward_gossip_peer(gossip_message)

def do_gossip(my_host, my_port, server_socket, json_response):
    # print("INSIDE GOSSIP")
    # print(f"CURRENT TIME: {time.time()}")
    peer_id = json_response["id"]

    ''' README: handle peers -> renew peer timeout or remove peer '''
    renew_timeout_peer(peer_id, peer_obj_list)
    remove_peer(peer_obj_list, time.time())

    #add peer to list if not exist in peer list
    add_peer_list(my_host, my_port, json_response, server_socket)

    #send back gossip reply
    send_gossip_reply(my_host, my_port, server_socket, json_response)

    #send gossip message to all peers exactly once
    foward_messages(json_response, my_host, my_port)
    # print(print_peers())

def ping_gossip(my_host, my_port, elapsed_time):
    '''
    PING GOSSIP, 'keep-alive'
    '''
    # gossip to 3 different random hosts from list
    if elapsed_time >= GOSSIP_REPEAT_DURATION and len(peer_obj_list) > 2:
        random_hosts = random.sample(peer_obj_list, 2)
        # print(f"GOSSIPING TO: {random_hosts}")
        for host in random_hosts:
            host.gossip(my_host, my_port)
        return True


#==============================================================

#=======================README: COLLECT ALL BLOCKS CODE ===========================

def send_stats():
    # print("INSIDE STATS")
    # send STATs to all peers at once
    for peer in peer_obj_list:
        peer.send_stat()
    # print("FINISHED SENDING STATS")

def save_stats_reply(addr, json_response, stats_replies):
    json_response["host"] = addr[0]
    json_response["port"] = addr[1]
    stats_replies.append(json_response)

def do_getallblocks(my_host, my_port, server_socket, consensus_list):
    '''
    get block from peers in a load balance way
    using round robin
    '''
    # try:
    # see if there's any timeout, peer. Don't request from them if yes.
    remove_peer(peer_obj_list, time.time())

    if consensus_list != None and len(consensus_list) > 0:
        curr_height = 0
        max_height = consensus_list[0]["height"]
        print(f"DO GETTING ALL BLOCKS FROM: {consensus_list}\n MAX HEIGHT: {max_height}")
        print_list(peer_obj_list)
        # load balance get block request
        while(curr_height < max_height):
            for peer in consensus_list:
                peer_obj = get_peer_by_addr(peer["host"], peer["port"])
                peer_addr = (peer["host"], peer["port"])
                if peer_obj != None and peer_addr not in blacklisted_peers:
                    peer_obj.send_getblock(curr_height)
                curr_height += 1
        
        get_blocks_timeout = time.time() + ALLBLOCKS_DURATION
        handle_getblock_reply(my_host, my_port, server_socket, get_blocks_timeout)
    
    # except TypeError as e:
    #     print(f"Type Error:. {e}")
    #     pass

def handle_getblock_reply(my_host, my_port, server_socket, get_blocks_timeout):
    '''
    we want to make timeout and see how many replies we got in an interval
    validate and resend if there's block missing
    '''
    print(f"GETTING BLOCKS TIMEOUT: {get_blocks_timeout}. \nCURRENT TIME: {time.time()}")
    if time.time() >= get_blocks_timeout:
        return
    
    finish_getblock_time = time.time() + GETBLOCK_DURATION
    while time.time() <= finish_getblock_time:
        #try getting any data during this time
        print("RECEIVING REPLY GETBLOCK")
        # print(f"CONSENSUS PEERS: {consensus_peers}")
        # for peer in consensus_peers:
        #     print(peer)
        try:
            data, addr = server_socket.recvfrom(1024)
            json_response = json.loads(data)
            print(f"\nReceived From {addr}, \ndata: {json_response}")
            msg_type = json_response["type"]
            if msg_type == "GET_BLOCK_REPLY":
                get_blocks_timeout += GETBLOCK_DURATION # give more time if still receiving get blocks
                insert_block(addr, json_response)
            else:
                # handle any other response
                handle_response(addr, my_host,my_port, server_socket, json_response)
        except json.decoder.JSONDecodeError as e:
            print(f"JSON ERROR {e}")
            # to_blacklist(addr, blacklisted_peers)
        except KeyError as e:
            print(f"Key error {e}")
        except TypeError as e:
            print(f"Type error {e}")


    print("FINISHED RECEIVING REPLY BLOCKS ")
    # print("MY CURRENT CHAIN: ")
    # for block in my_chain:
    #     print(f"{block}\n")

    # check current chain
    missing_blocks = find_missing_blocks(my_chain, consensus_peers[0]["height"])
    # request missing blocks
    check_req_blocks(my_host, my_port, server_socket, missing_blocks, get_blocks_timeout)
    
def check_req_blocks(my_host, my_port, server_socket, missing_blocks, get_blocks_timeout):
    # request missing blocks until all filled,
    # if there's missing blocks, need to handle get block reply
    if len(missing_blocks) > 0:
        print(f"MISSING BLOCKS FOUND {missing_blocks} \n WITH LENGTH: {len(missing_blocks)}")
        request_missing_blocks(missing_blocks, consensus_peers)
        handle_getblock_reply(my_host, my_port, server_socket, get_blocks_timeout)
    # AFTER GETTING ALL BLOCKS, VALIDATE CHAIN
    else:
        print(f"VALIDATING CHAIN")
        print("MY CURRENT CHAIN: ")
        for block in my_chain:
            print(f"{block}\n")
        global chain_valid
        chain_valid = validate_chain(my_chain)
        print(f"FINISHED VALIDATING CHAIN WITH RESULT: {chain_valid}")
        if chain_valid:
            global chain_updated
            chain_updated = True
            return True
        else:
            return False
    # print(f"CHAIN VALIDATION {chain_valid}")

def insert_block(addr, get_block_reply):
    '''
    INSERT BLOCKS TO MY CHAIN
    '''
    print(f"INSERTING BLOCKS {get_block_reply}")
    block_height = get_block_reply["height"]

    if block_height != 'None' or block_height != None:
        existing_block = next((block for block in my_chain if block["height"] == block_height and block["hash"] == get_block_reply["hash"]), None)

        # find index to insert block
        if existing_block is None:
            index = 0
            while index < len(my_chain) and my_chain[index]["height"] < block_height:
                index += 1

            new_block = block_format(get_block_reply)
            new_block["addr"] = addr
            #insert block
            my_chain.insert(index, new_block)
    else:
        to_blacklist(addr, blacklisted_peers)

def find_missing_blocks(current_chain, target_height):
    '''
    FINDING MISSING BLOCKS WITH THE TARGETED HEIGHT
    '''
    missing_blocks = []
    for i in range(len(current_chain) - 1):
        current_element = current_chain[i]["height"]
        next_element = current_chain[i + 1]["height"]

        # Check if there is a gap between current_element and next_element
        if next_element - current_element > 1:
            # Insert missing block into the result list
            for block in range(current_element + 1, next_element):
                missing_blocks.append(block)
    
    # print(current_chain[len(current_chain) - 1])
    if len(current_chain) > 0:
        max_height = current_chain[len(current_chain) - 1]["height"]
        # print(max_height)
        if max_height < target_height:
            for i in range(max_height+1, target_height):
                missing_blocks.append(i)

    return missing_blocks

def request_missing_blocks(missing_blocks, consensus_list):
    '''
    get missing blocks from peers in a load balance way
    '''
    total_missing = len(missing_blocks)
    # if there's missing blocks
    if total_missing > 0:
        random.shuffle(consensus_list)
        curr_index = 0
        # load balance get block request
        while(curr_index < total_missing):
            for peer in consensus_list:
                if curr_index < total_missing:
                    peer_obj = get_peer_by_addr(peer["host"], peer["port"])
                    if peer_obj != None:
                        peer_obj.send_getblock(missing_blocks[curr_index])
                    curr_index += 1 
    
# ======================= README: VALIDATING/VERIFY CHAIN CODE ===================================
def validate_chain(current_chain):
    '''
    chain validation here.
    1. Messages have a maximum length of 20 characters (keeps us under MTU)
    2. Blocks have a maximum of 10 messages in them.
    3. A nonce is a string (really, bytes) and must be less than 40 characters
    4. Every block has the correct hash
    5. And the hash has the correct difficulty
    '''
    is_validated = True
    for i in range(len(current_chain)):
        current_block = current_chain[i]
        if i == 0:
            is_validated &= validate_block(current_block, None) #genesis block
        else:
            prev_block = current_chain[i-1]
            is_validated &= validate_block(current_block, prev_block)
    return is_validated

def validate_block_messages(block_messages):
    if len(block_messages) > 10:
        return False
    
    for message in block_messages:
        if len(message) > 20:
            return False
    
    return True

def validate_block_nonce(block_nonce):
    if len(block_nonce) > 40:
        return False
    
    return True

def get_block_hash(current_block, prev_block):
    block_messages = current_block["messages"]
    block_minedby = current_block["minedBy"]
    block_nonce = current_block["nonce"]
    block_time = current_block["timestamp"]
    # get block hash
    hashBase = hashlib.sha256()

    # prev hash
    if prev_block != None: #ignore if genesis
        if prev_block['hash'] != None:
            hashBase.update(prev_block['hash'].encode()) 
    # mined by 
    if block_minedby != None:
        hashBase.update(block_minedby.encode()) 

    # messages
    if block_messages != None:
        for message in block_messages: 
            if message != None:
                hashBase.update(message.encode())
    # time
    if block_time != None:
        hashBase.update(block_time.to_bytes(8,'big'))
    if block_nonce != None:
        # nonce
        hashBase.update(str(block_nonce).encode())
   
    # print(f"generated hash {hashBase.hexdigest()}")
    # print(f"current hash {current_block['hash']}")

    return hashBase.hexdigest()

def validate_block(current_block, prev_block):
    print(f"VALIDATING BLOCK {current_block}")
    block_hash = current_block["hash"]
    block_messages = current_block["messages"]
    block_nonce = current_block["nonce"]

    if "addr" in current_block:
        block_addr = current_block["addr"]

    hashBase = get_block_hash(current_block, prev_block)

    #validate all requirements
    if (hashBase == current_block["hash"] 
        and validate_block_nonce(block_nonce) 
        and validate_block_messages(block_messages)
        and block_hash[-1 * DIFFICULTY:] == '0' * DIFFICULTY):
        # print(f"BLOCK IS VALID {current_block}")
        return True
    else:
        print(f"BLOCK IS INVALID")
        if "addr" in current_block:
            # blacklist bad peer
            to_blacklist(block_addr, blacklisted_peers)
        return False
# =================================================================

# =================== README: CONSENSUS CODE =======================
def check_reply_mychain(consensus_list):
    '''
    check if my chain is still in sync with others chain
    '''
    # try:
    if consensus_list != None:
        if len(consensus_list) > 0 and len(my_chain) > 0:
            if (consensus_list[0]["height"] == len(my_chain) 
                and consensus_list[0]["hash"] == my_chain[len(my_chain)-1]["hash"]):
                return True
            else:
                return False

    # except TypeError as e:
    #     print(f"Type Error:. {e}")
    #     pass

def get_consensus_list(stats_replies):
    '''
    RETURNING THE MOST AGREED CHAIN PEER LISTS
    '''
    return find_majority_hash(find_max_height(stats_replies))

def find_max_height(stats_replies):
    '''
    FINDING THE MAXIMUM HEIGHT FROM ALL TRACKED PEERS
    '''
    # Find the maximum height
    try:
        valid_entries = [entry for entry in stats_replies if entry['height'] is not None 
                         and entry['height'] != 'null'
                         and entry ['height'] != 'None']

        if len(valid_entries) > 0:
            max_height = max(int(entry['height']) for entry in valid_entries)
            return [entry for entry in valid_entries if entry['height'] == max_height]
    except TypeError as e:
        print(f"Type Error:. {e}")
        # sys.exit()

def find_majority_hash(stats_replies):
    '''
    FINDING THE MAJORITY HASH FROM ALL TRACKED PEERS
    '''
    hash_counts = {}
    try:
        if stats_replies != None:
            for entry in stats_replies:
                current_hash = entry['hash']
                hash_counts[current_hash] = hash_counts.get(current_hash, 0) + 1
            # Find the majority hash
            majority_hash = max(hash_counts, key=hash_counts.get)
            # Filter entries with the majority hash
            entries_with_majority_hash = [entry for entry in stats_replies if entry['hash'] == majority_hash]
            return entries_with_majority_hash
    except TypeError as e:
        print(f"Type Error:. {e}")
        # sys.exit()

def handle_consensus(my_host, my_port, server_socket, json_response):
    '''
    README: DOING CONSENSUS HERE
    '''
    finish_consensus_time = time.time() + CONSENSUS_DURATION
    # send stats to all peers at once
    send_stats()
    stats_replies = []
    #timeout, doing consensus currently
    while time.time() <= finish_consensus_time:
        try:
            #get the data
            print("RECEIVING REPLIES STATS")
            
            data, addr = server_socket.recvfrom(1024)
            json_response = json.loads(data)
            print(f"\nReceived From {addr}, \ndata: {json_response}")
            msg_type = json_response["type"]

            # save stats_reply
            if msg_type == "STATS_REPLY" and addr not in blacklisted_peers:
                save_stats_reply(addr, json_response, stats_replies)
            #handle other requests, but dont handle other consensus
            elif msg_type != "STATS_REPLY" and msg_type != "CONSENSUS": 
                handle_response(addr, my_host, my_port, server_socket, json_response)
            else:
                print("CANT HANDLE OTHER CONSENSUS")
        except TypeError as e:
            to_blacklist(addr, blacklisted_peers)
            print(f"Type error {e}")

    
    print("FINISHED RECEIVING REPLIES STATS")
    print("STATS REPLY: ")
    for stat in stats_replies:
        print(f"{stat} \n")
    #after getting all stats reply, do consensus
    consensus_list = get_consensus_list(stats_replies)
    global consensus_peers
    consensus_peers = consensus_list
    
    # if consensus peers list is none, try doing another consensus
    print(f"CONSENSUS PEERS: {consensus_peers}")
    if consensus_peers is not None:
        for peer in consensus_peers:
            print(peer)
    else:
        return -CONSENSUS_REPEAT_DURATION

    # check with my chain whether chain is same or no,
    # no need to get all blocks if chain are the same
    global chain_valid
    if not check_reply_mychain(consensus_list):
        #get all blocks
        print("CHAIN IS DIFFERENT, GETTING ALL BLOCKS")
        chain_valid = False
        global my_chain
        my_chain = []
        do_getallblocks(my_host, my_port, server_socket, consensus_list)
        if chain_valid:
            global my_chain_valid
            my_chain_valid = my_chain
    else:
        chain_valid = True
    
    return time.time()

# =================================================================

# =================== HANDLE NORMAL RESPONSE =======================
def handle_response(addr, my_host, my_port, server_socket, json_response):
    msg_type = json_response["type"]
    if msg_type == "GOSSIP":
        do_gossip(my_host, my_port, server_socket, json_response)
    elif msg_type == "STATS" and len(my_chain_valid) > 0:
        handle_stats_reply(addr, server_socket)
    elif msg_type == "GET_BLOCK" and chain_valid:
        handle_getblock(addr, server_socket, json_response)
    elif msg_type == "ANNOUNCE" and chain_valid:
        handle_announce(json_response, my_chain)

def handle_getblock(addr, server_socket, json_response):
    height_requested = json_response["height"]
    block_reply = {}
    if height_requested in range(len(my_chain)):
        block_reply = my_chain[height_requested]
        block_reply = block_format(block_reply)
        block_reply["type"] = "GET_BLOCK_REPLY"
    else:
        block_reply = {   
            'type': 'GET_BLOCK_REPLY',
            'hash': 'None',
            'height': 'None',
            'messages': 'None',
            'minedBy': 'None',
            'nonce': 'None',
            'timestamp': 'None',
        }
    
    server_socket.sendto(json.dumps(block_reply).encode(), (addr[0], addr[1]))

def handle_announce(json_response, current_chain):
    del json_response["type"]
    new_block = json_response
    # validate block with the last block
    if len(current_chain) > 0:
        is_validated = validate_block(new_block, current_chain[len(my_chain)-1])
        if is_validated:
            current_chain.append(new_block)
            return True
        else:
            return False

def handle_stats_reply(addr, server_socket):
    stats_reply_msg = {
        "type": "STATS_REPLY",
        "height": len(my_chain_valid),
        "hash": my_chain_valid[len(my_chain_valid)-1]["hash"] 
    }
    print(f"SENDING STATS REPLY: {stats_reply_msg} TO {addr}")
    server_socket.sendto(json.dumps(stats_reply_msg).encode(), (addr[0], addr[1]))
# =================================================================

def my_server(my_host, my_port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind((my_host, my_port))
        # server_socket.settimeout(SOCKET_TIMEOUT)
        
        print(f"Server listening on host {my_host} and PORT {my_port}")

        #init gossip to well known host
        init_peer = Peer(SILICON_HOST, SILICON_PORT, None, None, server_socket)
        init_peer.gossip(my_host, my_port)
        global peer_obj_list
        start_time_gossip = time.time()

        # do consensus if possible for the 1st time
        start_time_consensus = time.time() - CONSENSUS_REPEAT_DURATION
        #init consensus, false because can't do consensus initially
        is_consensus = False

        time_offset = 0
        while True:
            try:
                '''
                HANDLE PEER SERVER 
                '''
                #ping gossip every 30 secs
                current_time = time.time()
                elapsed_time_gossip = current_time - start_time_gossip
                # print(f"ELAPSE GOSSIP:{elapsed_time_gossip}")
                ping = ping_gossip(my_host, my_port, elapsed_time_gossip)
                if ping:
                    # print("PING GOSSIP 30 SEC")
                    start_time_gossip = time.time()

                #get the data
                data, addr = server_socket.recvfrom(1024)
                json_response = json.loads(data)
                print(f"\nReceived From {addr}, \ndata: {json_response}")
                msg_type = json_response["type"]
                elapse_time_consensus = current_time - start_time_consensus - time_offset
                #handle consensus or repeat consensus every 1 min 
                # will do consensus if only have at least 3 peers
                print(f"ELAPSE CONSENSUS:{elapse_time_consensus}")
                if ((msg_type == "CONSENSUS" or elapse_time_consensus >= CONSENSUS_REPEAT_DURATION or not chain_valid)
                    and not is_consensus and len(peer_obj_list) >= 1):
                    #starting consensus
                    is_consensus = True
                    # print("STARTING CONSENSUS 1 MIN")
                    
                    start_time_consensus = handle_consensus(my_host, my_port, server_socket, json_response)
                    # finished consensus
                    is_consensus = False
                else: #handle any other response
                    handle_response(addr, my_host, my_port, server_socket, json_response)

                print(f"CHAIN VALID: {chain_valid} with length: {len(my_chain_valid)}")
                print(f"BLACKLISTED PEERS: {blacklisted_peers}\n")
                print(f"CONSENSUS PEERS: {consensus_peers}")

            except KeyError as e:
                print(f"Key error {e}")
                is_consensus = False
                to_blacklist(addr)
                pass
                
            except TypeError as e:
                print(f"Type Error:. {e}")
                is_consensus = False
                pass
            
            except json.decoder.JSONDecodeError as e:
                print(f"Json decoder error {e}")
                is_consensus = False
                pass

            except UnboundLocalError as e:
                print(f"Unbound local error {e}")
                is_consensus = False

            except ConnectionRefusedError as e:
                print(f"Connection Refused {e}")

            except KeyboardInterrupt as e:
                print(f"Program stopped. Keyboard Interrupt {e}")
                sys.exit()


def main():
    # Get the IP address associated with the local hostname
    my_host = socket.gethostbyname(socket.gethostname())

    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int)

    args = parser.parse_args()

    port = args.port

    # my_host = "192.168.101.248"
    my_server(my_host, port)

if __name__ == "__main__":
    main()
