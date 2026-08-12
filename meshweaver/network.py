import asyncio


class UDPNodeProtocol(asyncio.DatagramProtocol):
    def __init__(self, node_name: str):
        self.node_name = node_name
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        address = transport.get_extra_info("sockname")
        print(f"[{self.node_name}] Listening on {address}")

    def datagram_received(self, data, addr):
        message = data.decode()

        print(f"[{self.node_name}] Received '{message}' from {addr}")

        if message == "PING":
            self.transport.sendto(b"PONG", addr)
            print(f"[{self.node_name}] Sent 'PONG' to {addr}")

    def error_received(self, exc):
        print(f"[{self.node_name}] Network error: {exc}")

    def connection_lost(self, exc):
        print(f"[{self.node_name}] Connection closed")


async def start_node(host: str, port: int, node_name: str):
    loop = asyncio.get_running_loop()

    transport, _ = await loop.create_datagram_endpoint(
        lambda: UDPNodeProtocol(node_name),
        local_addr=(host, port),
    )

    return transport


async def send_ping(
    host: str,
    port: int,
    target_host: str,
    target_port: int,
):
    loop = asyncio.get_running_loop()

    transport, _ = await loop.create_datagram_endpoint(
        asyncio.DatagramProtocol,
        local_addr=(host, 0),
    )

    print(f"[Client] Sending PING to {target_host}:{target_port}")

    transport.sendto(
        b"PING",
        (target_host, target_port),
    )

    await asyncio.sleep(1)

    transport.close()


async def main():
    node_port = 9999

    node_transport = await start_node(
        "127.0.0.1",
        node_port,
        "Node-B",
    )

    await asyncio.sleep(1)

    await send_ping(
        "127.0.0.1",
        0,
        "127.0.0.1",
        node_port,
    )

    await asyncio.sleep(1)

    node_transport.close()


if __name__ == "__main__":
    asyncio.run(main())