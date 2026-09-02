from meshweaver.router import Task
from meshweaver.task_priority import TaskPriorityQueue


def test_high_priority_before_medium_and_low():
    queue = TaskPriorityQueue()

    queue.add_task(Task(task_id="low"), "LOW")
    queue.add_task(Task(task_id="medium"), "MEDIUM")
    queue.add_task(Task(task_id="high"), "HIGH")

    assert queue.pop_task().task_id == "high"
    assert queue.pop_task().task_id == "medium"
    assert queue.pop_task().task_id == "low"


def test_same_priority_follows_fifo():
    queue = TaskPriorityQueue()

    queue.add_task(Task(task_id="high-1"), "HIGH")
    queue.add_task(Task(task_id="high-2"), "HIGH")
    queue.add_task(Task(task_id="high-3"), "HIGH")

    assert queue.pop_task().task_id == "high-1"
    assert queue.pop_task().task_id == "high-2"
    assert queue.pop_task().task_id == "high-3"


def test_default_priority_is_medium():
    queue = TaskPriorityQueue()

    queue.add_task(Task(task_id="task-1"))

    assert queue.get_task_priority("task-1") == "MEDIUM"


def test_duplicate_task_is_rejected():
    queue = TaskPriorityQueue()

    task = Task(task_id="task-1")

    assert queue.add_task(task, "HIGH") is True
    assert queue.add_task(task, "LOW") is False
    assert queue.size() == 1


def test_duplicate_task_id_is_rejected():
    queue = TaskPriorityQueue()

    assert queue.add_task(Task(task_id="task-1"), "HIGH") is True
    assert queue.add_task(Task(task_id="task-1"), "MEDIUM") is False


def test_invalid_priority_is_rejected():
    queue = TaskPriorityQueue()

    assert queue.add_task(
        Task(task_id="task-1"),
        "INVALID",
    ) is False

    assert queue.is_empty()


def test_priority_is_case_insensitive():
    queue = TaskPriorityQueue()

    assert queue.add_task(
        Task(task_id="task-1"),
        "high",
    ) is True

    assert queue.get_task_priority("task-1") == "HIGH"


def test_get_next_task_does_not_remove_task():
    queue = TaskPriorityQueue()

    queue.add_task(
        Task(task_id="task-1"),
        "HIGH",
    )

    task = queue.get_next_task()

    assert task.task_id == "task-1"
    assert queue.size() == 1


def test_peek_task_does_not_remove_task():
    queue = TaskPriorityQueue()

    queue.add_task(
        Task(task_id="task-1"),
        "HIGH",
    )

    task = queue.peek_task()

    assert task.task_id == "task-1"
    assert queue.size() == 1


def test_empty_queue_returns_none():
    queue = TaskPriorityQueue()

    assert queue.get_next_task() is None
    assert queue.peek_task() is None
    assert queue.pop_task() is None


def test_remove_task():
    queue = TaskPriorityQueue()

    queue.add_task(Task(task_id="task-1"), "HIGH")
    queue.add_task(Task(task_id="task-2"), "MEDIUM")

    assert queue.remove_task("task-1") is True
    assert queue.contains("task-1") is False
    assert queue.size() == 1


def test_remove_unknown_task():
    queue = TaskPriorityQueue()

    assert queue.remove_task("unknown") is False


def test_contains_task():
    queue = TaskPriorityQueue()

    queue.add_task(
        Task(task_id="task-1"),
        "HIGH",
    )

    assert queue.contains("task-1") is True
    assert queue.contains("unknown") is False


def test_clear_queue():
    queue = TaskPriorityQueue()

    queue.add_task(Task(task_id="task-1"), "HIGH")
    queue.add_task(Task(task_id="task-2"), "LOW")

    queue.clear()

    assert queue.is_empty()
    assert queue.size() == 0
    assert queue.contains("task-1") is False


def test_queue_length():
    queue = TaskPriorityQueue()

    assert len(queue) == 0

    queue.add_task(Task(task_id="task-1"), "HIGH")
    queue.add_task(Task(task_id="task-2"), "LOW")

    assert len(queue) == 2


def test_get_priority():
    queue = TaskPriorityQueue()

    assert queue.get_priority("HIGH") == 0
    assert queue.get_priority("MEDIUM") == 1
    assert queue.get_priority("LOW") == 2


def test_get_priority_case_insensitive():
    queue = TaskPriorityQueue()

    assert queue.get_priority("high") == 0
    assert queue.get_priority("medium") == 1
    assert queue.get_priority("low") == 2


def test_get_priority_invalid_raises_error():
    queue = TaskPriorityQueue()

    try:
        queue.get_priority("INVALID")
        assert False
    except ValueError:
        assert True


def test_set_priority_changes_task_priority():
    queue = TaskPriorityQueue()

    queue.add_task(Task(task_id="low-task"), "LOW")
    queue.add_task(Task(task_id="high-task"), "HIGH")

    assert queue.set_priority("low-task", "HIGH") is True

    assert queue.get_task_priority("low-task") == "HIGH"

    assert queue.pop_task().task_id == "low-task"


