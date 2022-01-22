import asyncio
from asyncio import sleep
import p2p
from random import *


async def main():
    for x in range(500):
        x = randint(0, 500)
        await p2p.SendFiles("Test1.jpg", x, 2000)
        await sleep(0.1)
        print("Sent File Fragment")


if __name__ == "__main__":
    asyncio.run(main())
