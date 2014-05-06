#coding=utf-8
from datetime import datetime, timedelta
import time
import calendar
from relativedelta import relativedelta
from functools import total_ordering
from timeparser import timeparse

__all__ = ['Sandglass','ben']

@total_ordering
class Sandglass(object):
    '''The core object.Enhence the datetime.datetime.
    '''
    mock_offset = {}
    _units = ['year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond']
    def __init__(self, year=1970, month=1, day=1, hour=0, minute=0, second=0, microsecond=0,dt = None):
        if dt:
            self._dt = dt
        else:
            self._dt = datetime(year, month, day, hour, minute, second, microsecond)

    @classmethod
    def mock(cls,**kwargs):
        '''fake current time,don't need to change OS time,it is helpful for test'''
        cls.mock_offset = kwargs

    @classmethod
    def unmock(cls):
        cls.mock_offset = {}

    @classmethod
    def now(cls):
        dt = datetime.now()
        return cls(dt=dt).shift(**cls.mock_offset)

    @classmethod
    def fromtimestamp(cls, timestamp):
        timestamp = float(timestamp )
        dt = datetime.fromtimestamp(timestamp)
        return cls(dt=dt)

    def raw(self):
        return self._dt

    def clone(self):
        return self.__class__(dt=self._dt)

    def replace(self, **kwargs):
        self._dt = self._dt.replace(**kwargs)

    def shift(self, **kwargs):
        '''in place'''
        for unit in kwargs:
            setattr(self, unit.rstrip('s'), getattr(self, unit.rstrip('s')) + kwargs[unit])
        return self

    def shifted(self, **kwargs):
        '''return new object'''
        return self.clone().shift(**kwargs)

    def floor(self,unit):
        if unit not in self._units:
            raise AttributeError()
        units = self._units[:self._units.index(unit)+1]
        values = [getattr(self,u) for u in units]
        return self.__class__(*values)

    def ceil(self,unit):
        if unit not in self._units:
            raise AttributeError()
        return self.floor(unit).shifted(**{unit:1,'microsecond':-1})

    def round(self,factor):
        ''' factor is seconds want round to,such as 30*60'''
        seconds = (self._dt - self._dt.min).seconds
        rounding = int((seconds+factor/2.0)) / factor * factor
        return self.shifted(seconds=rounding-seconds,microseconds=-self._dt.microsecond)

    def roundfloor(self,factor):
        ''' factor is seconds want round to,such as 30*60'''
        seconds = (self._dt - self._dt.min).seconds
        rounding = seconds / factor * factor
        return self.shifted(seconds=rounding-seconds,microseconds=-self._dt.microsecond)

    #Access
    def _get_date(self):
        return self._dt.date()

    def _set_date(self, value):
        self._dt = datetime.combine(value, self._dt.time())

    date = property(_get_date, _set_date)

    def _get_time(self):
        return self._dt.time()

    def _set_time(self, value):
        self._dt = datetime.combine(self._dt.date(), value)

    time = property(_get_time, _set_time)

    def _get_tuple(self):
        return self._dt.timetuple()

    def _set_tuple(self, value):
        self._dt = self._dt.fromtimestamp(int(time.mktime(value)))

    tuple = property(_get_tuple, _set_tuple)

    def _get_year(self):
        return self._dt.year

    def _set_year(self, value):
        self._dt = self._dt.replace(year = value)

    year = property(_get_year, _set_year)

    def _get_month(self):
        return self._dt.month

    def _set_month(self, value):
        self._dt += relativedelta(months = value - self._dt.month)

    month = property(_get_month, _set_month)

    def _get_week(self):
        delta = self._dt - datetime(self._dt.year, 1, 1)
        return delta.days / 7

    def _set_week(self, value):
        week = self._get_week()
        self._dt += timedelta(weeks = value - week)

    week = property(_get_week, _set_week)

    def _get_day(self):
        return self._dt.day

    def _set_day(self, value):
        self._dt += timedelta(days = value - self._dt.day)

    day = property(_get_day, _set_day)

    def _get_hour(self):
        return self._dt.hour

    def _set_hour(self, value):
        self._dt += timedelta(hours = value - self._dt.hour)

    hour = property(_get_hour, _set_hour)

    def _get_minute(self):
        return self._dt.minute

    def _set_minute(self, value):
        self._dt += timedelta(minutes = value - self._dt.minute)

    minute = property(_get_minute, _set_minute)

    def _get_second(self):
        return self._dt.second

    def _set_second(self, value):
        self._dt += timedelta(seconds = value - self._dt.second)

    second = property(_get_second, _set_second)

    def _get_microsecond(self):
        return self._dt.microsecond

    def _set_microsecond(self, value):
        self._dt += timedelta(microseconds = value - self._dt.microsecond)

    microsecond = property(_get_microsecond, _set_microsecond)

    @property
    def weekday(self):
        return self._dt.weekday()

    @property
    def isoweekday(self):
        return self._dt.isoweekday()

    def today(self):
        return self

    def tomorrow(self):
        return self.shifted(days=1)

    def yesterday(self):
        return self.shifted(days=-1)

    #pred method
    def is_today(self):
        return self._dt.date() == datetime.today().date()

    def is_past_date(self):
        return self._dt.date() < datetime.today().date()

    def is_future_date(self):
        return self._dt.date() > datetime.today().date()

    @property
    def timestamp(self):
        return int(time.mktime(self._dt.timetuple()))+self.microsecond/1000000.0

    @property
    def days_in_month(self):
        return calendar.monthrange(self.year, self.month)[1]

    def __add__(self, other):
        if isinstance(other, (timedelta, relativedelta)):
            return self.__class__(dt=self._dt + other)
        raise NotImplementedError()

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, timedelta):
            return self.__class__(dt=self._dt - other)
        elif isinstance(other, datetime):
            return self._dt - other
        elif isinstance(other, Sandglass):
            return self._dt - other._dt
        raise NotImplementedError()

    # comparisons
    def __eq__(self, other):
        if not isinstance(other, Sandglass):
            return False
        return self._dt == other._dt

    def __lt__(self, other):
        if not isinstance(other, Sandglass):
            return False
        return self._dt < other._dt

    #representation
    def __repr__(self):
        return '<{0} object ({1})>'.format(self.__class__.__name__, self._dt)

    def __str__(self):
        return self.__repr__()

    @property
    def sqldate(self):
        return self._dt.strftime("%Y-%m-%d")

    @property
    def sqltime(self):
        return self._dt.strftime("%H:%M:%S")

    @property
    def sql(self):
        return self.sqldate + " " + self.sqltime

    def strftime(self, fmt):
        return self._dt.strftime(fmt)

    @classmethod
    def strptime(cls, timestr, fmt):
        dt = datetime.strptime(timestr, fmt)
        return cls(dt=dt)

def ben(*args, **kwargs):
    '''
    This is a constructors to get Sandglass object.
    Which is very convenient to do conversion
    Usage:
        >>>ben()
        >>>ben(timestamp)
        >>>ben(timestr)
        >>>ben(datetime)
        >>>ben(Sandglass)
        >>>ben('2013-01-01','%Y-%m-%d')
        >>>ben(year=2013,month=2,day=8,hour=7)
    '''
    if kwargs:
        return Sandglass(*args, **kwargs)
    arg_count = len(args)
    if arg_count == 0:
        return Sandglass.now()
    if arg_count == 1:
        arg = args[0]

        if isinstance(arg, Sandglass):
            return arg.clone()

        if isinstance(arg, datetime):
            return Sandglass(dt=arg)

        if isinstance(arg,(int,float)):
            return Sandglass.fromtimestamp(arg)

        return Sandglass(dt=timeparse(arg))

    if arg_count == 2:
        date_str,fmt = args
        return Sandglass.strptime(date_str,fmt)


#sg = ben('2013,1,1')
