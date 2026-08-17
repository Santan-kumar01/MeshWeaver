import asyncio

from meshweaver.node import MeshNode


async def main():
    # Create two nodes
    node_a = MeshNode(
        host="127.0.0.1",
        port=9001,
        name="Node-A",
    )

    node_b = MeshNode(
        host="127.0.0.1",
        port=9002,
        name="Node-B",
    )

    # Start both nodes
    await node_a.start()
    await node_b.start()

    # Node-A discovers Node-B
    node_a.add_peer(
        "127.0.0.1",
        9002,
    )

    print("\n[Node-A] Known peers:")

    for peer in node_a.get_peers():
        print(
            f"  - {peer.node_id[:8]} "
            f"-> {peer.host}:{peer.port}"
        )

    # Keep nodes alive briefly
    await asyncio.sleep(1)

    # Stop nodes
    await node_a.stop()
    await node_b.stop()


if __name__ == "__main__":
    asyncio.run(main())