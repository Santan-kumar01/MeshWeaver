import pytest

from meshweaver.task_queue import TaskQueue


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def queue():
    """Return a fresh, empty TaskQueue for each test."""
    return TaskQueue()


# ---------------------------------------------------------------------------
# add_task
# ---------------------------------------------------------------------------

class TestAddTask:
    def test_add_single_task(self, queue):
        """A task can be added without raising an exception."""
        queue.add_task("task-1", {"action": "ping"})
        assert queue.size() == 1

    def test_add_multiple_tasks(self, queue):
        """Multiple distinct tasks can be added."""
        queue.add_task("task-1", {"action": "ping"})
        queue.add_task("task-2", {"action": "pong"})
        queue.add_task("task-3", {"action": "sync"})
        assert queue.size() == 3

    def test_add_task_with_none_payload(self, queue):
        """A task with a None payload is valid."""
        queue.add_task("task-null", None)
        assert queue.size() == 1

    def test_add_task_empty_id_raises(self, queue):
        """Adding a task with an empty string ID raises ValueError."""
        with pytest.raises(ValueError, match="Task ID cannot be empty"):
            queue.add_task("", {"action": "ping"})

    def test_add_duplicate_id_raises(self, queue):
        """Adding a task whose ID already exists raises ValueError."""
        queue.add_task("task-dup", {"action": "ping"})
        with pytest.raises(ValueError, match="already exists"):
            queue.add_task("task-dup", {"action": "pong"})

    def test_add_duplicate_does_not_corrupt_queue(self, queue):
        """A failed duplicate add must not change the queue state."""
        queue.add_task("task-1", {"action": "ping"})
        try:
            queue.add_task("task-1", {"action": "pong"})
        except ValueError:
            pass
        assert queue.size() == 1


# ---------------------------------------------------------------------------
# FIFO order
# ---------------------------------------------------------------------------

class TestFifoOrder:
    def test_tasks_returned_in_insertion_order(self, queue):
        """get_next_task always returns the oldest (first-in) task."""
        ids = ["alpha", "beta", "gamma", "delta"]
        for tid in ids:
            queue.add_task(tid, {"seq": tid})

        for expected_id in ids:
            result = queue.get_next_task()
            assert result is not None
            task_id, _ = result
            assert task_id == expected_id
            queue.remove_task(task_id)

    def test_fifo_after_removal_of_non_head(self, queue):
        """Removing a middle task does not disrupt FIFO for remaining tasks."""
        queue.add_task("first", 1)
        queue.add_task("second", 2)
        queue.add_task("third", 3)

        queue.remove_task("second")

        task_id, payload = queue.get_next_task()
        assert task_id == "first"
        assert payload == 1

        queue.remove_task("first")

        task_id, payload = queue.get_next_task()
        assert task_id == "third"
        assert payload == 3


# ---------------------------------------------------------------------------
# get_next_task
# ---------------------------------------------------------------------------

class TestGetNextTask:
    def test_get_next_task_returns_tuple(self, queue):
        """get_next_task returns a (task_id, task) tuple."""
        queue.add_task("t1", {"x": 1})
        result = queue.get_next_task()
        assert isinstance(result, tuple)
        task_id, task = result
        assert task_id == "t1"
        assert task == {"x": 1}

    def test_get_next_task_does_not_remove(self, queue):
        """get_next_task is non-destructive; the queue size is unchanged."""
        queue.add_task("t1", "payload")
        queue.get_next_task()
        assert queue.size() == 1

    def test_get_next_task_empty_queue_returns_none(self, queue):
        """get_next_task returns None when the queue is empty."""
        assert queue.get_next_task() is None


# ---------------------------------------------------------------------------
# remove_task
# ---------------------------------------------------------------------------

class TestRemoveTask:
    def test_remove_existing_task_returns_true(self, queue):
        """remove_task returns True when the task exists."""
        queue.add_task("task-rm", {"a": 1})
        assert queue.remove_task("task-rm") is True

    def test_remove_existing_task_decreases_size(self, queue):
        """Removing a task decreases the queue size by one."""
        queue.add_task("t1", 1)
        queue.add_task("t2", 2)
        queue.remove_task("t1")
        assert queue.size() == 1

    def test_remove_non_existing_task_returns_false(self, queue):
        """remove_task returns False when the task ID does not exist."""
        assert queue.remove_task("ghost") is False

    def test_remove_task_id_can_be_reused(self, queue):
        """After removal the same ID can be added again."""
        queue.add_task("reuse", "v1")
        queue.remove_task("reuse")
        queue.add_task("reuse", "v2")  # should not raise
        assert queue.size() == 1
        _, payload = queue.get_next_task()
        assert payload == "v2"

    def test_remove_all_tasks_empties_queue(self, queue):
        """Removing every task results in an empty queue."""
        ids = ["a", "b", "c"]
        for tid in ids:
            queue.add_task(tid, tid)
        for tid in ids:
            queue.remove_task(tid)
        assert queue.is_empty()


# ---------------------------------------------------------------------------
# size
# ---------------------------------------------------------------------------

class TestSize:
    def test_initial_size_is_zero(self, queue):
        assert queue.size() == 0

    def test_size_after_adds(self, queue):
        queue.add_task("t1", 1)
        queue.add_task("t2", 2)
        assert queue.size() == 2

    def test_size_after_remove(self, queue):
        queue.add_task("t1", 1)
        queue.add_task("t2", 2)
        queue.remove_task("t1")
        assert queue.size() == 1

    def test_size_consistency_with_is_empty(self, queue):
        """size() == 0 iff is_empty() is True."""
        assert (queue.size() == 0) == queue.is_empty()
        queue.add_task("x", None)
        assert (queue.size() == 0) == queue.is_empty()


# ---------------------------------------------------------------------------
# is_empty
# ---------------------------------------------------------------------------

class TestIsEmpty:
    def test_new_queue_is_empty(self, queue):
        assert queue.is_empty() is True

    def test_not_empty_after_add(self, queue):
        queue.add_task("t1", 1)
        assert queue.is_empty() is False

    def test_empty_after_removing_last_task(self, queue):
        queue.add_task("t1", 1)
        queue.remove_task("t1")
        assert queue.is_empty() is True

    def test_empty_queue_get_next_returns_none(self, queue):
        """Verifies safe handling of an empty queue across two methods."""
        assert queue.is_empty() is True
        assert queue.get_next_task() is None
