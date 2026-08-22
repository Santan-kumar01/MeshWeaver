from dataclasses import dataclass
from typing import Optional

from meshweaver.dht import Peer


@dataclass
class PeerResource:
    """System resource information for a peer."""

    cpu_percent: float
    ram_percent: float = 0.0


class TaskRouter:
    """Route tasks using CPU-aware peer selection and failure recovery."""

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

    def assign_task(
        self,
        task_id: str,
        peer: Peer,
    ) -> bool:
        """Assign a task to a peer."""

        if peer.node_id not in self.resources:
            return False

        self.tasks[task_id] = peer.node_id

        return True

    def remove_peer(self, peer_id: str):
        """Remove a failed peer from resource tracking."""

        self.resources.pop(peer_id, None)

    def reassign_tasks(
        self,
        failed_peer_id: str,
        peers: list[Peer],
    ) -> dict[str, str]:
        """Reassign tasks from a failed peer."""

        # Remove failed peer
        self.remove_peer(failed_peer_id)

        reassigned = {}

        # Find tasks assigned to failed peer
        for task_id, assigned_peer_id in list(
            self.tasks.items()
        ):
            if assigned_peer_id != failed_peer_id:
                continue

            # Select another healthy peer
            new_peer = self.select_peer(peers)

            if new_peer is None:
                continue

            # Reassign task
            self.tasks[task_id] = new_peer.node_id

            reassigned[task_id] = new_peer.node_id

        return reassigned