from meshweaver.router import TaskRouter, TaskStatus
from meshweaver.dht import KademliaDHT


def test_completed_task_is_saved_in_history():
    dht = KademliaDHT("node-a")

    peer = dht.add_peer(
        "127.0.0.1",
        9002,
    )

    router = TaskRouter()

    router.update_resource(
        peer.node_id,
        cpu_percent=20.0,
    )

    router.create_task("task-1")

    assert router.assign_task(
        "task-1",
        peer,
    )

    assert router.start_task("task-1")

    assert router.complete_task(
        "task-1",
        result="success",
    )

    history = router.get_execution_history("task-1")

    assert len(history) == 1
    assert history[0].task_id == "task-1"
    assert history[0].peer_id == peer.node_id
    assert history[0].status == TaskStatus.COMPLETED
    assert history[0].result == "success"


def test_failed_task_is_saved_in_history():
    dht = KademliaDHT("node-a")

    peer = dht.add_peer(
        "127.0.0.1",
        9002,
    )

    router = TaskRouter()

    router.update_resource(
        peer.node_id,
        cpu_percent=20.0,
    )

    router.create_task("task-2")

    assert router.assign_task(
        "task-2",
        peer,
    )

    assert router.start_task("task-2")

    assert router.fail_task(
        "task-2",
        error="Execution failed",
    )

    history = router.get_execution_history("task-2")

    assert len(history) == 1
    assert history[0].status == TaskStatus.FAILED
    assert history[0].error == "Execution failed"


def test_latest_execution_is_returned():
    router = TaskRouter()

    router.create_task("task-3")

    router.record_execution(
        "task-3",
        TaskStatus.FAILED,
        error="First attempt failed",
        retry_count=1,
    )

    router.record_execution(
        "task-3",
        TaskStatus.COMPLETED,
        result="success",
        retry_count=2,
    )

    latest = router.get_latest_execution("task-3")

    assert latest is not None
    assert latest.status == TaskStatus.COMPLETED
    assert latest.result == "success"
    assert latest.retry_count == 2


def test_empty_history_returns_empty_list():
    router = TaskRouter()

    history = router.get_execution_history(
        "unknown-task",
    )

    assert history == []


def test_latest_execution_returns_none_for_unknown_task():
    router = TaskRouter()

    latest = router.get_latest_execution(
        "unknown-task",
    )

    assert latest is None