import hashlib
from dataclasses import dataclass


@dataclass
class Peer:
    node_id: str
    host: str
    port: int


class KademliaDHT:
    """Basic Kademlia-inspired peer registry and routing table."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.peers = {}

    @staticmethod
    def generate_node_id(host: str, port: int) -> str:
        """Generate a unique node ID."""
        value = f"{host}:{port}".encode()
        return hashlib.sha256(value).hexdigest()

    def add_peer(self, host: str, port: int) -> Peer:
        """Add or update a peer in the routing table."""
        peer_id = self.generate_node_id(host, port)

        # Do not add the local node as a peer
        if peer_id == self.node_id:
            return Peer(
                node_id=peer_id,
                host=host,
                port=port,
            )

        peer = Peer(
            node_id=peer_id,
            host=host,
            port=port,
        )

        self.peers[peer_id] = peer

        return peer

    def remove_peer(self, node_id: str) -> bool:
        """Remove a peer from the routing table."""
        return self.peers.pop(node_id, None) is not None

    def find_peer(self, node_id: str):
        """Find a peer by node ID."""
        return self.peers.get(node_id)

    def get_peers(self):
        """Return all known peers."""
        return list(self.peers.values())

    def peer_count(self) -> int:
        """Return the number of known peers."""
        return len(self.peers)

    def find_closest_peers(self, target_id: str, count: int = 3):
        """
        Return peers closest to the target ID using XOR distance.

        This is a simplified Kademlia-style lookup.
        """
        if count <= 0:
            return []

        target = int(target_id, 16)

        sorted_peers = sorted(
            self.peers.values(),
            key=lambda peer: int(peer.node_id, 16) ^ target,
        )

        return sorted_peers[:count]

    def has_peer(self, node_id: str) -> bool:
        """Check whether a peer exists in the routing table."""
        return node_id in self.peers

    def clear_peers(self):
        """Remove all peers from the routing table."""
        self.peers.clear()