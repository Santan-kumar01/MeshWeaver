import asyncio

from meshweaver.node import MeshNode


async def main():
    node = MeshNode(
        host="127.0.0.1",
        port=9999,
        name="Node-B",
    )

    await node.start()

    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        pass
    finally:
        await node.stop()


if __name__ == "__main__":
    asyncio.run(main())