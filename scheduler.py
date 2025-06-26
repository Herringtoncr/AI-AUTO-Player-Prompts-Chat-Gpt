# scheduler.py
import time, random, datetime
from automation.config_loader import config

# ── load shift settings ───────────────────────────────────────────
cfg     = config["shift"]
START_H = cfg["start_hour"]
SHIFT_S = cfg["shift_length_hours"] * 3600
LUNCH   = cfg["lunch"]
BREAKS  = cfg["breaks"]
RAND    = cfg.get("randomize", False)

def _rand_window(low_hour, high_hour, dur_s):
    low  = low_hour * 3600
    high = high_hour * 3600 - dur_s
    return random.uniform(low, max(low, high))

def schedule_times():
    """
    Returns a sorted list of (label, start_s, duration_s):
      [('break1', ...), ('lunch', ...), ('break2', ...)]
    """
    # convert minutes→seconds
    lunch_dur = LUNCH["duration_minutes"] * 60
    break_dur = BREAKS["duration_minutes"] * 60

    if RAND:
        # lunch random between earliest and latest
        ls = _rand_window(
            LUNCH["earliest_start_hour"],
            LUNCH["latest_start_hour"],
            lunch_dur
        )
        # one break before lunch window
        b1 = _rand_window(
            BREAKS["earliest_start_hour"],
            LUNCH["earliest_start_hour"],
            break_dur
        )
        # second break after lunch
        b2 = _rand_window(
            LUNCH["latest_start_hour"],
            START_H + cfg["shift_length_hours"],
            break_dur
        )
    else:
        # fixed times for quick testing
        b1 = SHIFT_S * (1/3)
        ls = SHIFT_S * (1/2)
        b2 = SHIFT_S * (2/3)

    events = [
        ("break1", b1, break_dur),
        ("lunch",  ls, lunch_dur),
        ("break2", b2, break_dur),
    ]
    # only keep those inside shift
    return sorted(events, key=lambda e: e[1])

def run_with_shift(task_fn):
    """
    Wraps your `main()`:
     - waits until shift start_hour
     - runs task_fn() in a loop, pausing for breaks & lunch
     - stops after shift_length_hours
    """
    now = datetime.datetime.now()
    start = now.replace(hour=START_H, minute=0, second=0, microsecond=0)
    if now < start:
        sec = (start - now).total_seconds()
        print(f"⏱ Sleeping {sec/60:.1f} min until {START_H}:00…")
        time.sleep(sec)

    shift_begin = time.time()
    events = schedule_times()
    done_ev  = set()

    print("🟢 Shift started at", datetime.datetime.now().strftime("%H:%M"))
    while True:
        elapsed = time.time() - shift_begin

        # end of shift?
        if elapsed >= SHIFT_S:
            print("🔴 Shift ended at", datetime.datetime.now().strftime("%H:%M"))
            break

        # check for any break/lunch to trigger
        for label, start_s, dur_s in events:
            if start_s <= elapsed < start_s + dur_s and label not in done_ev:
                print(f"☕️ {label.capitalize()} at +{start_s/3600:.2f} h for {dur_s/60} min")
                time.sleep(dur_s)
                done_ev.add(label)
                print("🔄 Resuming at", datetime.datetime.now().strftime("%H:%M"))
                break

        # run one iteration of your existing main()
        task_fn()

    print("✅ Done for the day.")
