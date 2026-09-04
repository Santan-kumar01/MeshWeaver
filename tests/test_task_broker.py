from meshweaver.task_broker import TaskBroker


def test_submit_task():
    broker = TaskBroker()

    task = broker.submit_task("task-1")

    assert task is not None
    assert task.task_id == "task-1"
    assert broker.queue_size() == 1


def test_duplicate_task_is_not_submitted():
    broker = TaskBroker()

    first = broker.submit_task("task-1")
    second = broker.submit_task("task-1")

    assert first is not None
    assert second is None
    assert broker.queue_size() == 1


def test_get_next_task():
    broker = TaskBroker()

    broker.submit_task("task-1")
    broker.submit_task("task-2")

    task = broker.get_next_task()

    assert task is not None
    assert task.task_id == "task-1"
    assert broker.queue_size() == 2


def test_pop_next_task():
    broker = TaskBroker()

    broker.submit_task("task-1")
    broker.submit_task("task-2")

    task = broker.pop_next_task()

    assert task is not None
    assert task.task_id == "task-1"
    assert broker.queue_size() == 1


def test_get_task():
    broker = TaskBroker()

    broker.submit_task("task-1")

    task = broker.get_task("task-1")

    assert task is not None
    assert task.task_id == "task-1"


def test_statistics():
    broker = TaskBroker()

    broker.submit_task("task-1")
    broker.submit_task("task-2")

    stats = broker.statistics()

    assert stats["total_tasks"] == 2
    assert stats["queue_size"] == 2
    assert stats["is_empty"] is False
    assert stats["task_ids"] == ["task-1", "task-2"]
    assert stats["next_task_id"] == "task-1"


def test_empty_broker():
    broker = TaskBroker()

    assert broker.get_next_task() is None
    assert broker.pop_next_task() is None
    assert broker.queue_size() == 0

    stats = broker.statistics()

    assert stats["total_tasks"] == 0
    assert stats["is_empty"] is True
    assert stats["next_task_id"] is None