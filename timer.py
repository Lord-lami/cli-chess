from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
import time
import threading
import asyncio
import queue


def timer(duration: int, stop_timer: threading.Event, remaining_time: queue.Queue) -> None:
    # stop_timer.clear()
    for sec in range(duration, 0, -1):
        if stop_timer.is_set():
            remaining_time.put(sec)
            return
        print(sec, end="", flush=True)
        time.sleep(1)
        print("\r", end="", flush=True)
    print(0, end="", flush=True)
    remaining_time.put(0)



async def timed_input(duration: int, prompt: str) -> str | None:
    session = PromptSession()

    try:
        return await asyncio.wait_for(
            session.prompt_async(prompt),
            timeout=duration
        )
    except asyncio.TimeoutError:
        return None


def timer_timed_input(duration: int, prompt: str) -> tuple[str, int]:
    stop_timer = threading.Event()
    remaining_time = queue.Queue()
    with patch_stdout():
        thread = threading.Thread(target=timer, args=(duration, stop_timer, remaining_time))
        thread.start()
        command = asyncio.run(timed_input(duration, prompt))

    stop_timer.set()
    thread.join()
    return command, remaining_time.get()

# print(f"You entered: {name}")


# print("Beans butter bunny", end="", flush=True)
# time.sleep(1)
# print("\r\033[2K")
# print("\b", end="")
# print("\r", end="")
# print("Chicken")
# timed_input(10, "> ")