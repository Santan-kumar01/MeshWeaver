from meshweaver.dht import KademliaDHT


def test_add_and_find_peer():
    dht = KademliaDHT("node-a")

    peer = dht.add_peer("127.0.0.1", 9002)

    assert peer.host == "127.0.0.1"
    assert peer.port == 9002
    assert dht.has_peer(peer.node_id)

    found = dht.find_peer(peer.node_id)

    assert found is not None
    assert found.node_id == peer.node_id


def test_remove_peer():
    dht = KademliaDHT("node-a")

    peer = dht.add_peer("127.0.0.1", 9002)

    assert dht.has_peer(peer.node_id)

    removed = dht.remove_peer(peer.node_id)

    assert removed is True
    assert not dht.has_peer(peer.node_id)


def test_peer_count():
    dht = KademliaDHT("node-a")

    dht.add_peer("127.0.0.1", 9002)
    dht.add_peer("127.0.0.1", 9003)
    dht.add_peer("127.0.0.1", 9004)

    assert dht.peer_count() == 3


def test_find_closest_peers():
    dht = KademliaDHT("node-a")

    p1 = dht.add_peer("127.0.0.1", 9002)
    p2 = dht.add_peer("127.0.0.1", 9003)
    p3 = dht.add_peer("127.0.0.1", 9004)

    target = p1.node_id

    closest = dht.find_closest_peers(target, 2)

    assert len(closest) == 2
    assert all(peer in [p1, p2, p3] for peer in closest)


def test_generate_node_id_is_consistent():
    dht = KademliaDHT("node-a")

    id1 = dht.generate_node_id("127.0.0.1", 9002)
    id2 = dht.generate_node_id("127.0.0.1", 9002)

    assert id1 == id2