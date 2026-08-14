import asyncio

from .network import UDPNodeProtocol


class MeshNode:
    """Reusable asynchronous UDP node for MeshWeaver."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 9999,
        name: str = "Node",
    ):
        self.host = host
        self.port = port
        self.name = name
        self.transport = None

    async def start(self):
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

    async def stop(self):
        if self.transport:
            self.transport.close()
            self.transport = None

        print(f"[{self.name}] Node stopped")