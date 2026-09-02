from meshweaver.router import Task
from meshweaver.task_priority import TaskPriorityQueue


def test_add_task():
    queue = TaskPriorityQueue()

    task = Task(task_id="task-1")

    assert queue.add_task(task, "HIGH") is True
    assert queue.size() == 1
    assert queue.contains("task-1") is True


def test_add_duplicate_task():
    queue = TaskPriorityQueue()

    task = Task(task_id="task-1")

    assert queue.add_task(task, "HIGH") is True
    assert queue.add_task(task, "LOW") is False
    assert queue.size() == 1


def test_add_invalid_priority():
    queue = TaskPriorityQueue()

    task = Task(task_id="task-1")

    assert queue.add_task(task, "INVALID") is False
    assert queue.size() == 0


def test_default_priority():
    queue = TaskPriorityQueue()

    task = Task(task_id="task-1")

    assert queue.add_task(task) is True
    assert queue.get_task_priority("task-1") == "MEDIUM"


def test_priority_order():
    queue = TaskPriorityQueue()

    low = Task(task_id="low")
    medium = Task(task_id="medium")
    high = Task(task_id="high")

    queue.add_task(low, "LOW")
    queue.add_task(medium, "MEDIUM")
    queue.add_task(high, "HIGH")

    assert queue.pop_task().task_id == "high"
    assert queue.pop_task().task_id == "medium"
    assert queue.pop_task().task_id == "low"


def test_same_priority_fifo():
    queue = TaskPriorityQueue()

    task1 = Task(task_id="task-1")
    task2 = Task(task_id="task-2")
    task3 = Task(task_id="task-3")

    queue.add_task(task1, "HIGH")
    queue.add_task(task2, "HIGH")
    queue.add_task(task3, "HIGH")

    assert queue.pop_task().task_id == "task-1"
    assert queue.pop_task().task_id == "task-2"
    assert queue.pop_task().task_id == "task-3"


def test_get_next_task():
    queue = TaskPriorityQueue()

    task = Task(task_id="task-1")

    queue.add_task(task, "HIGH")

    result = queue.get_next_task()

    assert result.task_id == "task-1"
    assert queue.size() == 1


def test_pop_empty_queue():
    queue = TaskPriorityQueue()

    assert queue.pop_task() is None


def test_get_next_task_empty_queue():
    queue = TaskPriorityQueue()

    assert queue.get_next_task() is None


def test_remove_task():
    queue = TaskPriorityQueue()

    task = Task(task_id="task-1")

    queue.add_task(task, "HIGH")

    assert queue.remove_task("task-1") is True
    assert queue.contains("task-1") is False
    assert queue.size() == 0


def test_remove_nonexistent_task():
    queue = TaskPriorityQueue()

    assert queue.remove_task("missing") is False


def test_contains_task():
    queue = TaskPriorityQueue()

    task = Task(task_id="task-1")

    queue.add_task(task, "HIGH")

    assert queue.contains("task-1") is True
    assert queue.contains("missing") is False


def test_is_empty():
    queue = TaskPriorityQueue()

    assert queue.is_empty() is True

    queue.add_task(Task(task_id="task-1"), "HIGH")

    assert queue.is_empty() is False


def test_size():
    queue = TaskPriorityQueue()

    assert queue.size() == 0

    queue.add_task(Task(task_id="task-1"), "HIGH")
    queue.add_task(Task(task_id="task-2"), "LOW")

    assert queue.size() == 2


def test_len():
    queue = TaskPriorityQueue()

    assert len(queue) == 0

    queue.add_task(Task(task_id="task-1"), "HIGH")

    assert len(queue) == 1


def test_clear():
    queue = TaskPriorityQueue()

    queue.add_task(Task(task_id="task-1"), "HIGH")
    queue.add_task(Task(task_id="task-2"), "LOW")

    queue.clear()

    assert queue.is_empty() is True
    assert queue.size() == 0


def test_get_priority_high():
    queue = TaskPriorityQueue()

    assert queue.get_priority("HIGH") == 0


def test_get_priority_medium():
    queue = TaskPriorityQueue()

    assert queue.get_priority("MEDIUM") == 1


def test_get_priority_low():
    queue = TaskPriorityQueue()

    assert queue.get_priority("LOW") == 2


def test_get_priority_case_insensitive():
    queue = TaskPriorityQueue()

    assert queue.get_priority("high") == 0
    assert queue.get_priority("medium") == 1
    assert queue.get_priority("low") == 2


def test_get_priority_invalid():
    queue = TaskPriorityQueue()

    try:
        queue.get_priority("INVALID")
        assert False
    except ValueError:
        assert True


def test_set_priority():
    queue = TaskPriorityQueue()

    task = Task(task_id="task-1")

    queue.add_task(task, "LOW")

    assert queue.set_priority("task-1", "HIGH") is True
    assert queue.get_task_priority("task-1") == "HIGH"


def test_set_priority_invalid():
    queue = TaskPriorityQueue()

    task = Task(task_id="task-1")

    queue.add_task(task, "LOW")

    assert queue.set_priority("task-1", "INVALID") is False
    assert queue.get_task_priority("task-1") == "LOW"


def test_set_priority_nonexistent():
    queue = TaskPriorityQueue()

    assert queue.set_priority("missing", "HIGH") is False


def test_set_priority_changes_order():
    queue = TaskPriorityQueue()

    low = Task(task_id="low")
    high = Task(task_id="high")

    queue.add_task(low, "LOW")
    queue.add_task(high, "HIGH")

    assert queue.set_priority("low", "HIGH") is True

    assert queue.pop_task().task_id == "low"
    assert queue.pop_task().task_id == "high"


