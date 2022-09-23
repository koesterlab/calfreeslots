# calfreeslots

A small command line utility for printing free calendar slots (by parsing iCal data) in the coming days, either for personal use or for pasting into mails or chat platforms in order to let others know when you are available.

## Install

Given that you have a Python installation, you can install calfreeslots via

```bash
pip install calfreeslots
```

## Configure

Calfreeslots is configured via environment variables.
Put the following into your shell profile (e.g. `.bashrc` or `.zshrc`):

```bash
export CALFREESLOTS_ICAL_URLS="..." # Here, add ical urls, separated by commas.
export CALFREESLOTS_MORNING_START="9:30" # Start time in the morning.
export CALFREESLOTS_EVENING_END="17:00" # End time in the evening.
export CALFREESLOTS_SHRINK_SLOTS_MIN="5" # Minutes to shring free slots, in order to generate some free time between events.
```

For example, you can get iCal URLs for any of your google calendars by the following procedure:

1. Go to settings (gear icon at the top right).
2. Choose calendar in the left panel.
3. Scroll down to "Integrate calendar" and copy the "Secret address in iCal format".

## Example output

```
$ calfreeslots
Friday, 2022-09-23:
    9:00 - 17:00
Saturday, 2022-09-24:
    9:00 - 17:00
Sunday, 2022-09-25:
    9:00 - 17:00
Monday, 2022-09-26:
    10:05 - 10:55
    12:05 - 17:00
Tuesday, 2022-09-27:
    9:00 - 9:55
    10:35 - 15:55
Wednesday, 2022-09-28:
    9:00 - 13:55
    15:05 - 15:25
    16:05 - 17:00
Thursday, 2022-09-29:
    9:00 - 11:25
    12:35 - 13:10
    14:20 - 17:00
```
