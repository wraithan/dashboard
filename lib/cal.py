import json
from datetime import datetime, timedelta
from pprint import pprint

import requests
from dateutil.rrule import rrulestr
from dateutil.tz import tzlocal
from icalendar import Calendar


def dt_cmp(unsafe_dt, other_dt):
    if not isinstance(unsafe_dt, datetime):
        other_dt = other_dt.date()
    elif not unsafe_dt.tzinfo:
        other_dt = other_dt.replace(tzinfo=None)

    if unsafe_dt > other_dt:
        return 1
    elif unsafe_dt == other_dt:
        return 0
    else:
        return -1


def get_events(ics, start, end):
    events = []
    cal = Calendar.from_ical(res.text)
    start_no_tz = start.replace(tzinfo=None)
    end_no_tz = end.replace(tzinfo=None)
    for event in cal.walk('vevent'):
        this_event = {
            'title': unicode(event.get('summary', '')),
            'description': unicode(event.get('description', '')),
            'location': unicode(event.get('location', '')),
            'raw': event
        }
        if 'rrule' in event:
            duration = event['dtstart'].dt - event['dtend'].dt
            rrule = rrulestr(event['rrule'].to_ical(),
                             dtstart=event['dtstart'].dt)
            if not isinstance(event['dtstart'].dt, datetime):
                occurances = rrule.between(start_no_tz, end_no_tz)
            else:
                occurances = rrule.between(start, end)
            for occ in occurances:
                print (dt_cmp(occ, start))
                if dt_cmp(occ, start) >= 0:
                    if dt_cmp(occ+duration, end) <= 0:
                        new_event = this_event.copy()
                        new_event['start'] = occ
                        new_event['end'] = occ+duration
                        events.append(new_event)
        elif dt_cmp(event['dtstart'].dt, start) >= 0:
            if dt_cmp(event['dtend'].dt, end) <= 0:
                this_event['start'] = event['dtstart'].dt
                this_event['end'] = event['dtend'].dt
                events.append(this_event)
    return events

if __name__ == '__main__':
    now = datetime.now(tzlocal())
    week = timedelta(days=365)
    with open('../calendars.json') as f:
        config = json.load(f)
        for line in config:
            res = requests.get(line['url'])
            pprint(get_events(res.text, now-week, now+week))
