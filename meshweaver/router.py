from dataclasses import dataclass
from typing import Optional

from meshweaver.dht import Peer


@dataclass
class PeerResource:
    """System resource information for a peer."""

    cpu_percent: float
    ram_percent: float = 0.0


class TaskRouter:
    """Select the least-loaded peer for task execution."""

    def __init__(self):
        self.resources = {}

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
            peer for peer in peers
            if peer.node_id in self.resources
        ]

        if not available_peers:
            return None

        return min(
            available_peers,
            key=lambda peer: self.resources[peer.node_id].cpu_percent,
        )