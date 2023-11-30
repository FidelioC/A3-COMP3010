import argparse
import socket
import json
import sys

class Miner:
    def __init__(self, miner_host = None, miner_port = None):
        self.miner_host = miner_host
        self.miner_port = miner_port

    def send_maxblock_miner(self, max_block):
        #send current max block to miner
        print(f"SENDING MAX BLOCK TO WORKER PORT: {self.miner_port}, MESSAGE SEND: {max_block}")
        request_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        request_socket.connect((self.miner_host, self.miner_port))
        request_socket.send(json.dumps(max_block).encode())

    def req_newword_miner(self, new_word):
        # send new word request to miner
        print(f"SENDING NEW WORD TO WORKER PORT: {self.miner_port}, MESSAGE SEND: {new_word}")
        request_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        request_socket.connect((self.miner_host, self.miner_port))
        request_socket.send(json.dumps(new_word).encode())

    def __str__(self) -> str:
        return f"Miner host: {self.miner_host}, miner port: {self.miner_port}"
    
def miners_to_object(miner_input):
    host,port = miner_input
    return Miner(host, port)

def insert_miner(miner_inputs, miner_list):
    for miner_input in miner_inputs:
        miner_list.append(miners_to_object(miner_input))

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

                data = json.loads(client_connect.recv(1024).decode())
                print(f"Received: {data}\n")

                client_connect.close()

            except KeyboardInterrupt as key:
                print("Program Stopped. Interrupted by keyboard.")
                sys.exit()
            except Exception as error_msg:
                print(error_msg.with_traceback())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("host", type=str, help="Worker's host")
    parser.add_argument("port", type=int, help="Worker's port")

    args = parser.parse_args()
    socket_con_nothread(args.host, args.port)


if __name__ == "__main__":
    main()