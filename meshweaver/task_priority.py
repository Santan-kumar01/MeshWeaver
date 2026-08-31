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

        priority = priority.upper()

        if priority not in self.PRIORITY_LEVELS:
            raise ValueError(
                f"Invalid priority: {priority}. "
                f"Expected HIGH, MEDIUM, or LOW."
            )

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

                # Keep the original sequence number so the task
                # maintains its original FIFO position.
                heappush(
                    self._queue,
                    (priority_level, sequence, task),
                )

                return True

        return False

    def get_task_priority(self, task_id: str) -> Optional[str]:
        """Return the priority of a task by its ID."""

        for priority_level, _, task in self._queue:
            if task.task_id == task_id:
                for priority, level in self.PRIORITY_LEVELS.items():
                    if level == priority_level:
                        return priority

        return None