from meshweaver.router import Task
from meshweaver.task_queue import TaskQueue


def test_add_task():
    queue = TaskQueue()
    task = Task("task-1")

    assert queue.add_task(task) is True
    assert queue.contains("task-1") is True
    assert queue.size() == 1


def test_duplicate_task_is_not_added():
    queue = TaskQueue()
    task = Task("task-1")

    assert queue.add_task(task) is True
    assert queue.add_task(task) is False
    assert queue.size() == 1


def test_get_next_task():
    queue = TaskQueue()
    task1 = Task("task-1")
    task2 = Task("task-2")

    queue.add_task(task1)
    queue.add_task(task2)

    next_task = queue.get_next_task()

    assert next_task is task1
    assert queue.size() == 2


def test_pop_task():
    queue = TaskQueue()
    task1 = Task("task-1")
    task2 = Task("task-2")

    queue.add_task(task1)
    queue.add_task(task2)

    popped_task = queue.pop_task()

    assert popped_task is task1
    assert queue.contains("task-1") is False
    assert queue.contains("task-2") is True
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


def test_remove_nonexistent_task():
    queue = TaskQueue()

    assert queue.remove_task("missing-task") is False


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
    assert queue.contains("task-2") is False


def test_queue_statistics():
    queue = TaskQueue()

    queue.add_task(Task("task-1"))
    queue.add_task(Task("task-2"))

    stats = queue.statistics()

    assert stats["total_tasks"] == 2
    assert stats["queue_size"] == 2
    assert stats["is_empty"] is False


def test_empty_queue_statistics():
    queue = TaskQueue()

    stats = queue.statistics()

    assert stats["total_tasks"] == 0
    assert stats["queue_size"] == 0
    assert stats["is_empty"] is True


def test_queue_statistics_includes_task_ids():
    queue = TaskQueue()

    queue.add_task(Task("task-1"))
    queue.add_task(Task("task-2"))
    queue.add_task(Task("task-3"))

    stats = queue.statistics()

    assert stats["task_ids"] == ["task-1", "task-2", "task-3"]


def test_queue_statistics_includes_next_task():
    queue = TaskQueue()

    queue.add_task(Task("task-1"))
    queue.add_task(Task("task-2"))

    stats = queue.statistics()

    assert stats["next_task_id"] == "task-1"


def test_empty_queue_statistics_has_no_next_task():
    queue = TaskQueue()

    stats = queue.statistics()

    assert stats["task_ids"] == []
    assert stats["next_task_id"] is None