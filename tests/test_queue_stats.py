from meshweaver.router import Task
from meshweaver.task_priority import TaskPriorityQueue
from meshweaver.queue_stats import QueueStatistics


def test_total_tasks():
    queue = TaskPriorityQueue()
    stats = QueueStatistics(queue)

    queue.add_task(Task("task-1"), "HIGH")
    queue.add_task(Task("task-2"), "MEDIUM")
    queue.add_task(Task("task-3"), "LOW")

    assert stats.total_tasks() == 3


def test_high_priority_count():
    queue = TaskPriorityQueue()
    stats = QueueStatistics(queue)

    queue.add_task(Task("task-1"), "HIGH")
    queue.add_task(Task("task-2"), "HIGH")
    queue.add_task(Task("task-3"), "LOW")

    assert stats.high_priority_tasks() == 2


def test_medium_priority_count():
    queue = TaskPriorityQueue()
    stats = QueueStatistics(queue)

    queue.add_task(Task("task-1"), "MEDIUM")
    queue.add_task(Task("task-2"), "HIGH")
    queue.add_task(Task("task-3"), "MEDIUM")

    assert stats.medium_priority_tasks() == 2


def test_low_priority_count():
    queue = TaskPriorityQueue()
    stats = QueueStatistics(queue)

    queue.add_task(Task("task-1"), "LOW")
    queue.add_task(Task("task-2"), "LOW")
    queue.add_task(Task("task-3"), "HIGH")

    assert stats.low_priority_tasks() == 2


def test_empty_queue_statistics():
    queue = TaskPriorityQueue()
    stats = QueueStatistics(queue)

    assert stats.total_tasks() == 0
    assert stats.is_empty() is True


def test_summary():
    queue = TaskPriorityQueue()
    stats = QueueStatistics(queue)

    queue.add_task(Task("task-1"), "HIGH")
    queue.add_task(Task("task-2"), "HIGH")
    queue.add_task(Task("task-3"), "MEDIUM")
    queue.add_task(Task("task-4"), "LOW")

    assert stats.summary() == {
        "total": 4,
        "high": 2,
        "medium": 1,
        "low": 1,
    }


def test_invalid_priority_statistics():
    queue = TaskPriorityQueue()
    stats = QueueStatistics(queue)

    try:
        stats.count_by_priority("URGENT")
        assert False
    except ValueError:
        assert True