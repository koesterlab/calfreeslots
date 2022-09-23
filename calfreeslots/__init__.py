import argparse
from collections import defaultdict, namedtuple
import os
import time
import calendar
from ics import Calendar
import requests
import datetime
import arrow
import icalendar
import recurring_ical_events

# from https://stackoverflow.com/a/6558571/7070491
def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


Event = namedtuple("Event", ["begin", "end"])


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--from", help="")
    args = parser.parse_args()
    return args


def main():
    args = cli()
    urls = os.environ["CALFREESLOTS_ICAL_URLS"].split(",")
    timezone = time.tzname[-1]

    # get the Friday after the next
    weekday_now = arrow.now().weekday()
    days_to_go = 4 - weekday_now + 8
    end_date = arrow.now() + datetime.timedelta(days=days_to_go)

    free_slots = {
        day.date(): Day(day)
        for day in arrow.Arrow.range("day", arrow.now(), end_date)
        if day.weekday() not in (5, 6)
    }

    for url in urls:
        calendar = icalendar.Calendar.from_ical(requests.get(url).text)
        events = recurring_ical_events.of(calendar).between(
            arrow.now().datetime, end_date.datetime
        )
        for event in events:
            begin = arrow.get(event["DTSTART"].dt).to(timezone)
            end = arrow.get(event["DTEND"].dt).to(timezone)

            try:
                free_slots[begin.date()].add_event(Event(begin, end))
            except KeyError:
                # day is not considered (e.g. weekend)
                pass

    for day in free_slots.values():
        day.process()

    free_slots = sorted(free_slots.values(), key=lambda x: x.day)
    print(*free_slots, sep="\n")


def parse_hour_min(day, hour_min):
    hour, minute = hour_min.split(":")
    return day.replace(hour=int(hour), minute=int(minute), second=0, microsecond=0)


class Slot:
    def __init__(self, day, begin=None, end=None):
        self.begin = begin or day.morning_start
        self.end = end or day.evening_end
        self.day = day

    def is_empty(self):
        return self.begin == self.end

    def shrink(self):
        delta = int(os.environ.get("CALFREESLOTS_SHRINK_SLOTS_MIN", "5"))
        if self.begin > self.day.morning_start:
            self.begin += datetime.timedelta(minutes=delta)
        if self.end < self.day.evening_end:
            self.end -= datetime.timedelta(minutes=delta)

    def __str__(self):
        b = self.begin.time()
        e = self.end.time()
        return f"{b.hour}:{b.minute:02d} - {e.hour}:{e.minute:02d}"

    def __gt__(self, other):
        return self.begin > other.begin


class Day:
    def __init__(self, day):
        self.morning_start = parse_hour_min(
            day, os.environ.get("CALFREESLOTS_MORNING_START", "9:00")
        )
        self.evening_end = parse_hour_min(
            day, os.environ.get("CALFREESLOTS_EVENING_END", "17:00")
        )
        self.slots = [Slot(self)]

    @property
    def day(self):
        return self.slots[0].begin

    def process(self):
        for slot in self.slots:
            slot.shrink()
        self.cleanup()

    def cleanup(self):
        self.slots = [slot for slot in self.slots if not slot.is_empty()]

    def add_event(self, event):
        for slot in list(self.slots):
            if slot.begin < event.begin:
                if slot.end > event.end:
                    # case 1: event is in the middle of the slot
                    self.slots.remove(slot)
                    self.slots.append(Slot(self, slot.begin, event.begin))
                    self.slots.append(Slot(self, event.end, slot.end))
                else:
                    if slot.end > event.begin:
                        # case 2: event overlaps the end of the slot
                        slot.end = event.begin
                    else:
                        # case 3: event comes after the slot
                        pass
            else:
                if slot.begin > event.end:
                    # case 4: slot is after the event
                    pass
                else:
                    if slot.end < event.end:
                        # case 5: slot is completely inside the event
                        self.slots.remove(slot)
                    else:
                        # case 6: event overlaps the beginning of the slot
                        slot.begin = event.end
        self.cleanup()

    def __str__(self):
        day_name = calendar.day_name[self.day.weekday()]
        sep = "\n    "
        return f"{day_name}, {self.day.date()}:\n    {sep.join(map(str, sorted(self.slots)))}"
