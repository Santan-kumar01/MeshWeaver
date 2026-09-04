from meshweaver.dht import KademliaDHT
from meshweaver.gossip import GossipProtocol


def test_gossip_shares_peers():
    dht_a = KademliaDHT("node-a")
    dht_b = KademliaDHT("node-b")

    # Node A knows Node C
    peer_c = dht_a.add_peer("127.0.0.1", 9003)

    gossip_a = GossipProtocol(dht_a)
    gossip_b = GossipProtocol(dht_b)

    # Node A creates gossip message
    message = gossip_a.create_message()

    # Node B receives the message
    added = gossip_b.receive_message(message)

    assert added == 1
    assert dht_b.has_peer(peer_c.node_id)


def test_gossip_does_not_add_duplicate_peer():
    dht_a = KademliaDHT("node-a")
    dht_b = KademliaDHT("node-b")

    peer_c = dht_a.add_peer("127.0.0.1", 9003)

    gossip_a = GossipProtocol(dht_a)
    gossip_b = GossipProtocol(dht_b)

    message = gossip_a.create_message()

    gossip_b.receive_message(message)
    added_again = gossip_b.receive_message(message)

    assert added_again == 0
    assert dht_b.peer_count() == 1


def test_gossip_ignores_sender():
    dht_a = KademliaDHT("node-a")

    # Node A already knows another peer
    dht_a.add_peer("127.0.0.1", 9003)

    gossip_a = GossipProtocol(dht_a)

    message = gossip_a.create_message()

    assert message.sender_id == "node-a"
    assert len(message.peers) == 1