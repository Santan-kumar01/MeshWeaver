from dataclasses import dataclass
from enum import Enum
from typing import Optional
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
    RETRYING = "retrying"


@dataclass
class PeerResource:
    """System resource information for a peer."""

    cpu_percent: float
    ram_percent: float = 0.0


@dataclass
class Task:
    """Task information and lifecycle state."""

    task_id: str
    status: TaskStatus = TaskStatus.PENDING
    peer_id: Optional[str] = None
    result: Optional[object] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    started_at: Optional[float] = None
    timeout: float = 30.0


class TaskRouter:
    """Route tasks with lifecycle, timeout and retry management."""

    def __init__(self):
        self.resources = {}
        self.tasks = {}

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

    def select_peer(self, peers: list[Peer]) -> Optional[Peer]:
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

        return True

    def start_task(self, task_id: str) -> bool:
        """Start an assigned task."""

        task = self.tasks.get(task_id)

        if task is None:
            return False

        if task.status != TaskStatus.ASSIGNED:
            return False

        task.status = TaskStatus.RUNNING
        task.started_at = time.monotonic()

        return True

    def complete_task(
        self,
        task_id: str,
        result=None,
    ) -> bool:
        """Complete a running task and store its result."""

        task = self.tasks.get(task_id)

        if task is None:
            return False

        if task.status != TaskStatus.RUNNING:
            return False

        task.status = TaskStatus.COMPLETED
        task.result = result
        task.started_at = None

        return True

    def fail_task(
        self,
        task_id: str,
        error: str = "Task execution failed",
    ) -> bool:
        """Mark a task as failed."""

        task = self.tasks.get(task_id)

        if task is None:
            return False

        task.status = TaskStatus.FAILED
        task.error = error
        task.started_at = None

        return True

    def check_timeout(self, task_id: str) -> bool:
        """Check whether a running task has exceeded its timeout."""

        task = self.tasks.get(task_id)

        if task is None:
            return False

        if task.status != TaskStatus.RUNNING:
            return False

        if task.started_at is None:
            return False

        elapsed = time.monotonic() - task.started_at

        if elapsed < task.timeout:
            return False

        task.status = TaskStatus.TIMEOUT
        task.error = "Task execution timed out"
        task.started_at = None

        return True

    def retry_task(self, task_id: str) -> bool:
        """Retry a timed-out or failed task."""

        task = self.tasks.get(task_id)

        if task is None:
            return False

        if task.status not in (
            TaskStatus.TIMEOUT,
            TaskStatus.FAILED,
        ):
            return False

        if task.retry_count >= task.max_retries:
            task.status = TaskStatus.FAILED
            task.error = "Maximum retry limit exceeded"
            return False

        task.retry_count += 1
        task.status = TaskStatus.RETRYING
        task.error = None

        return True

    def get_task(self, task_id: str) -> Optional[Task]:
        """Return task information."""

        return self.tasks.get(task_id)

    def remove_peer(self, peer_id: str):
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
                task.error = "No available peer"
                continue

            task.peer_id = new_peer.node_id
            task.status = TaskStatus.REASSIGNED

            reassigned[task_id] = new_peer.node_id

        return reassigned