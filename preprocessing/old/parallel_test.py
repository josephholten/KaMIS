import asyncio
import time


async def say_after(delay, msg):
    await asyncio.sleep(delay)
    print(msg)


async def main():
    print(f"started at {time.strftime('%X')}")

    task1 = asyncio.create_task(say_after(1, "hello"))
    task2 = asyncio.create_task(say_after(2, "world"))
    await task1
    await task2

    print(f"ended at {time.strftime('%X')}")

asyncio.run(main())
