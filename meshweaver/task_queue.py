from collections import deque

class TaskQueue:
    """FIFO task queue with duplicate task ID prevention."""

    def __init__(self):
        self._queue = deque()
        self._tasks = {}

    def add_task(self, task_id: str, task) -> None:
        """Add a task to the queue."""

        if not task_id:
            raise ValueError("Task ID cannot be empty")

        if task_id in self._tasks:
            raise ValueError(f"Task with ID '{task_id}' already exists")

        self._queue.append(task_id)
        self._tasks[task_id] = task

    def get_next_task(self):
        """Return the next pending task without removing it."""

        if self.is_empty():
            return None

        task_id = self._queue[0]
        return task_id, self._tasks[task_id]

    def remove_task(self, task_id: str) -> bool:
        """Remove a task from the queue by its ID."""

        if task_id not in self._tasks:
            return False

        self._queue.remove(task_id)
        del self._tasks[task_id]

        return True

    def is_empty(self) -> bool:
        """Return True if the queue is empty."""

        return len(self._queue) == 0

    def size(self) -> int:
        """Return the number of tasks in the queue."""

        return len(self._queue)