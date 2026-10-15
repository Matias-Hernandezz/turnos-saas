from datetime import date, datetime, time

from features.availability.slot_calculator import BusyBlock, generate_slots


def test_generate_slots_excludes_busy():
    day = date(2026, 6, 2)
    busy = [
        BusyBlock(
            start=datetime(2026, 6, 2, 10, 0),
            end=datetime(2026, 6, 2, 10, 30),
        )
    ]
    slots = generate_slots(
        day=day,
        open_time=time(9, 0),
        close_time=time(12, 0),
        slot_minutes=30,
        busy=busy,
    )
    starts = [s.start for s in slots]
    assert datetime(2026, 6, 2, 9, 0) in starts
    assert datetime(2026, 6, 2, 10, 0) not in starts
    assert datetime(2026, 6, 2, 10, 30) in starts
