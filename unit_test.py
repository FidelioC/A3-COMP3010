import peer_no_miner
import time
import miner
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

    peer.remove_peer(peer_obj_list,curr_time)

def test_findmaxheight():
    # Example usage
    stats_reply_list = [
        {'type': 'STATS_REPLY', 'height': 140, 'hash': '8ffac79219d5a071d3223fa0a67bf1c1a725c22cca2c4d0d93d685f000000000', 'host': '130.179.28.134', 'port': 8472},
        {'type': 'STATS_REPLY', 'height': 140, 'hash': '8ffac79219d5a071d3223fa0a67bf1c1a725c22cca2c4d0d93d685f000000000', 'host': '130.179.28.37', 'port': 8999},
        {'type': 'STATS_REPLY', 'height': 140, 'hash': '8ffac79219d5a071d3223fa0a67bf1c1a725c22cca2c4d0d93d685f000000000', 'host': '130.179.28.117', 'port': 8999},
        {'type': 'STATS_REPLY', 'height': 140, 'hash': '8ffac79219d5a071d3223fa0a67bf1c1a725c22cca2c4d0d93d685f000000000', 'host': '10.152.152.40', 'port': 8750},
        {'type': 'STATS_REPLY', 'height': 140, 'hash': 'qwdwqdqwdqwdwdq', 'host': '130.179.28.127', 'port': 8999},
        {'type': 'STATS_REPLY', 'height': 130, 'hash': '8ffac79219d5a071d3223fa0a67bf1c1a7qwdqwdqwdwdwfe000000000', 'host': '130.179.28.129', 'port': 8999}
    ]

    lists = peer.find_max_height(stats_reply_list)
    for list in lists:
        print(f"{list} \n")

def test_find_majority_hash():
    # Example usage
    stats_reply_list = [
        {'type': 'STATS_REPLY', 'height': 140, 'hash': '8ffac79219d5a071d3223fa0a67bf1c1a725c22cca2c4d0d93d685f000000000', 'host': '130.179.28.134', 'port': 8472},
        {'type': 'STATS_REPLY', 'height': 140, 'hash': '8ffac79219d5a071d3223fa0a67bf1c1a725c22cca2c4d0d93d685f000000000', 'host': '130.179.28.37', 'port': 8999},
        {'type': 'STATS_REPLY', 'height': 140, 'hash': '8ffac79219d5a071d3223fa0a67bf1c1a725c22cca2c4d0d93d685f000000000', 'host': '130.179.28.117', 'port': 8999},
        {'type': 'STATS_REPLY', 'height': 140, 'hash': '8ffac79219d5a071d3223fa0a67bf1c1a725c22cca2c4d0d93d685f000000000', 'host': '10.152.152.40', 'port': 8750},
        {'type': 'STATS_REPLY', 'height': 140, 'hash': 'qwdwqdqwdqwdwdq', 'host': '130.179.28.127', 'port': 8999},
        {'type': 'STATS_REPLY', 'height': 130, 'hash': '8ffac79219d5a071d3223fa0a67bf1c1a725c22cca2c4d0d93d685f000000000', 'host': '130.179.28.129', 'port': 8999}
    ]
    lists = peer.find_majority_hash(stats_reply_list)
    for list in lists:
        print(f"{list} \n")

def test_getconsensuslist():
    # Example usage
    stats_reply_list = [
        {'type': 'STATS_REPLY', 'height': 0, 'hash': 'adada', 'host': '130.179.28.134', 'port': 8472},
        {'type': 'STATS_REPLY', 'height': 140, 'hash': 'adada', 'host': '130.179.28.37', 'port': 8999},
        {'type': 'STATS_REPLY', 'height': 139, 'hash': 'adada', 'host': '130.179.28.117', 'port': 8999},
        {'type': 'STATS_REPLY', 'height': 139, 'hash': 'adada', 'host': '10.152.152.40', 'port': 8750},
        {'type': 'STATS_REPLY', 'height': 139, 'hash': 'adada', 'host': '130.179.28.127', 'port': 8999},
        {'type': 'STATS_REPLY', 'height': 139, 'hash': 'adada', 'host': '130.179.28.129', 'port': 8999}
    ]
    lists = peer.get_consensus_list(stats_reply_list)
    for list in lists:
        print(f"{list} \n")

