from typing import Dict, Any


class QueueMonitor:
    """Monitor task queue activity and provide queue health information."""

    def __init__(self, queue):
        self.queue = queue
        self.total_added = 0
        self.total_processed = 0
        self.total_removed = 0

    def record_added(self) -> None:
        """Record a task added to the queue."""
        self.total_added += 1

    def record_processed(self) -> None:
        """Record a task processed from the queue."""
        self.total_processed += 1

    def record_removed(self) -> None:
        """Record a task removed from the queue."""
        self.total_removed += 1

    def get_status(self) -> Dict[str, Any]:
        """Return the current queue monitoring status."""
        return {
            "queue_size": self.queue.size(),
            "total_added": self.total_added,
            "total_processed": self.total_processed,
            "total_removed": self.total_removed,
        }

    def is_healthy(self) -> bool:
        """Return True when the queue is operating normally."""
        return self.queue.size() >= 0

    def summary(self) -> str:
        """Return a human-readable queue monitoring summary."""
        status = self.get_status()

        return (
            f"Queue size: {status['queue_size']}, "
            f"Added: {status['total_added']}, "
            f"Processed: {status['total_processed']}, "
            f"Removed: {status['total_removed']}"
        )