def test_set_priority_invalid_priority():
    queue = TaskPriorityQueue()

    queue.add_task(Task(task_id="task-1"), "MEDIUM")

    assert queue.set_priority(
        "task-1",
        "INVALID",
    ) is False

    assert queue.get_task_priority("task-1") == "MEDIUM"


def test_set_priority_unknown_task():
    queue = TaskPriorityQueue()

    assert queue.set_priority(
        "unknown",
        "HIGH",
    ) is False


def test_get_task_priority_unknown_task():
    queue = TaskPriorityQueue()

    assert queue.get_task_priority("unknown") is None


def test_remove_by_priority():
    queue = TaskPriorityQueue()

    queue.add_task(Task(task_id="high-1"), "HIGH")
    queue.add_task(Task(task_id="high-2"), "HIGH")
    queue.add_task(Task(task_id="low-1"), "LOW")

    removed = queue.remove_by_priority("HIGH")

    assert removed == 2
    assert queue.size() == 1
    assert queue.contains("high-1") is False
    assert queue.contains("high-2") is False


def test_remove_by_priority_case_insensitive():
    queue = TaskPriorityQueue()

    queue.add_task(
        Task(task_id="task-1"),
        "HIGH",
    )

    assert queue.remove_by_priority("high") == 1
    assert queue.is_empty()


def test_remove_by_invalid_priority():
    queue = TaskPriorityQueue()

    queue.add_task(
        Task(task_id="task-1"),
        "HIGH",
    )

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
    queue.add_task(Task(task_id="task-2"), "MEDIUM")
    queue.add_task(Task(task_id="task-3"), "LOW")

    task_ids = queue.get_task_ids()

    assert set(task_ids) == {
        "task-1",
        "task-2",
        "task-3",
    }


def test_get_tasks_by_priority():
    queue = TaskPriorityQueue()

    high_task = Task(task_id="high-1")
    low_task = Task(task_id="low-1")

    queue.add_task(high_task, "HIGH")
    queue.add_task(low_task, "LOW")

    high_tasks = queue.get_tasks_by_priority("HIGH")

    assert len(high_tasks) == 1
    assert high_tasks[0].task_id == "high-1"


def test_get_tasks_by_priority_invalid():
    queue = TaskPriorityQueue()

    assert queue.get_tasks_by_priority("INVALID") == []


def test_has_priority():
    queue = TaskPriorityQueue()

    queue.add_task(
        Task(task_id="high-1"),
        "HIGH",
    )

    assert queue.has_priority("HIGH") is True
    assert queue.has_priority("LOW") is False


def test_has_priority_case_insensitive():
    queue = TaskPriorityQueue()

    queue.add_task(
        Task(task_id="high-1"),
        "HIGH",
    )

    assert queue.has_priority("high") is True


def test_has_priority_invalid():
    queue = TaskPriorityQueue()

    assert queue.has_priority("INVALID") is False


# ---------------------------------------------------------
# Priority Summary Tests
# ---------------------------------------------------------


def test_priority_summary_empty_queue():
    queue = TaskPriorityQueue()

    assert queue.priority_summary() == {
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0,
    }


def test_priority_summary_counts_tasks():
    queue = TaskPriorityQueue()

    queue.add_task(
        Task(task_id="high-1"),
        "HIGH",
    )

    queue.add_task(
        Task(task_id="high-2"),
        "HIGH",
    )

    queue.add_task(
        Task(task_id="medium-1"),
        "MEDIUM",
    )

    queue.add_task(
        Task(task_id="low-1"),
        "LOW",
    )

    assert queue.priority_summary() == {
        "HIGH": 2,
        "MEDIUM": 1,
        "LOW": 1,
    }


def test_priority_summary_updates_after_removal():
    queue = TaskPriorityQueue()

    queue.add_task(
        Task(task_id="high-1"),
        "HIGH",
    )

    queue.add_task(
        Task(task_id="medium-1"),
        "MEDIUM",
    )

    queue.add_task(
        Task(task_id="low-1"),
        "LOW",
    )

    queue.remove_task("high-1")

    assert queue.priority_summary() == {
        "HIGH": 0,
        "MEDIUM": 1,
        "LOW": 1,
    }


# ---------------------------------------------------------
# Priority Update Tests - Commit #15
# ---------------------------------------------------------


def test_update_priority_changes_task_priority():
    queue = TaskPriorityQueue()

    queue.add_task(
        Task(task_id="task-1"),
        "LOW",
    )

    assert queue.update_priority(
        "task-1",
        "HIGH",
    ) is True

    assert queue.get_task_priority("task-1") == "HIGH"


def test_update_priority_unknown_task():
    queue = TaskPriorityQueue()

    assert queue.update_priority(
        "unknown",
        "HIGH",
    ) is False


def test_update_priority_invalid_priority():
    queue = TaskPriorityQueue()

    queue.add_task(
        Task(task_id="task-1"),
        "MEDIUM",
    )

    assert queue.update_priority(
        "task-1",
        "INVALID",
    ) is False

    assert queue.get_task_priority("task-1") == "MEDIUM"