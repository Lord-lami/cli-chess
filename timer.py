from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
import time
import threading


def timer(duration: int, stop_timer: threading.Event) -> None:
    # stop_timer.clear()
    for sec in range(duration, 0, -1):
        if stop_timer.is_set():
            return
        print(sec, end="", flush=True)
        time.sleep(1)
        print("\r", end="", flush=True)
    print(0, end="", flush=True)

def timed_input(duration: int, prompt: str) -> str:
    stop_timer = threading.Event()
    session = PromptSession()
    with patch_stdout():
        thread = threading.Thread(target=timer, args=(duration, stop_timer))
        thread.start()
        command = session.prompt(prompt)
    stop_timer.set()
    thread.join()
    return command

# print(f"You entered: {name}")


# print("Beans butter bunny", end="", flush=True)
# time.sleep(1)
# print("\r\033[2K")
# print("\b", end="")
# print("\r", end="")
# print("Chicken")
# timed_input(10, "> ")