import asyncio

from meshweaver.node import MeshNode


def test_node_starts_and_stops():
    async def run_test():
        node = MeshNode(
            host="127.0.0.1",
            port=9998,
            name="Test-Node",
        )

        await node.start()

        assert node.transport is not None

        await node.stop()

        assert node.transport is None

    asyncio.run(run_test())


def test_node_send_message():
    async def run_test():
        node = MeshNode(
            host="127.0.0.1",
            port=9997,
            name="Test-Node",
        )

        await node.start()

        assert node.transport is not None

        node.send_message(
            "PING",
            "127.0.0.1",
            9999,
        )

        await asyncio.sleep(0.1)

        await node.stop()

    asyncio.run(run_test())