def test_findmissingblock():
    chain = [
        {'hash': '5b0cc813303f305927dbaf559bebab19229ba30106687a61ed4c62d000000000', 'height': 0, 'messages': ["wiz's", 'shrouded', 'regenerates', "reconnaissance's", 'penitence'], 'minedBy': 'Prof!', 'nonce': '2251755442', 'timestamp': 1700636371},
        {'hash': '6e242a9cb5822240f8de04a6b7a7ce9813a9587eb9cf621dcca93bb000000000', 'height': 2, 'messages': ['overanimated'], 'minedBy': 'GossipZilla!', 'nonce': '2083334054052021', 'timestamp': 1700655104},
        {'hash': 'bb02ecf8b3ff4bb3e18ff08217c6d3429895da1f34833888fee339e000000000', 'height': 4, 'messages': ['fly-stuck'], 'minedBy': 'GossipZilla!', 'nonce': '4583335277304293', 'timestamp': 1700656987},
        {'hash': 'c156db5000397adbfbf068c16e469ff9dcf083c896a1688b17708b5000000000', 'height': 8, 'messages': ['Bontocs', 'waivers'], 'minedBy': 'GossipZilla!', 'nonce': '208333437970814', 'timestamp': 1700662569},
        {'hash': '8a2fa39a68461965b19aedd0544674d916d91872f8b545115043742000000000', 'height': 10, 'messages': ['gymnotid', 'Leupold'], 'minedBy': 'GossipZilla!', 'nonce': '4583333401198356', 'timestamp': 1700671783},
    ]
    missing_blocks = peer.find_missing_blocks(chain, 20)
    for block in missing_blocks:
        print(f"{block}")

def test_validate_block():
    test_block = {'hash': 'c94101870f308e28e7ada1e98d46f58cffad3452c05175a7d44565d000000000', 'height': 2014, 'messages': ['subservience', "region's", "protÃ©gÃ©'s", "catchword's", 'affording', "bookmark's", 'grub', 'fizzing'], 'minedBy': 'Bryce', 'nonce': 'GQfaBI210APjUm8pb5vQ', 'timestamp': 1701741408, 'addr': ('130.179.28.122', 8755)}
    block = {'hash': 'f916ed002a20454b6515e43aab622110674fb386d0c47f5251ae2f9000000000', 'height': 2013, 'messages': ['fun'], 'minedBy': 'leorize', 'nonce': '*Ic\x1dB:D\x12e?\x1a\x18U2K&', 'timestamp': 1701741360, 'addr': ('130.179.28.122', 8755)}
    
    next_block = {'hash': '5b0cc813303f305927dbaf559bebab19229ba30106687a61ed4c62d000000000', 
                  'height': 1, 
                  'messages': ["wiz's", 
                               'shrouded', 
                               'regenerates', 
                               "reconnaissance's", 
                               'penitence'], 
                   'minedBy': 'Prof!', 
                   'nonce': '2251755442', 
                   'timestamp': 1700636371}
    block80 = {'hash': '2fc329f7cbf06417158665c819d29f6ea1f41e6789c269ca6b6de8c000000000', 'height': 80, 'messages': ['Elstan', 'funmaking'], 'minedBy': 'GossipZilla!', 'nonce': '1458333614994197', 'timestamp': 1700823420}
    block79 = {'hash': '0eb8fd66cb4f1937f5ccfb1a661955bb42c7168ef300baef191e057000000000', 'height': 79, 'messages': ['PSI'], 'minedBy': 'GossipZilla!', 'nonce': '2500000301125418', 'timestamp': 1700822662}
    
    prev_block = {   'hash': '7d04464769f93fde871f1fa9e5c0c0874a94a444822f4dbfb27e7c7d09976c20',
    'height': 343,
    'messages': ['testannounce'],
    'minedBy': 'Prof!',
    'nonce': '6446110839462',
    'timestamp': 1701981756,}
    my_block = {   'hash': '0dd66f47a67fc53226dc478d60530757fb19bd40a72c983d09ef9a01a8ed2d40',
    'height': 344,
    'messages': ['o'],
    'minedBy': 'Bowser Jr.',
    'nonce': '6446110839492',
    'timestamp': 1701982929,
    }
    # print(f"MESSAGE {peer.validate_block_messages(block80['messages'])}")
    # print(f"NONCE {peer.validate_block_nonce(block80['nonce'])}")
    print(f"VALIDATE BLOCK {peer_no_miner.validate_block(my_block, prev_block)}")

    print(f"TEST BLOCK {peer_no_miner.get_block_hash(my_block, prev_block)}")
    

