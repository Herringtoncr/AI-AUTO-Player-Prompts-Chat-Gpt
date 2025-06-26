from scheduler import run_with_shift
import time

def dummy_task():
    # This stands in for your real work.
    print("⏰ dummy task at", time.strftime("%H:%M:%S"))
    time.sleep(1)  # simulate a quick action

if __name__ == "__main__":
    run_with_shift(dummy_task)
