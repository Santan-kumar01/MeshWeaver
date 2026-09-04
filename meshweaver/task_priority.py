from heapq import heappop, heappush, heapify
from itertools import count
from typing import Optional

from meshweaver.router import Task


class TaskPriorityQueue:
    """Priority queue for MeshWeaver tasks."""

    HIGH = 0
    MEDIUM = 1
    LOW = 2

    PRIORITY_LEVELS = {
        "HIGH": HIGH,
        "MEDIUM": MEDIUM,
        "LOW": LOW,
    }

    def __init__(self):
        self._queue = []
        self._counter = count()

    def _validate_priority(self, priority: str):
        """Validate and normalize task priority."""
        if not isinstance(priority, str):
            return None

        priority = priority.upper()

        if priority not in self.PRIORITY_LEVELS:
            return None

        return priority

    def add_task(self, task: Task, priority: str = "MEDIUM") -> bool:
        """Add a task to the queue."""
        if self.contains(task.task_id):
            return False

        priority = self._validate_priority(priority)

        if priority is None:
            return False

        level = self.PRIORITY_LEVELS[priority]
        sequence = next(self._counter)

        heappush(self._queue, (level, sequence, task))

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

        return heappop(self._queue)[2]

    def remove_task(self, task_id: str) -> bool:
        """Remove a task by task ID."""
        for index, item in enumerate(self._queue):
            if item[2].task_id == task_id:
                self._queue.pop(index)
                heapify(self._queue)
                return True

        return False

    def contains(self, task_id: str) -> bool:
        """Return True if the task exists."""
        return any(
            item[2].task_id == task_id
            for item in self._queue
        )

    def is_empty(self) -> bool:
        """Return True if the queue is empty."""
        return len(self._queue) == 0

    def size(self) -> int:
        """Return the number of tasks."""
        return len(self._queue)

    def clear(self):
        """Remove all tasks from the queue."""
        self._queue.clear()

    def get_priority(self, priority: str) -> int:
        """Return the numeric priority level."""
        priority = self._validate_priority(priority)

        if priority is None:
            raise ValueError("Invalid priority")

        return self.PRIORITY_LEVELS[priority]

    def __len__(self):
        """Return the number of tasks."""
        return len(self._queue)

    def set_priority(self, task_id: str, priority: str) -> bool:
        """Change the priority of a task."""
        priority = self._validate_priority(priority)

        if priority is None:
            return False

        for index, item in enumerate(self._queue):
            if item[2].task_id == task_id:
                _, sequence, task = self._queue.pop(index)

                heapify(self._queue)

                new_level = self.PRIORITY_LEVELS[priority]

                heappush(
                    self._queue,
                    (new_level, sequence, task)
                )

                return True

        return False

    def update_priority(self, task_id: str, priority: str) -> bool:
        """Update the priority of a task."""
        return self.set_priority(task_id, priority)

    def get_task_priority(self, task_id: str) -> Optional[str]:
        """Return the priority name of a task."""
        for level, _, task in self._queue:
            if task.task_id == task_id:
                for name, value in self.PRIORITY_LEVELS.items():
                    if value == level:
                        return name

        return None

    def peek_task(self) -> Optional[Task]:
        """Return the highest-priority task without removing it."""
        return self.get_next_task()

    def remove_by_priority(self, priority: str) -> int:
        """Remove all tasks with the given priority."""
        priority = self._validate_priority(priority)

        if priority is None:
            return 0

        level = self.PRIORITY_LEVELS[priority]

        original_size = len(self._queue)

        self._queue = [
            item
            for item in self._queue
            if item[0] != level
        ]

        heapify(self._queue)

        return original_size - len(self._queue)

    def count_by_priority(self, priority: str) -> int:
        """Count tasks with the given priority."""
        priority = self._validate_priority(priority)

        if priority is None:
            return 0

        level = self.PRIORITY_LEVELS[priority]

        return sum(
            1
            for item in self._queue
            if item[0] == level
        )

    def get_task_ids(self):
        """Return all task IDs."""
        return [
            item[2].task_id
            for item in self._queue
        ]

    def get_tasks_by_priority(self, priority: str):
        """Return tasks with the given priority."""
        priority = self._validate_priority(priority)

        if priority is None:
            return []

        level = self.PRIORITY_LEVELS[priority]

        return [
            item[2]
            for item in self._queue
            if item[0] == level
        ]

    def has_priority(self, priority: str) -> bool:
        """Return True if at least one task has the priority."""
        priority = self._validate_priority(priority)

        if priority is None:
            return False

        level = self.PRIORITY_LEVELS[priority]

        return any(
            item[0] == level
            for item in self._queue
        )

    def priority_summary(self):
        """Return task counts grouped by priority."""
        return {
            "HIGH": self.count_by_priority("HIGH"),
            "MEDIUM": self.count_by_priority("MEDIUM"),
            "LOW": self.count_by_priority("LOW"),
        }

    def get_highest_priority(self):
        """Return the highest priority currently present."""
        if not self._queue:
            return None

        highest_level = min(
            item[0]
            for item in self._queue
        )

        for name, value in self.PRIORITY_LEVELS.items():
            if value == highest_level:
                return name

        return None

    def get_lowest_priority(self):
        """Return the lowest priority currently present."""
        if not self._queue:
            return None

        lowest_level = max(
            item[0]
            for item in self._queue
        )

        for name, value in self.PRIORITY_LEVELS.items():
            if value == lowest_level:
                return name

        return None

    def get_priority_tasks(self):
        """Return task IDs grouped by priority."""
        return {
            "HIGH": [
                task.task_id
                for task in self.get_tasks_by_priority("HIGH")
            ],
            "MEDIUM": [
                task.task_id
                for task in self.get_tasks_by_priority("MEDIUM")
            ],
            "LOW": [
                task.task_id
                for task in self.get_tasks_by_priority("LOW")
            ],
        }

    def get_tasks_in_priority_order(self):
        """Return all queued tasks ordered from highest to lowest priority."""
        return [
            item[2]
            for item in sorted(
                self._queue,
                key=lambda item: (item[0], item[1])
            )
        ]