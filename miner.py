import argparse
import socket
import json
import sys
import time
import peer
import select
import random

max_block = None
DIFFICULTY = 8

class Miner:
    def __init__(self, miner_host = None, miner_port = None):
        self.miner_host = miner_host
        self.miner_port = miner_port
        self.is_mining = False

    def req_newword_miner(self, json_response):
        # send new word request to miner
        print(f"\nSENDING MESSAGE TO WORKER PORT: {self.miner_port}, \nMESSAGE SEND: {json_response}\n")
        request_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        request_socket.connect((self.miner_host, self.miner_port))
        request_socket.send(json.dumps(json_response).encode())

        return request_socket

    def __str__(self) -> str:
        return f"Miner host: {self.miner_host}, miner port: {self.miner_port}"
    
def miners_to_object(miner_input):
    host,port = miner_input
    return Miner(host, port)

def insert_miner(miner_inputs, miner_list):
    for miner_input in miner_inputs:
        miner_list.append(miners_to_object(miner_input))

def handle_newword(json_response, difficulty, client_connect, server_socket):
    new_word = json_response["word"]
    nonce_start = str(int(json_response["nonce_start"]))
    block_mined, new_connect = mine_block(max_block, new_word, difficulty, server_socket, nonce_start)
    block_mined["type"] = "ANNOUNCE"
    if new_connect is None:
        print("client connect")
        client_connect.send(json.dumps(block_mined).encode())
    else:
        print("new connect")
        new_connect.send(json.dumps(block_mined).encode())
    
def handle_maxblock(json_response):
    global max_block
    del json_response["type"]
    max_block = json_response

def make_newblock(previous_block, messages, nonce_start):
    message_list = []
    message_list.append(messages)
    new_block = {
        "height" : previous_block["height"] + 1,
        "messages": message_list,
        "minedBy": "Bowser Jr.",
        "timestamp": int(time.time())
    }
    new_block['hash'] = previous_block['hash']

    nonce = 499999999999999969854583185801664424805
    new_block['nonce'] = nonce
    return new_block

def mine_block(previous_block, messages, difficulty, server_socket, nonce_start):
    new_block = make_newblock(previous_block, messages, nonce_start)

    nonce_found = False
    client_connect = None
    nonce = new_block['nonce']
    while not nonce_found:
        # Check if the client socket is readable
        ready_to_read, _, _ = select.select([server_socket], [], [], 0)
        
        if ready_to_read:
            # Receive data if available
            try:
                client_conn, client_addr = server_socket.accept()
                print("\nConnected by", client_addr)
                json_response = json.loads(client_conn.recv(1024).decode())
                print(json_response)
                if json_response["type"] == "MAX_BLOCK":
                    handle_maxblock(json_response)
                    new_block = make_newblock(max_block, messages, nonce_start)
                    nonce = new_block['nonce']
                    client_connect = client_conn
                    print(client_addr)
                    time.sleep(2)
                # Handle json_response if needed
            except json.JSONDecodeError:
                # Handle JSON decoding error
                pass
        nonce = str(int(nonce) + 1)
        new_block['nonce'] = nonce
        hashBase = peer.get_block_hash(new_block, previous_block)
        print(f"nonce: {nonce}")
        print(f"mining height: {new_block['height']}")
        print(f"hashBase: {hashBase}")
        if hashBase[-1 * difficulty:] == '0' * difficulty:
            new_block["hash"] = hashBase
            nonce_found = True

    
    new_block['type'] = "ANNOUNCE"
    print(f"NEW BLOCK FOUND: {new_block}")
    return new_block, client_connect
    

def socket_con_nothread(host, port_num):
    # create TCP stream
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port_num))
        server_socket.listen(0)
        print(f"Miner listening on host {host} and port {port_num}")
        while True:
            try:
                client_connect, addr = server_socket.accept()
                print("Connected by", addr)

                json_response = json.loads(client_connect.recv(1024).decode())
                print(f"Received: {json_response}\n")
                
                msg_type = json_response["type"]
                if msg_type == "MAX_BLOCK":
                    handle_maxblock(json_response)
                elif msg_type == "NEW_WORD":
                    handle_newword(json_response, DIFFICULTY, client_connect, server_socket)                        

                client_connect.close()

            except KeyboardInterrupt as key:
                print("Program Stopped. Interrupted by keyboard.")
                sys.exit()



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("host", type=str, help="Worker's host")
    parser.add_argument("port", type=int, help="Worker's port")

    args = parser.parse_args()
    socket_con_nothread(args.host, args.port)


if __name__ == "__main__":
    main()