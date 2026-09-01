from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
import time

from meshweaver.dht import Peer


class TaskStatus(Enum):
    """Possible states of a task."""

    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    REASSIGNED = "reassigned"
    TIMEOUT = "timeout"


@dataclass
class PeerResource:
    """System resource information for a peer."""

    cpu_percent: float
    ram_percent: float = 0.0


@dataclass
class ExecutionRecord:
    """Historical record of one task execution."""

    task_id: str
    peer_id: Optional[str]
    status: TaskStatus
    started_at: Optional[float]
    finished_at: Optional[float]
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0


@dataclass
class Task:
    """Task information and lifecycle state."""

    task_id: str
    status: TaskStatus = TaskStatus.PENDING
    peer_id: Optional[str] = None
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    timeout: float = 30.0

    history: list[ExecutionRecord] = field(
        default_factory=list
    )


class TaskRouter:
    """Route tasks using CPU-aware selection, priority queue,
    lifecycle management, timeout, retry, result persistence
    and execution history.
    """

    def __init__(self):
        # Local import prevents circular import:
        # task_priority.py imports Task from router.py
        from meshweaver.task_priority import TaskPriorityQueue

        self.resources = {}
        self.tasks = {}

        # Priority queue integration
        self.priority_queue = TaskPriorityQueue()

    def update_resource(
        self,
        peer_id: str,
        cpu_percent: float,
        ram_percent: float = 0.0,
    ):
        """Update resource information for a peer."""

        self.resources[peer_id] = PeerResource(
            cpu_percent=cpu_percent,
            ram_percent=ram_percent,
        )

    def select_peer(
        self,
        peers: list[Peer],
    ) -> Optional[Peer]:
        """Select the peer with the lowest CPU usage."""

        available_peers = [
            peer
            for peer in peers
            if peer.node_id in self.resources
        ]

        if not available_peers:
            return None

        return min(
            available_peers,
            key=lambda peer: self.resources[
                peer.node_id
            ].cpu_percent,
        )

    def create_task(
        self,
        task_id: str,
        max_retries: int = 3,
        timeout: float = 30.0,
    ) -> Task:
        """Create a new pending task."""

        task = Task(
            task_id=task_id,
            max_retries=max_retries,
            timeout=timeout,
        )

        self.tasks[task_id] = task

        return task

    def add_task(
        self,
        task_id: str,
        priority: str = "MEDIUM",
        max_retries: int = 3,
        timeout: float = 30.0,
    ) -> bool:
        """Create and add a task to the priority queue."""

        if task_id in self.tasks:
            return False

        task = self.create_task(
            task_id=task_id,
            max_retries=max_retries,
            timeout=timeout,
        )

        return self.priority_queue.add_task(
            task,
            priority,
        )

    def get_next_task(self) -> Optional[Task]:
        """Return the highest-priority pending task."""

        return self.priority_queue.get_next_task()

    def pop_next_task(self) -> Optional[Task]:
        """Remove and return the highest-priority task."""

        return self.priority_queue.pop_task()

    def remove_queued_task(
        self,
        task_id: str,
    ) -> bool:
        """Remove a task from the priority queue."""

        return self.priority_queue.remove_task(task_id)

    def queue_size(self) -> int:
        """Return the number of queued tasks."""

        return self.priority_queue.size()

    def assign_task(
        self,
        task_id: str,
        peer: Peer,
    ) -> bool:
        """Assign a task to a peer."""

        task = self.tasks.get(task_id)

        if task is None:
            task = self.create_task(task_id)

        if peer.node_id not in self.resources:
            return False

        task.peer_id = peer.node_id
        task.status = TaskStatus.ASSIGNED
        task.error = None

        # Remove task from priority queue after assignment.
        self.priority_queue.remove_task(task_id)

        return True

    def start_task(
        self,
        task_id: str,
    ) -> bool:
        """Mark an assigned task as running."""

        task = self.tasks.get(task_id)

        if task is None:
            return False

        if task.status != TaskStatus.ASSIGNED:
            return False

        task.status = TaskStatus.RUNNING
        task.started_at = time.monotonic()
        task.finished_at = None
        task.error = None

        return True

    def complete_task(
        self,
        task_id: str,
        result: Any = None,
    ) -> bool:
        """Complete a running task and persist its result."""

        task = self.tasks.get(task_id)

        if task is None:
            return False

        if task.status != TaskStatus.RUNNING:
            return False

        task.status = TaskStatus.COMPLETED
        task.result = result
        task.error = None
        task.finished_at = time.monotonic()

        self._save_execution_history(task)

        return True

    def fail_task(
        self,
        task_id: str,
        error: Optional[str] = None,
    ) -> bool:
        """Mark a task as failed and persist the error."""

        task = self.tasks.get(task_id)

        if task is None:
            return False

        task.status = TaskStatus.FAILED
        task.error = error
        task.finished_at = time.monotonic()

        self._save_execution_history(task)

        return True

    def record_execution(
        self,
        task_id: str,
        status: TaskStatus,
        peer_id: Optional[str] = None,
        started_at: Optional[float] = None,
        finished_at: Optional[float] = None,
        result: Any = None,
        error: Optional[str] = None,
        retry_count: int = 0,
    ) -> Optional[ExecutionRecord]:
        """Record an execution attempt in task history."""

        task = self.tasks.get(task_id)

        if task is None:
            return None

        record = ExecutionRecord(
            task_id=task_id,
            peer_id=(
                peer_id
                if peer_id is not None
                else task.peer_id
            ),
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            result=result,
            error=error,
            retry_count=retry_count,
        )

        task.history.append(record)

        return record

    def _save_execution_history(
        self,
        task: Task,
    ):
        """Save the current execution state to history."""

        record = ExecutionRecord(
            task_id=task.task_id,
            peer_id=task.peer_id,
            status=task.status,
            started_at=task.started_at,
            finished_at=task.finished_at,
            result=task.result,
            error=task.error,
            retry_count=task.retry_count,
        )

        task.history.append(record)

    def get_task(
        self,
        task_id: str,
    ) -> Optional[Task]:
        """Return task information."""

        return self.tasks.get(task_id)

    def get_task_result(
        self,
        task_id: str,
    ) -> Any:
        """Return the persisted result of a completed task."""

        task = self.tasks.get(task_id)

        if task is None:
            return None

        if task.status != TaskStatus.COMPLETED:
            return None

        return task.result

    def get_task_error(
        self,
        task_id: str,
    ) -> Optional[str]:
        """Return the error of a failed task."""

        task = self.tasks.get(task_id)

        if task is None:
            return None

        return task.error

    def get_execution_history(
        self,
        task_id: str,
    ) -> list[ExecutionRecord]:
        """Return complete execution history of a task."""

        task = self.tasks.get(task_id)

        if task is None:
            return []

        return list(task.history)

    def get_latest_execution(
        self,
        task_id: str,
    ) -> Optional[ExecutionRecord]:
        """Return the latest execution record."""

        history = self.get_execution_history(task_id)

        if not history:
            return None

        return history[-1]

    def remove_peer(
        self,
        peer_id: str,
    ):
        """Remove a failed peer from resource tracking."""

        self.resources.pop(peer_id, None)

    def reassign_tasks(
        self,
        failed_peer_id: str,
        peers: list[Peer],
    ) -> dict[str, str]:
        """Reassign tasks from a failed peer."""

        self.remove_peer(failed_peer_id)

        reassigned = {}

        for task_id, task in self.tasks.items():

            if task.peer_id != failed_peer_id:
                continue

            new_peer = self.select_peer(peers)

            if new_peer is None:
                task.status = TaskStatus.FAILED
                task.error = (
                    "No available peer for reassignment"
                )
                task.finished_at = time.monotonic()

                continue

            task.peer_id = new_peer.node_id
            task.status = TaskStatus.REASSIGNED
            task.error = None
            task.started_at = None

            reassigned[task_id] = new_peer.node_id

        return reassigned

    def check_timeouts(self) -> list[str]:
        """Detect running tasks that exceeded their timeout."""

        current_time = time.monotonic()
        timed_out = []

        for task_id, task in self.tasks.items():

            if task.status != TaskStatus.RUNNING:
                continue

            if task.started_at is None:
                continue

            elapsed = current_time - task.started_at

            if elapsed >= task.timeout:
                task.status = TaskStatus.TIMEOUT
                task.error = "Task execution timed out"
                task.finished_at = current_time

                self._save_execution_history(task)

                task.started_at = None

                timed_out.append(task_id)

        return timed_out

    def retry_task(
        self,
        task_id: str,
        peers: list[Peer],
    ) -> bool:
        """Retry a timed-out or failed task."""

        task = self.tasks.get(task_id)

        if task is None:
            return False

        if task.retry_count >= task.max_retries:
            task.status = TaskStatus.FAILED
            task.error = "Maximum retry limit reached"
            task.finished_at = time.monotonic()

            return False

        if task.status not in (
            TaskStatus.TIMEOUT,
            TaskStatus.FAILED,
        ):
            return False

        peer = self.select_peer(peers)

        if peer is None:
            task.status = TaskStatus.FAILED
            task.error = "No available peer for retry"
            task.finished_at = time.monotonic()

            return False

        task.retry_count += 1
        task.peer_id = peer.node_id
        task.status = TaskStatus.REASSIGNED
        task.error = None
        task.started_at = None
        task.finished_at = None

        return True

    def retry_timed_out_tasks(
        self,
        peers: list[Peer],
    ) -> list[str]:
        """Check timeouts and retry eligible tasks."""

        timed_out_tasks = self.check_timeouts()
        retried_tasks = []

        for task_id in timed_out_tasks:

            if self.retry_task(
                task_id,
                peers,
            ):
                retried_tasks.append(task_id)

        return retried_tasks

    def get_retry_count(
        self,
        task_id: str,
    ) -> int:
        """Return the current retry count."""

        task = self.tasks.get(task_id)

        if task is None:
            return 0

        return task.retry_count