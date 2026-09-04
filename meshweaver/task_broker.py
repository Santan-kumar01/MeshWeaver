from typing import Optional

from meshweaver.router import Task, TaskRouter
from meshweaver.task_queue import TaskQueue


class TaskBroker:
    """High-level broker for submitting and managing tasks."""

    def __init__(self):
        self.router = TaskRouter()
        self.queue = TaskQueue()

    def submit_task(
        self,
        task_id: str,
        max_retries: int = 3,
        timeout: float = 30.0,
    ) -> Optional[Task]:
        """Create and enqueue a new task."""

        if self.queue.contains(task_id):
            return None

        if task_id in self.router.tasks:
            return None

        task = self.router.create_task(
            task_id=task_id,
            max_retries=max_retries,
            timeout=timeout,
        )

        if not self.queue.add_task(task):
            return None

        return task

    def get_next_task(self) -> Optional[Task]:
        """Return the next queued task without removing it."""

        return self.queue.get_next_task()

    def pop_next_task(self) -> Optional[Task]:
        """Remove and return the next queued task."""

        return self.queue.pop_task()

    def get_task(self, task_id: str) -> Optional[Task]:
        """Return a task by ID."""

        return self.router.get_task(task_id)

    def queue_size(self) -> int:
        """Return the number of queued tasks."""

        return self.queue.size()

    def statistics(self) -> dict:
        """Return current broker queue statistics."""

        return self.queue.statistics()

    def clear_queue(self) -> None:
        """Remove all queued tasks."""

        self.queue.clear()