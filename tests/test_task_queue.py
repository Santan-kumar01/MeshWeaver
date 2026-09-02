from meshweaver.router import Task
from meshweaver.task_queue import TaskQueue


def test_add_task():
    queue = TaskQueue()

    task = Task("task-1")

    assert queue.add_task(task) is True
    assert queue.size() == 1
    assert queue.contains("task-1")


def test_fifo_order():
    queue = TaskQueue()

    task1 = Task("task-1")
    task2 = Task("task-2")
    task3 = Task("task-3")

    queue.add_task(task1)
    queue.add_task(task2)
    queue.add_task(task3)

    assert queue.pop_task().task_id == "task-1"
    assert queue.pop_task().task_id == "task-2"
    assert queue.pop_task().task_id == "task-3"


def test_duplicate_task_is_rejected():
    queue = TaskQueue()

    task = Task("task-1")

    assert queue.add_task(task) is True
    assert queue.add_task(task) is False
    assert queue.size() == 1


def test_get_next_task_without_removing():
    queue = TaskQueue()

    task = Task("task-1")

    queue.add_task(task)

    next_task = queue.get_next_task()

    assert next_task is not None
    assert next_task.task_id == "task-1"
    assert queue.size() == 1


def test_remove_task():
    queue = TaskQueue()

    task1 = Task("task-1")
    task2 = Task("task-2")

    queue.add_task(task1)
    queue.add_task(task2)

    assert queue.remove_task("task-1") is True
    assert queue.contains("task-1") is False
    assert queue.size() == 1
    assert queue.get_next_task().task_id == "task-2"


def test_remove_unknown_task():
    queue = TaskQueue()

    assert queue.remove_task("unknown") is False


def test_empty_queue():
    queue = TaskQueue()

    assert queue.is_empty() is True
    assert queue.size() == 0
    assert queue.get_next_task() is None
    assert queue.pop_task() is None


def test_clear_queue():
    queue = TaskQueue()

    queue.add_task(Task("task-1"))
    queue.add_task(Task("task-2"))

    queue.clear()

    assert queue.is_empty() is True
    assert queue.size() == 0
    assert queue.contains("task-1") is False


def test_queue_statistics():
    queue = TaskQueue()

    queue.add_task(Task("task-1"))
    queue.add_task(Task("task-2"))
    queue.add_task(Task("task-3"))

    stats = queue.statistics()

    assert stats["total_tasks"] == 3
    assert stats["queue_size"] == 3
    assert stats["is_empty"] is False


def test_empty_queue_statistics():
    queue = TaskQueue()

    stats = queue.statistics()

    assert stats["total_tasks"] == 0
    assert stats["queue_size"] == 0
    assert stats["is_empty"] is True