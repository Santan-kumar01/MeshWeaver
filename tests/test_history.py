from meshweaver.dht import KademliaDHT
from meshweaver.router import TaskRouter, TaskStatus


def test_completed_task_result_is_persisted():
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

    assert router.assign_task(
        "task-1",
        peer,
    )

    assert router.start_task("task-1")

    assert router.complete_task(
        "task-1",
        result={"message": "success"},
    )

    assert router.get_task_result(
        "task-1"
    ) == {"message": "success"}


def test_execution_history_is_saved():
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

    router.assign_task(
        "task-1",
        peer,
    )

    router.start_task("task-1")

    router.complete_task(
        "task-1",
        result=42,
    )

    history = router.get_execution_history(
        "task-1"
    )

    assert len(history) == 1
    assert history[0].task_id == "task-1"
    assert history[0].peer_id == peer.node_id
    assert history[0].status == TaskStatus.COMPLETED
    assert history[0].result == 42


def test_failed_task_error_is_persisted():
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

    router.assign_task(
        "task-1",
        peer,
    )

    router.start_task("task-1")

    router.fail_task(
        "task-1",
        error="Execution failed",
    )

    assert router.get_task_error(
        "task-1"
    ) == "Execution failed"

    history = router.get_execution_history(
        "task-1"
    )

    assert len(history) == 1
    assert history[0].status == TaskStatus.FAILED
    assert history[0].error == "Execution failed"


def test_latest_execution_is_available():
    router = TaskRouter()

    router.create_task("task-1")

    assert router.get_latest_execution(
        "task-1"
    ) is None


def test_execution_history_is_empty_for_unknown_task():
    router = TaskRouter()

    history = router.get_execution_history(
        "unknown-task"
    )

    assert history == []