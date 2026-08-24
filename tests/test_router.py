from meshweaver.dht import KademliaDHT
from meshweaver.router import TaskRouter, TaskStatus

def test_router_selects_lowest_cpu_peer():
    dht = KademliaDHT("node-a")

    peer_b = dht.add_peer("127.0.0.1", 9002)
    peer_c = dht.add_peer("127.0.0.1", 9003)
    peer_d = dht.add_peer("127.0.0.1", 9004)

    router = TaskRouter()

    router.update_resource(peer_b.node_id, cpu_percent=80.0)
    router.update_resource(peer_c.node_id, cpu_percent=25.0)
    router.update_resource(peer_d.node_id, cpu_percent=60.0)

    selected = router.select_peer(dht.get_peers())

    assert selected is not None
    assert selected.node_id == peer_c.node_id


def test_router_returns_none_without_resource_data():
    dht = KademliaDHT("node-a")

    peer = dht.add_peer("127.0.0.1", 9002)

    router = TaskRouter()

    selected = router.select_peer(dht.get_peers())

    assert selected is None


def test_router_updates_peer_resource():
    dht = KademliaDHT("node-a")

    peer = dht.add_peer("127.0.0.1", 9002)

    router = TaskRouter()

    router.update_resource(
        peer.node_id,
        cpu_percent=35.0,
        ram_percent=50.0,
    )

    assert peer.node_id in router.resources
    assert router.resources[peer.node_id].cpu_percent == 35.0
    assert router.resources[peer.node_id].ram_percent == 50.0


def test_automatic_task_reassignment():
    dht = KademliaDHT("node-a")

    peer_a = dht.add_peer("127.0.0.1", 9001)
    peer_b = dht.add_peer("127.0.0.1", 9002)

    router = TaskRouter()

    # Register healthy peer resources
    router.update_resource(
        peer_a.node_id,
        cpu_percent=20.0,
    )

    router.update_resource(
        peer_b.node_id,
        cpu_percent=40.0,
    )

    # Assign tasks to peer A
    assert router.assign_task(
        "task-1",
        peer_a,
    )

    assert router.assign_task(
        "task-2",
        peer_a,
    )

    # Simulate peer A failure
    reassigned = router.reassign_tasks(
        peer_a.node_id,
        [peer_a, peer_b],
    )

    # Tasks should move to peer B
    assert reassigned["task-1"] == peer_b.node_id
    assert reassigned["task-2"] == peer_b.node_id

    # Verify task lifecycle state
    assert router.tasks["task-1"].peer_id == peer_b.node_id
    assert router.tasks["task-2"].peer_id == peer_b.node_id

    assert router.tasks["task-1"].status == TaskStatus.REASSIGNED
    assert router.tasks["task-2"].status == TaskStatus.REASSIGNED