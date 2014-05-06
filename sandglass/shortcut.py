#coding=utf-8
from datetime import datetime
from sandglass import Sandglass,ben

__all__ = ['tslice','timediff']

def tslice(unit,start=None,end=None,step=1,count=None):
    '''tslice(unit,start=None,end=None,step=1,count=None) -> generator of Sandglass object
    unit in ['year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond']
    this is some kind xrange-like
    '''
    if unit not in Sandglass._units:
        raise AttributeError()
    if isinstance(start,basestring):
        start = ben(start)
    if isinstance(end,basestring):
        end = ben(end)

    start = start or ben()
    count = count or float('inf')
    cur  = start
    cnt = 0
    if step>0:
        end = end or ben(datetime.max)
        while cur<end and cnt<count:
            yield cur
            cur = cur.shifted(**{unit:step})
            cnt += 1
    elif step<0:
        end = end or ben(datetime.min)
        while cur>end and cnt<count:
            yield cur
            cur = cur.shifted(**{unit:step})
            cnt += 1


def timediff(timestr,factor=86400,base=None):
    '''Get the distance to the next time
    >>>timediff('20:00:00',factor=86400,base='19:30:00')
    1800
    >>>timediff('20:00:00',factor=86400,base='21:30:00')
    81000
    '''
    base = ben(base) if base else ben()
    sg = ben(timestr)
    diff = int((sg - base).total_seconds())
    return diff%factor

