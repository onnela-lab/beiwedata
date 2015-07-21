# -*- coding: utf-8 -*-
"""Internal functions. Purely for convenience in using pandas.DataFrame.apply.

    Probably shouldn't be used otherwise.

"""
import datetime

def _sms_sort(row, yval=1, spacer=.05):
    if row['sent vs received'] == 'sent SMS':
        return yval+spacer
    if row['sent vs received'] == 'received SMS':
        return yval-spacer

def _call_end(row):
    start_t = datetime.datetime.utcfromtimestamp(int(row['timestamp'] / 1000))
    end_t = start_t + datetime.timedelta(0, row['duration in seconds'])
    return end_t

def _call_sort(row, yval=1.5, spacer=.05):
    if row['call type'] == "Incoming Call":
        return yval-spacer
    ## keep missed calls separate for now in case we change this later
    elif row['call type'] == "Missed Call":
        return yval-spacer
    elif row['call type'] == "Outgoing Call":
        return yval+spacer
    else:
        return None
