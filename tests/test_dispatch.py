from meshweaver.dht import KademliaDHT
from meshweaver.router import TaskRouter
from meshweaver.task_queue import TaskQueue


def test_dispatch_selects_lowest_cpu_peer():
    dht = KademliaDHT("node-a")

    peer_a = dht.add_peer("127.0.0.1", 9001)
    peer_b = dht.add_peer("127.0.0.1", 9002)

    router = TaskRouter()

    router.update_resource(
        peer_a.node_id,
        cpu_percent=80.0,
    )

    router.update_resource(
        peer_b.node_id,
        cpu_percent=20.0,
    )

    queue = TaskQueue()

    task = router.create_task("task-1")
    queue.add_task(task)

    selected = router.select_peer(
        dht.get_peers()
    )

    assert selected is not None
    assert selected.node_id == peer_b.node_id


def test_dispatch_removes_task_from_queue():
    dht = KademliaDHT("node-a")

    peer = dht.add_peer(
        "127.0.0.1",
        9001,
    )

    router = TaskRouter()

    router.update_resource(
        peer.node_id,
        cpu_percent=30.0,
    )

    queue = TaskQueue()

    task = router.create_task("task-1")
    queue.add_task(task)

    assert queue.get_next_task() is not None

    removed = queue.remove_task("task-1")

    assert removed is True
    assert queue.get_next_task() is None


def test_dispatch_returns_none_for_empty_queue():
    queue = TaskQueue()

    assert queue.get_next_task() is None


def test_dispatch_returns_none_without_available_peer():
    dht = KademliaDHT("node-a")

    peer = dht.add_peer(
        "127.0.0.1",
        9001,
    )

    router = TaskRouter()

    queue = TaskQueue()

    task = router.create_task("task-1")
    queue.add_task(task)

    selected = router.select_peer(
        dht.get_peers()
    )

    assert selected is None