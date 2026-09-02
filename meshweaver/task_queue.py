from collections import deque
from typing import Optional

from meshweaver.router import Task


class TaskQueue:
    """FIFO queue for managing MeshWeaver tasks."""

    def __init__(self):
        self._queue = deque()
        self._task_ids = set()

    def add_task(self, task: Task) -> bool:
        """Add a task to the queue.

        Returns False if the task is already present.
        """
        if task.task_id in self._task_ids:
            return False

        self._queue.append(task)
        self._task_ids.add(task.task_id)
        return True

    def get_next_task(self) -> Optional[Task]:
        """Return the next task without removing it."""
        if not self._queue:
            return None

        return self._queue[0]

    def pop_task(self) -> Optional[Task]:
        """Remove and return the next task."""
        if not self._queue:
            return None

        task = self._queue.popleft()
        self._task_ids.discard(task.task_id)

        return task

    def remove_task(self, task_id: str) -> bool:
        """Remove a task by its ID."""
        for task in self._queue:
            if task.task_id == task_id:
                self._queue.remove(task)
                self._task_ids.discard(task_id)
                return True

        return False

    def contains(self, task_id: str) -> bool:
        """Check whether a task exists in the queue."""
        return task_id in self._task_ids

    def is_empty(self) -> bool:
        """Return True if the queue is empty."""
        return len(self._queue) == 0

    def size(self) -> int:
        """Return the number of tasks in the queue."""
        return len(self._queue)

    def statistics(self) -> dict:
        """Return basic statistics about the task queue."""
        total_tasks = len(self._queue)

        return {
            "total_tasks": total_tasks,
            "queue_size": total_tasks,
            "is_empty": total_tasks == 0,
        }

    def clear(self) -> None:
        """Remove all tasks from the queue."""
        self._queue.clear()
        self._task_ids.clear()