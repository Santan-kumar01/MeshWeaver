import time
from dataclasses import dataclass


@dataclass
class PeerHeartbeat:
    """Heartbeat state for a peer."""

    last_seen: float


class HeartbeatMonitor:
    """Monitor peers and detect inactive nodes."""

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self.peers = {}

    def register_peer(self, peer_id: str) -> None:
        """Register a peer for heartbeat monitoring."""

        self.peers[peer_id] = PeerHeartbeat(
            last_seen=time.monotonic()
        )

    def heartbeat(self, peer_id: str) -> None:
        """Update the last-seen time of a peer."""

        if peer_id not in self.peers:
            self.register_peer(peer_id)
            return

        self.peers[peer_id].last_seen = time.monotonic()

    def is_alive(self, peer_id: str) -> bool:
        """Check whether a peer is still alive."""

        peer = self.peers.get(peer_id)

        if peer is None:
            return False

        elapsed = time.monotonic() - peer.last_seen

        return elapsed <= self.timeout

    def get_failed_peers(self) -> list[str]:
        """Return peers whose heartbeat has timed out."""

        now = time.monotonic()

        return [
            peer_id
            for peer_id, peer in self.peers.items()
            if now - peer.last_seen > self.timeout
        ]

    def remove_peer(self, peer_id: str) -> bool:
        """Remove a peer from heartbeat monitoring."""

        return self.peers.pop(peer_id, None) is not None