def test_validate_chain():
    curr_chain = [
        {'hash': 'da32c5e6d1478caad5c39eea5f05855daed3bda5980da4633aa1e5c000000000', 'height': 0, 'messages': ['3010 rocks', 'Warning:', 'Procrastinators', 'will be sent back', 'in time to start', 'early.', 'Chain 2'], 'minedBy': 'Prof!', 'nonce': '742463477029129', 'timestamp': 1700629652},
        {'hash': '5b0cc813303f305927dbaf559bebab19229ba30106687a61ed4c62d000000000', 'height': 1, 'messages': ["wiz's", 'shrouded', 'regenerates', "reconnaissance's", 'penitence'], 'minedBy': 'Prof!', 'nonce': '2251755442', 'timestamp': 1700636371},
        {'hash': '6e242a9cb5822240f8de04a6b7a7ce9813a9587eb9cf621dcca93bb000000000', 'height': 2, 'messages': ['overanimated'], 'minedBy': 'GossipZilla!', 'nonce': '2083334054052021', 'timestamp': 1700655104},
        {'hash': 'bb02ecf8b3ff4bb3e18ff08217c6d3429895da1f34833888fee339e000000000', 'height': 3, 'messages': ['fly-stuck'], 'minedBy': 'GossipZilla!', 'nonce': '4583335277304293', 'timestamp': 1700656987},
        {'hash': 'c156db5000397adbfbf068c16e469ff9dcf083c896a1688b17708b5000000000', 'height': 4, 'messages': ['Bontocs', 'waivers'], 'minedBy': 'GossipZilla!', 'nonce': '208333437970814', 'timestamp': 1700662569},
        {'hash': '4e2b16394768d1c819fe66976a6d650bd26c3eaa2f0ea362c220c23000000000', 'height': 5, 'messages': ["lubricant's", 'recap', 'peeved', 'intestines', 'blabbed', "nosiness's", 'creaming', 'fascists', 'castles', 'revolt'], 'minedBy': 'Prof!', 'nonce': '18822851911', 'timestamp': 1700670806},   
    ]
    print(f"VALIDATE CHAIN {peer.validate_chain(curr_chain)}")

def test_handleannounce():
    current_chain = [
        {'hash': 'da32c5e6d1478caad5c39eea5f05855daed3bda5980da4633aa1e5c000000000', 
             'height': 0, 
             'messages': ['3010 rocks', 
                          'Warning:', 
                          'Procrastinators', 
                          'will be sent back', 
                          'in time to start', 
                          'early.', 
                          'Chain 2'], 
             'minedBy': 'Prof!', 
             'nonce': '742463477029129', 
             'timestamp': 1700629652},
        ]
    response = {
        'type': 'ANNOUNCE',
        'hash': '5b0cc813303f305927dbaf559bebab19229ba30106687a61ed4c62d000000000', 
                  'height': 1, 
                  'messages': ["wiz's", 
                               'shrouded', 
                               'regenerates', 
                               "reconnaissance's", 
                               'penitence'], 
                   'minedBy': 'Prof!', 
                   'nonce': '2251755442', 
                   'timestamp': 1700636371
    }

    peer.handle_announce(response, current_chain)
    print(current_chain)

def test_mineblock():
    prev_block = {   'hash': 'da32c5e6d1478caad5c39eea5f05855daed3bda5980da4633aa1e5c000',
    'height': 0,
    'messages': [   '3010 rocks',
                    'Warning:',
                    'Procrastinators',
                    'will be sent back',
                    'in time to start',
                    'early.',
                    'Chain 2'],
    'minedBy': 'Prof!',
    'nonce': '742463477029129',
    'timestamp': 1700629652,
    'type': 'GET_BLOCK_REPLY'}
    
    block = miner.mine_block(prev_block, "test", 3)
    print(block)
    print(f"validating block: {peer.validate_block(block, prev_block)}")

def main():
    # test_getpeer()
    # test_renewtimeout()
    # test_removepeer()
    # test_findmaxheight()
    # test_find_majority_hash()
    # test_getconsensuslist()
    # test_findmissingblock()
    test_validate_block()
    # test_validate_chain()
    # test_handleannounce()
    # test_mineblock()



if __name__ == "__main__":
    main()


# echo '{"type":"NEW_WORD", "word":"test"}' | nc -u kingfisher 8795
''' echo '{"type":"MAX_BLOCK", "hash": "da32c5e6d1478caad5c39eea5f05855daed3bda5980da4633aa1e5c000000000", "height": 0, "messages": ["3010 rocks", "Warning:", "Procrastinators", "will be sent back", "in time to start", "early.", "Chain 2"], "minedBy": "Prof!", "nonce": "742463477029129", "timestamp": 1700629652}' | nc -u kingfisher 8795'''
# echo '{"type":"CONSENSUS"}' | nc -u kingfisher 8795
# echo '{"type":"STATS"}' | nc -u kingfisher 8795
