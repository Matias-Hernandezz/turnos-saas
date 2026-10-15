from dataclasses import dataclass
from datetime import date, datetime, time, timedelta


@dataclass(frozen=True, slots=True)
class TimeRange:
    start: datetime
    end: datetime


@dataclass(frozen=True, slots=True)
class BusyBlock:
    start: datetime
    end: datetime


def _parse_day_bounds(day: date, open_time: time, close_time: time) -> TimeRange:
    start = datetime.combine(day, open_time)
    end = datetime.combine(day, close_time)
    if end <= start:
        raise ValueError("close_time must be after open_time")
    return TimeRange(start=start, end=end)


def generate_slots(
    *,
    day: date,
    open_time: time,
    close_time: time,
    slot_minutes: int,
    busy: list[BusyBlock],
) -> list[TimeRange]:
    """
    Función pura: slots libres dentro del horario menos bloques ocupados.
    Sin DB — 100 % testeable.
    """
    if slot_minutes <= 0:
        raise ValueError("slot_minutes must be positive")

    window = _parse_day_bounds(day, open_time, close_time)
    step = timedelta(minutes=slot_minutes)
    slots: list[TimeRange] = []

    cursor = window.start
    while cursor + step <= window.end:
        candidate = TimeRange(start=cursor, end=cursor + step)
        if not _overlaps_any(candidate, busy):
            slots.append(candidate)
        cursor += step

    return slots


def _overlaps_any(slot: TimeRange, busy: list[BusyBlock]) -> bool:
    for block in busy:
        if slot.start < block.end and slot.end > block.start:
            return True
    return False
