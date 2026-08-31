from meshweaver.queue_monitor import QueueMonitor
from meshweaver.task_priority import TaskPriorityQueue
from meshweaver.router import Task


def test_initial_monitor_status():
    queue = TaskPriorityQueue()
    monitor = QueueMonitor(queue)

    status = monitor.get_status()

    assert status["queue_size"] == 0
    assert status["total_added"] == 0
    assert status["total_processed"] == 0
    assert status["total_removed"] == 0


def test_record_added():
    queue = TaskPriorityQueue()
    monitor = QueueMonitor(queue)

    monitor.record_added()
    monitor.record_added()

    assert monitor.get_status()["total_added"] == 2


def test_record_processed():
    queue = TaskPriorityQueue()
    monitor = QueueMonitor(queue)

    monitor.record_processed()

    assert monitor.get_status()["total_processed"] == 1


def test_record_removed():
    queue = TaskPriorityQueue()
    monitor = QueueMonitor(queue)

    monitor.record_removed()

    assert monitor.get_status()["total_removed"] == 1


def test_queue_size_is_reported():
    queue = TaskPriorityQueue()
    monitor = QueueMonitor(queue)

    queue.add_task(Task("task-1"), "HIGH")
    queue.add_task(Task("task-2"), "LOW")

    assert monitor.get_status()["queue_size"] == 2


def test_monitor_is_healthy():
    queue = TaskPriorityQueue()
    monitor = QueueMonitor(queue)

    assert monitor.is_healthy() is True


def test_summary_contains_queue_information():
    queue = TaskPriorityQueue()
    monitor = QueueMonitor(queue)

    monitor.record_added()

    summary = monitor.summary()

    assert "Queue size: 0" in summary
    assert "Added: 1" in summary