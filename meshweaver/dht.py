import hashlib
from dataclasses import dataclass


@dataclass
class Peer:
    node_id: str
    host: str
    port: int


class KademliaDHT:
    """Basic peer registry for MeshWeaver."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.peers = {}

    @staticmethod
    def generate_node_id(host: str, port: int) -> str:
        """Generate a unique node ID."""
        value = f"{host}:{port}".encode()
        return hashlib.sha256(value).hexdigest()

    def add_peer(self, host: str, port: int) -> Peer:
        """Add a peer to the local registry."""
        peer_id = self.generate_node_id(host, port)

        peer = Peer(
            node_id=peer_id,
            host=host,
            port=port,
        )

        self.peers[peer_id] = peer

        return peer

    def remove_peer(self, node_id: str) -> bool:
        """Remove a peer."""
        return self.peers.pop(node_id, None) is not None

    def find_peer(self, node_id: str):
        """Find a peer by node ID."""
        return self.peers.get(node_id)

    def get_peers(self):
        """Return all known peers."""
        return list(self.peers.values())

    def peer_count(self) -> int:
        """Return number of known peers."""
        return len(self.peers)