def test_update_priority():
    queue = TaskPriorityQueue()

    task = Task(task_id="task-1")

    queue.add_task(task, "LOW")

    assert queue.update_priority("task-1", "HIGH") is True
    assert queue.get_task_priority("task-1") == "HIGH"


def test_update_priority_invalid():
    queue = TaskPriorityQueue()

    task = Task(task_id="task-1")

    queue.add_task(task, "MEDIUM")

    assert queue.update_priority("task-1", "INVALID") is False
    assert queue.get_task_priority("task-1") == "MEDIUM"


def test_update_priority_nonexistent():
    queue = TaskPriorityQueue()

    assert queue.update_priority("missing", "HIGH") is False


def test_get_task_priority():
    queue = TaskPriorityQueue()

    task = Task(task_id="task-1")

    queue.add_task(task, "HIGH")

    assert queue.get_task_priority("task-1") == "HIGH"


def test_get_task_priority_missing():
    queue = TaskPriorityQueue()

    assert queue.get_task_priority("missing") is None


def test_peek_task():
    queue = TaskPriorityQueue()

    low = Task(task_id="low")
    high = Task(task_id="high")

    queue.add_task(low, "LOW")
    queue.add_task(high, "HIGH")

    result = queue.peek_task()

    assert result.task_id == "high"
    assert queue.size() == 2


def test_peek_empty_queue():
    queue = TaskPriorityQueue()

    assert queue.peek_task() is None


def test_remove_by_priority():
    queue = TaskPriorityQueue()

    queue.add_task(Task(task_id="high-1"), "HIGH")
    queue.add_task(Task(task_id="high-2"), "HIGH")
    queue.add_task(Task(task_id="low-1"), "LOW")

    removed = queue.remove_by_priority("HIGH")

    assert removed == 2
    assert queue.size() == 1
    assert queue.contains("low-1") is True


def test_remove_by_priority_invalid():
    queue = TaskPriorityQueue()

    queue.add_task(Task(task_id="task-1"), "HIGH")

    assert queue.remove_by_priority("INVALID") == 0
    assert queue.size() == 1


def test_count_by_priority():
    queue = TaskPriorityQueue()

    queue.add_task(Task(task_id="high-1"), "HIGH")
    queue.add_task(Task(task_id="high-2"), "HIGH")
    queue.add_task(Task(task_id="medium-1"), "MEDIUM")
    queue.add_task(Task(task_id="low-1"), "LOW")

    assert queue.count_by_priority("HIGH") == 2
    assert queue.count_by_priority("MEDIUM") == 1
    assert queue.count_by_priority("LOW") == 1


def test_count_by_priority_invalid():
    queue = TaskPriorityQueue()

    assert queue.count_by_priority("INVALID") == 0


def test_get_task_ids():
    queue = TaskPriorityQueue()

    queue.add_task(Task(task_id="task-1"), "HIGH")
    queue.add_task(Task(task_id="task-2"), "LOW")

    task_ids = queue.get_task_ids()

    assert "task-1" in task_ids
    assert "task-2" in task_ids


def test_get_tasks_by_priority():
    queue = TaskPriorityQueue()

    high = Task(task_id="high-1")
    low = Task(task_id="low-1")

    queue.add_task(high, "HIGH")
    queue.add_task(low, "LOW")

    high_tasks = queue.get_tasks_by_priority("HIGH")

    assert len(high_tasks) == 1
    assert high_tasks[0].task_id == "high-1"


def test_get_tasks_by_priority_invalid():
    queue = TaskPriorityQueue()

    assert queue.get_tasks_by_priority("INVALID") == []


def test_has_priority():
    queue = TaskPriorityQueue()

    queue.add_task(Task(task_id="task-1"), "HIGH")

    assert queue.has_priority("HIGH") is True
    assert queue.has_priority("LOW") is False


def test_has_priority_invalid():
    queue = TaskPriorityQueue()

    assert queue.has_priority("INVALID") is False


def test_priority_summary():
    queue = TaskPriorityQueue()

    queue.add_task(Task(task_id="high-1"), "HIGH")
    queue.add_task(Task(task_id="high-2"), "HIGH")
    queue.add_task(Task(task_id="medium-1"), "MEDIUM")
    queue.add_task(Task(task_id="low-1"), "LOW")

    summary = queue.priority_summary()

    assert summary == {
        "HIGH": 2,
        "MEDIUM": 1,
        "LOW": 1,
    }


# Commit #16 tests

def test_get_highest_priority_returns_high():
    queue = TaskPriorityQueue()

    queue.add_task(Task(task_id="low-1"), "LOW")
    queue.add_task(Task(task_id="medium-1"), "MEDIUM")
    queue.add_task(Task(task_id="high-1"), "HIGH")

    assert queue.get_highest_priority() == "HIGH"


def test_get_highest_priority_returns_medium():
    queue = TaskPriorityQueue()

    queue.add_task(Task(task_id="low-1"), "LOW")
    queue.add_task(Task(task_id="medium-1"), "MEDIUM")

    assert queue.get_highest_priority() == "MEDIUM"


def test_get_highest_priority_returns_low():
    queue = TaskPriorityQueue()

    queue.add_task(Task(task_id="low-1"), "LOW")

    assert queue.get_highest_priority() == "LOW"


def test_get_highest_priority_empty_queue():
    queue = TaskPriorityQueue()

    assert queue.get_highest_priority() is None


def test_get_highest_priority_after_removing_high():
    queue = TaskPriorityQueue()

    queue.add_task(Task(task_id="high-1"), "HIGH")
    queue.add_task(Task(task_id="medium-1"), "MEDIUM")

    queue.remove_task("high-1")

    assert queue.get_highest_priority() == "MEDIUM"