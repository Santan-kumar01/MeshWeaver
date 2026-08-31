from meshweaver.router import Task
from meshweaver.task_priority import TaskPriorityQueue


def test_high_priority_runs_before_medium_and_low():
    queue = TaskPriorityQueue()

    low = Task("low-task")
    medium = Task("medium-task")
    high = Task("high-task")

    queue.add_task(low, "LOW")
    queue.add_task(medium, "MEDIUM")
    queue.add_task(high, "HIGH")

    assert queue.pop_task().task_id == "high-task"
    assert queue.pop_task().task_id == "medium-task"
    assert queue.pop_task().task_id == "low-task"


def test_same_priority_uses_fifo_order():
    queue = TaskPriorityQueue()

    task1 = Task("task-1")
    task2 = Task("task-2")
    task3 = Task("task-3")

    queue.add_task(task1, "HIGH")
    queue.add_task(task2, "HIGH")
    queue.add_task(task3, "HIGH")

    assert queue.pop_task().task_id == "task-1"
    assert queue.pop_task().task_id == "task-2"
    assert queue.pop_task().task_id == "task-3"


def test_duplicate_task_is_rejected():
    queue = TaskPriorityQueue()

    task = Task("task-1")

    assert queue.add_task(task, "HIGH") is True
    assert queue.add_task(task, "LOW") is False
    assert queue.size() == 1


def test_invalid_priority_is_rejected():
    queue = TaskPriorityQueue()

    task = Task("task-1")

    assert queue.add_task(task, "URGENT") is False
    assert queue.size() == 0


def test_get_next_task_does_not_remove_task():
    queue = TaskPriorityQueue()

    task = Task("task-1")

    queue.add_task(task, "HIGH")

    next_task = queue.get_next_task()

    assert next_task is not None
    assert next_task.task_id == "task-1"
    assert queue.size() == 1


def test_remove_task():
    queue = TaskPriorityQueue()

    task1 = Task("task-1")
    task2 = Task("task-2")

    queue.add_task(task1, "HIGH")
    queue.add_task(task2, "LOW")

    assert queue.remove_task("task-1") is True
    assert queue.contains("task-1") is False
    assert queue.size() == 1
    assert queue.get_next_task().task_id == "task-2"


def test_remove_unknown_task():
    queue = TaskPriorityQueue()

    assert queue.remove_task("unknown") is False


def test_empty_queue():
    queue = TaskPriorityQueue()

    assert queue.is_empty() is True
    assert queue.size() == 0
    assert queue.get_next_task() is None
    assert queue.pop_task() is None


def test_clear_queue():
    queue = TaskPriorityQueue()

    queue.add_task(Task("task-1"), "HIGH")
    queue.add_task(Task("task-2"), "LOW")

    queue.clear()

    assert queue.is_empty() is True
    assert queue.size() == 0
    assert queue.contains("task-1") is False
    assert queue.contains("task-2") is False


def test_priority_is_case_insensitive():
    queue = TaskPriorityQueue()

    high_task = Task("high-task")

    assert queue.add_task(high_task, "high") is True
    assert queue.pop_task().task_id == "high-task"


def test_get_priority_rejects_invalid_priority():
    queue = TaskPriorityQueue()

    try:
        queue.get_priority("URGENT")
        assert False
    except ValueError:
        assert True


def test_len_returns_queue_size():
    queue = TaskPriorityQueue()

    assert len(queue) == 0

    queue.add_task(Task("task-1"), "HIGH")
    queue.add_task(Task("task-2"), "LOW")

    assert len(queue) == 2


def test_set_priority_changes_task_priority():
    queue = TaskPriorityQueue()

    low_task = Task("low-task")
    high_task = Task("high-task")

    queue.add_task(low_task, "LOW")
    queue.add_task(high_task, "HIGH")

    assert queue.set_priority("low-task", "HIGH") is True
    assert queue.pop_task().task_id == "low-task"


def test_set_priority_invalid_priority():
    queue = TaskPriorityQueue()

    task = Task("task-1")
    queue.add_task(task, "LOW")

    assert queue.set_priority("task-1", "URGENT") is False
    assert queue.get_task_priority("task-1") == "LOW"


def test_set_priority_unknown_task():
    queue = TaskPriorityQueue()

    assert queue.set_priority("unknown", "HIGH") is False


def test_get_task_priority():
    queue = TaskPriorityQueue()

    high_task = Task("high-task")
    low_task = Task("low-task")

    queue.add_task(high_task, "HIGH")
    queue.add_task(low_task, "LOW")

    assert queue.get_task_priority("high-task") == "HIGH"
    assert queue.get_task_priority("low-task") == "LOW"
    assert queue.get_task_priority("unknown") is None


def test_peek_task_returns_highest_priority_without_removing():
    queue = TaskPriorityQueue()

    low_task = Task("low-task")
    high_task = Task("high-task")

    queue.add_task(low_task, "LOW")
    queue.add_task(high_task, "HIGH")

    peeked = queue.peek_task()

    assert peeked is not None
    assert peeked.task_id == "high-task"
    assert queue.size() == 2


def test_peek_task_returns_none_for_empty_queue():
    queue = TaskPriorityQueue()

    assert queue.peek_task() is None