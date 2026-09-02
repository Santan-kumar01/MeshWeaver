from heapq import heappop, heappush, heapify
from itertools import count
from typing import Optional

from meshweaver.router import Task


class TaskPriorityQueue:
    """Priority queue for MeshWeaver tasks.

    Higher-priority tasks are selected first.
    Tasks with the same priority follow FIFO ordering.
    """

    PRIORITY_LEVELS = {
        "HIGH": 0,
        "MEDIUM": 1,
        "LOW": 2,
    }

    def __init__(self):
        self._queue = []
        self._task_ids = set()
        self._counter = count()

    def _validate_priority(self, priority: str) -> str:
        """Validate and normalize a priority value."""

        priority = priority.upper()

        if priority not in self.PRIORITY_LEVELS:
            raise ValueError(
                f"Invalid priority: {priority}. "
                f"Expected HIGH, MEDIUM, or LOW."
            )

        return priority

    def add_task(self, task: Task, priority: str = "MEDIUM") -> bool:
        """Add a task with HIGH, MEDIUM, or LOW priority."""

        priority = priority.upper()

        if priority not in self.PRIORITY_LEVELS:
            return False

        if task.task_id in self._task_ids:
            return False

        priority_level = self.PRIORITY_LEVELS[priority]
        sequence = next(self._counter)

        heappush(
            self._queue,
            (priority_level, sequence, task),
        )

        self._task_ids.add(task.task_id)

        return True

    def get_next_task(self) -> Optional[Task]:
        """Return the highest-priority task without removing it."""

        if not self._queue:
            return None

        return self._queue[0][2]

    def pop_task(self) -> Optional[Task]:
        """Remove and return the highest-priority task."""

        if not self._queue:
            return None

        _, _, task = heappop(self._queue)

        self._task_ids.discard(task.task_id)

        return task

    def remove_task(self, task_id: str) -> bool:
        """Remove a task by its ID."""

        for index, (_, _, task) in enumerate(self._queue):
            if task.task_id == task_id:
                self._queue.pop(index)
                heapify(self._queue)

                self._task_ids.discard(task_id)

                return True

        return False

    def contains(self, task_id: str) -> bool:
        """Return True if the task exists in the queue."""

        return task_id in self._task_ids

    def is_empty(self) -> bool:
        """Return whether the queue is empty."""

        return len(self._queue) == 0

    def size(self) -> int:
        """Return the number of tasks in the queue."""

        return len(self._queue)

    def clear(self) -> None:
        """Remove all tasks from the queue."""

        self._queue.clear()
        self._task_ids.clear()

    def get_priority(self, priority: str) -> int:
        """Return the internal priority value."""

        priority = self._validate_priority(priority)

        return self.PRIORITY_LEVELS[priority]

    def __len__(self) -> int:
        """Return the number of tasks in the queue."""

        return len(self._queue)

    def set_priority(self, task_id: str, priority: str) -> bool:
        """Change the priority of an existing task."""

        priority = priority.upper()

        if priority not in self.PRIORITY_LEVELS:
            return False

        for index, (_, sequence, task) in enumerate(self._queue):
            if task.task_id == task_id:
                self._queue.pop(index)

                priority_level = self.PRIORITY_LEVELS[priority]

                heappush(
                    self._queue,
                    (priority_level, sequence, task),
                )

                return True

        return False

    def update_priority(self, task_id: str, priority: str) -> bool:
        """Update the priority of an existing task.

        Returns True when the task exists and the priority is updated.
        Returns False when the task does not exist or the priority is invalid.
        """

        return self.set_priority(task_id, priority)

    def get_task_priority(self, task_id: str) -> Optional[str]:
        """Return the priority of a task by its ID."""

        for priority_level, _, task in self._queue:
            if task.task_id == task_id:
                for priority, level in self.PRIORITY_LEVELS.items():
                    if level == priority_level:
                        return priority

        return None

    def peek_task(self) -> Optional[Task]:
        """Return the highest-priority task without removing it."""

        if not self._queue:
            return None

        return self._queue[0][2]

    def remove_by_priority(self, priority: str) -> int:
        """Remove all tasks with the given priority.

        Returns the number of tasks removed.
        """

        priority = priority.upper()

        if priority not in self.PRIORITY_LEVELS:
            return 0

        priority_level = self.PRIORITY_LEVELS[priority]

        remaining_tasks = []
        removed_count = 0

        for item in self._queue:
            if item[0] == priority_level:
                removed_count += 1
                self._task_ids.discard(item[2].task_id)
            else:
                remaining_tasks.append(item)

        self._queue = remaining_tasks
        heapify(self._queue)

        return removed_count

    def count_by_priority(self, priority: str) -> int:
        """Return the number of tasks with the given priority."""

        priority = priority.upper()

        if priority not in self.PRIORITY_LEVELS:
            return 0

        priority_level = self.PRIORITY_LEVELS[priority]

        return sum(
            1
            for item in self._queue
            if item[0] == priority_level
        )

    def get_task_ids(self):
        """Return all task IDs currently in the queue."""

        return [item[2].task_id for item in self._queue]

    def get_tasks_by_priority(self, priority: str):
        """Return all tasks with the given priority."""

        priority = priority.upper()

        if priority not in self.PRIORITY_LEVELS:
            return []

        priority_level = self.PRIORITY_LEVELS[priority]

        return [
            item[2]
            for item in self._queue
            if item[0] == priority_level
        ]

    def has_priority(self, priority: str) -> bool:
        """Return True if at least one task has the given priority."""

        priority = priority.upper()

        if priority not in self.PRIORITY_LEVELS:
            return False

        priority_level = self.PRIORITY_LEVELS[priority]

        return any(
            item[0] == priority_level
            for item in self._queue
        )

    def priority_summary(self):
        """Return the number of queued tasks for each priority."""

        return {
            "HIGH": self.count_by_priority("HIGH"),
            "MEDIUM": self.count_by_priority("MEDIUM"),
            "LOW": self.count_by_priority("LOW"),
        }

    def get_highest_priority(self) -> Optional[str]:
        """Return the highest priority currently in the queue.

        Returns None when the queue is empty.
        """

        if self.has_priority("HIGH"):
            return "HIGH"

        if self.has_priority("MEDIUM"):
            return "MEDIUM"

        if self.has_priority("LOW"):
            return "LOW"

        return None