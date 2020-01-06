import datetime
import random


def random_date(earliest=None, latest=None):
    earliest = earliest or datetime.datetime(1935, 1, 1)
    latest = latest or datetime.datetime(1990, 12, 31)
    
    assert latest > earliest

    delta = latest - earliest
    seconds = int(delta.total_seconds())
    random_dur = random.randrange(seconds)
    return earliest + datetime.timedelta(seconds=random_dur)
