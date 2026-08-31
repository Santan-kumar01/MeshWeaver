from typing import Dict

from meshweaver.task_priority import TaskPriorityQueue


class QueueStatistics:
    """Provides statistics for a TaskPriorityQueue."""

    def __init__(self, queue: TaskPriorityQueue):
        self.queue = queue

    def total_tasks(self) -> int:
        """Return the total number of tasks in the queue."""

        return self.queue.size()

    def count_by_priority(self, priority: str) -> int:
        """Return the number of tasks with the given priority."""

        priority = priority.upper()

        if priority not in self.queue.PRIORITY_LEVELS:
            raise ValueError(
                f"Invalid priority: {priority}. "
                f"Expected HIGH, MEDIUM, or LOW."
            )

        count = 0

        for priority_level, _, _ in self.queue._queue:
            if priority_level == self.queue.PRIORITY_LEVELS[priority]:
                count += 1

        return count

    def high_priority_tasks(self) -> int:
        """Return the number of HIGH-priority tasks."""

        return self.count_by_priority("HIGH")

    def medium_priority_tasks(self) -> int:
        """Return the number of MEDIUM-priority tasks."""

        return self.count_by_priority("MEDIUM")

    def low_priority_tasks(self) -> int:
        """Return the number of LOW-priority tasks."""

        return self.count_by_priority("LOW")

    def is_empty(self) -> bool:
        """Return whether the queue is empty."""

        return self.queue.is_empty()

    def summary(self) -> Dict[str, int]:
        """Return queue statistics as a dictionary."""

        return {
            "total": self.total_tasks(),
            "high": self.high_priority_tasks(),
            "medium": self.medium_priority_tasks(),
            "low": self.low_priority_tasks(),
        }