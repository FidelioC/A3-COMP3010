import peer
import time
def test_getpeer():
    peer_obj_list = []
    peer_obj = peer.Peer("test","test","name",1)
    peer_obj_list.append(peer_obj)
    print(peer.get_peer(1,peer_obj_list))

def test_renewtimeout():
    peer_obj_list = []
    peer_obj = peer.Peer("test","test","name",1)
    peer_obj_list.append(peer_obj)
    print(f"BEFORE: {peer_obj}")
    peer.renew_timeout_peer(1,peer_obj_list)
    print(f"AFTER: {peer_obj}")

def test_removepeer():
    curr_time = time.time()
    peer_obj_list = []
    peer_obj = peer.Peer("test","test","name",1)
    peer_obj_list.append(peer_obj)
    print(f"currtime: {curr_time}")
    print(f"peerobj: {peer_obj}")

    curr_time = curr_time + 61
    print(f"currtime+61: {curr_time}")

    peer.remove_peer(1,peer_obj_list,curr_time)

def main():
    # test_getpeer()
    # test_renewtimeout()
    test_removepeer()

if __name__ == "__main__":
    main()
