import asyncio

from .network import UDPNodeProtocol
from .dht import KademliaDHT


class MeshNode:
    """Reusable asynchronous UDP node for MeshWeaver."""

    def __init__(
        self,
        host="127.0.0.1",
        port=9999,
        name="Node",
    ):
        self.host = host
        self.port = port
        self.name = name
        self.transport = None

        # Initialize local Kademlia DHT
        self.dht = KademliaDHT(
            node_id=KademliaDHT.generate_node_id(
                host,
                port,
            )
        )

    async def start(self):
        """Start the asynchronous UDP node."""

        loop = asyncio.get_running_loop()

        self.transport, _ = await loop.create_datagram_endpoint(
            lambda: UDPNodeProtocol(self.name),
            local_addr=(self.host, self.port),
        )

        print(
            f"[{self.name}] Node started "
            f"on {self.host}:{self.port}"
        )

    def send_message(
        self,
        message: str,
        target_host: str,
        target_port: int,
    ):
        """Send a UDP message to another node."""

        if self.transport is None:
            raise RuntimeError("Node is not running")

        self.transport.sendto(
            message.encode(),
            (target_host, target_port),
        )

        print(
            f"[{self.name}] Sent '{message}' "
            f"to {target_host}:{target_port}"
        )

    def add_peer(self, host: str, port: int):
        """Register another node as a known peer."""

        peer = self.dht.add_peer(
            host,
            port,
        )

        print(
            f"[{self.name}] Discovered peer "
            f"{peer.node_id[:8]} "
            f"at {peer.host}:{peer.port}"
        )

        return peer

    def get_peers(self):
        """Return all discovered peers."""

        return self.dht.get_peers()

    async def stop(self):
        """Stop the asynchronous UDP node."""

        if self.transport:
            self.transport.close()
            self.transport = None

        print(
            f"[{self.name}] Node stopped"
        )