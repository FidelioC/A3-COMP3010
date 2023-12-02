import argparse
import socket
import json
import sys
import time
import peer
import hashlib
max_block = None
DIFFICULTY = 1
COORDINATOR_HOST = "kingfisher"
COORDINATOR_PORT = 8795

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

def handle_newword(json_response, difficulty, client_connect):
    new_word = json_response["word"]
    block_mined = mine_block(max_block, new_word, difficulty)
    block_mined["type"] = "ANNOUNCE"
    client_connect.send(json.dumps(block_mined).encode())
    
def handle_maxblock(json_response):
    global max_block
    del json_response["type"]
    max_block = json_response

def mine_block(previous_block, messages, difficulty):
    new_block = {
        "height" : previous_block["height"] + 1,
        "messages": messages,
        "minedBy": "Bowser Jr.",
        "timestamp": int(time.time())
    }
    new_block['hash'] = previous_block['hash']

    nonce = '0'
    new_block['nonce'] = nonce
    nonce_found = False
    while not nonce_found:
        nonce = str(int(nonce) + 1)
        new_block['nonce'] = nonce
        hashBase = peer.get_block_hash(new_block, previous_block)
        if hashBase[-1 * difficulty:] == '0' * difficulty:
            new_block["hash"] = hashBase
            nonce_found = True
    
    return new_block

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
                    handle_newword(json_response, DIFFICULTY, client_connect)

                client_connect.close()

            except KeyboardInterrupt as key:
                print("Program Stopped. Interrupted by keyboard.")
                sys.exit()
            except Exception as error_msg:
                print(error_msg)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("host", type=str, help="Worker's host")
    parser.add_argument("port", type=int, help="Worker's port")

    args = parser.parse_args()
    socket_con_nothread(args.host, args.port)


if __name__ == "__main__":
    main()