from dataclasses import dataclass
from typing import List

from meshweaver.dht import Peer, KademliaDHT


@dataclass
class GossipMessage:
    sender_id: str
    peers: List[Peer]


class GossipProtocol:
    """Basic gossip protocol for sharing peer information."""

    def __init__(self, dht: KademliaDHT):
        self.dht = dht

    def create_message(self) -> GossipMessage:
        """Create a gossip message containing known peers."""
        return GossipMessage(
            sender_id=self.dht.node_id,
            peers=self.dht.get_peers(),
        )

    def receive_message(self, message: GossipMessage) -> int:
        """Merge received peer information into the local DHT."""

        added = 0

        for peer in message.peers:
            # Don't add ourselves
            if peer.node_id == self.dht.node_id:
                continue

            # Add only unknown peers
            if not self.dht.has_peer(peer.node_id):
                self.dht.add_peer(peer.host, peer.port)
                added += 1

        return added