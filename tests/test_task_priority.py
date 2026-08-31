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

    assert queue.pop_task().task_id == "high-task"
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

    queue.add_task(Task("high-task"), "HIGH")
    queue.add_task(Task("medium-task"), "MEDIUM")
    queue.add_task(Task("low-task"), "LOW")

    assert queue.get_task_priority("high-task") == "HIGH"
    assert queue.get_task_priority("medium-task") == "MEDIUM"
    assert queue.get_task_priority("low-task") == "LOW"
    assert queue.get_task_priority("unknown") is None


def test_peek_task_returns_highest_priority_without_removing():
    queue = TaskPriorityQueue()

    queue.add_task(Task("low-task"), "LOW")
    queue.add_task(Task("medium-task"), "MEDIUM")
    queue.add_task(Task("high-task"), "HIGH")

    task = queue.peek_task()

    assert task is not None
    assert task.task_id == "high-task"
    assert queue.size() == 3


def test_peek_task_returns_none_for_empty_queue():
    queue = TaskPriorityQueue()

    assert queue.peek_task() is None


def test_remove_by_priority():
    queue = TaskPriorityQueue()

    queue.add_task(Task("high-1"), "HIGH")
    queue.add_task(Task("high-2"), "HIGH")
    queue.add_task(Task("medium-1"), "MEDIUM")
    queue.add_task(Task("low-1"), "LOW")

    removed = queue.remove_by_priority("HIGH")

    assert removed == 2
    assert queue.contains("high-1") is False
    assert queue.contains("high-2") is False
    assert queue.contains("medium-1") is True
    assert queue.contains("low-1") is True
    assert queue.size() == 2


def test_remove_by_priority_is_case_insensitive():
    queue = TaskPriorityQueue()

    queue.add_task(Task("high-1"), "HIGH")
    queue.add_task(Task("medium-1"), "MEDIUM")

    removed = queue.remove_by_priority("high")

    assert removed == 1
    assert queue.contains("high-1") is False
    assert queue.contains("medium-1") is True


def test_remove_by_priority_invalid_priority():
    queue = TaskPriorityQueue()

    queue.add_task(Task("task-1"), "HIGH")

    removed = queue.remove_by_priority("URGENT")

    assert removed == 0
    assert queue.size() == 1


def test_validate_priority_accepts_valid_priority():
    queue = TaskPriorityQueue()

    assert queue._validate_priority("HIGH") == "HIGH"
    assert queue._validate_priority("medium") == "MEDIUM"
    assert queue._validate_priority("low") == "LOW"


def test_validate_priority_rejects_invalid_priority():
    queue = TaskPriorityQueue()

    try:
        queue._validate_priority("URGENT")
        assert False
    except ValueError:
        assert True


def test_count_by_priority():
    queue = TaskPriorityQueue()

    queue.add_task(Task("high-1"), "HIGH")
    queue.add_task(Task("high-2"), "HIGH")
    queue.add_task(Task("medium-1"), "MEDIUM")
    queue.add_task(Task("low-1"), "LOW")

    assert queue.count_by_priority("HIGH") == 2
    assert queue.count_by_priority("MEDIUM") == 1
    assert queue.count_by_priority("LOW") == 1


def test_count_by_priority_is_case_insensitive():
    queue = TaskPriorityQueue()

    queue.add_task(Task("high-1"), "HIGH")
    queue.add_task(Task("high-2"), "HIGH")

    assert queue.count_by_priority("high") == 2
    assert queue.count_by_priority("High") == 2


def test_count_by_priority_returns_zero_for_invalid_priority():
    queue = TaskPriorityQueue()

    queue.add_task(Task("task-1"), "HIGH")

    assert queue.count_by_priority("URGENT") == 0


def test_get_task_ids():
    queue = TaskPriorityQueue()

    queue.add_task(Task("task-1"), "HIGH")
    queue.add_task(Task("task-2"), "MEDIUM")
    queue.add_task(Task("task-3"), "LOW")

    task_ids = queue.get_task_ids()

    assert set(task_ids) == {
        "task-1",
        "task-2",
        "task-3",
    }


def test_get_task_ids_returns_empty_for_empty_queue():
    queue = TaskPriorityQueue()

    assert queue.get_task_ids() == []


def test_get_task_ids_after_removing_task():
    queue = TaskPriorityQueue()

    queue.add_task(Task("task-1"), "HIGH")
    queue.add_task(Task("task-2"), "LOW")

    queue.remove_task("task-1")

    assert queue.get_task_ids() == ["task-2"]


def test_get_tasks_by_priority():
    queue = TaskPriorityQueue()

    high1 = Task("high-1")
    high2 = Task("high-2")
    medium = Task("medium-1")
    low = Task("low-1")

    queue.add_task(high1, "HIGH")
    queue.add_task(high2, "HIGH")
    queue.add_task(medium, "MEDIUM")
    queue.add_task(low, "LOW")

    tasks = queue.get_tasks_by_priority("HIGH")

    assert [task.task_id for task in tasks] == [
        "high-1",
        "high-2",
    ]


def test_get_tasks_by_priority_is_case_insensitive():
    queue = TaskPriorityQueue()

    queue.add_task(Task("high-1"), "HIGH")

    tasks = queue.get_tasks_by_priority("high")

    assert len(tasks) == 1
    assert tasks[0].task_id == "high-1"


def test_get_tasks_by_priority_invalid_priority():
    queue = TaskPriorityQueue()

    queue.add_task(Task("task-1"), "HIGH")

    assert queue.get_tasks_by_priority("URGENT") == []