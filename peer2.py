import asyncio
from asyncio import sleep

import p2p


async def main():
    for x in range(10000):
        await p2p.SendFiles("Test1.jpg", x, 1269)
        await sleep(0.1)
        print("Sent File Fragment")


if __name__ == "__main__":
    asyncio.run(main())
