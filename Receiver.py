from asyncio import sleep


def receiver():
    while True:
        sleep(1000)
        print("Receiver online")
