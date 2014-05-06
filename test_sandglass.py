#coding=utf-8
import pytest
from sandglass import *
from datetime import datetime,date,timedelta


class Test_Sandglass:
    def test_access_attr(self):
        now = datetime.now()
        sg = Sandglass(dt=now)
        assert sg.year == now.year
        assert sg.month == now.month
        assert sg.hour == now.hour
        assert sg.minute == now.minute
        assert sg.second == now.second
        assert sg.microsecond == now.microsecond
        assert sg.weekday == now.weekday()
        assert sg.isoweekday == now.isoweekday()
        assert Sandglass(year=2013,month=2,day=5).days_in_month == 28

    def test_representation(self):
        sg = Sandglass(year=2013,month=2,day=28)
        assert sg.sql == '2013-02-28 00:00:00'
        assert sg.sqldate == '2013-02-28'
        assert sg.sqltime == '00:00:00'

    def test_comparisons(self):
        sg = Sandglass(year=2013,month=2,day=28)
        sg2 = Sandglass(year=2013,month=2,day=28,hour=0)
        sg3 = Sandglass(year=2013,month=2,day=27,hour=0)
        sg4 = Sandglass(year=2013,month=3,day=1,hour=0)
        assert sg == sg2
        assert sg3 < sg4

    def test_pred(self):
        sg = Sandglass(dt=datetime.now())
        assert sg.is_today()
        assert not sg.is_past_date()
        assert not sg.is_future_date()

    def test_span(self):
        sg = Sandglass(year=2013,month=2,day=27,hour=17,minute=29,second=4,microsecond=123)
        assert sg.floor('year').sql   == '2013-01-01 00:00:00'
        assert sg.floor('month').sql  == '2013-02-01 00:00:00'
        assert sg.floor('day').sql    == '2013-02-27 00:00:00'
        assert sg.floor('hour').sql   == '2013-02-27 17:00:00'
        assert sg.floor('minute').sql == '2013-02-27 17:29:00'
        assert sg.floor('second').sql == '2013-02-27 17:29:04'

        assert sg.ceil('year').sql   == '2013-12-31 23:59:59'
        assert sg.ceil('month').sql  == '2013-02-28 23:59:59'
        assert sg.ceil('day').sql    == '2013-02-27 23:59:59'
        assert sg.ceil('hour').sql   == '2013-02-27 17:59:59'
        assert sg.ceil('minute').sql == '2013-02-27 17:29:59'
        assert sg.ceil('second').sql == '2013-02-27 17:29:04'

        assert sg.round(30*60).sql == '2013-02-27 17:30:00'
        assert sg.roundfloor(30*60).sql == '2013-02-27 17:00:00'
        sg.minute = 14
        assert sg.round(30*60).sql == '2013-02-27 17:00:00'



    def test_shift(self):
        sg = Sandglass(year=2013,month=2,day=27,hour=17,minute=29,second=4,microsecond=123)
        assert sg.shift(day=2,hour=4,minute=3,second=20).sql == '2013-03-01 21:32:24'

    def test_mock(self):
        Sandglass.mock(day=1)
        assert (Sandglass.now() - Sandglass(dt=datetime.now())).days == 1
        Sandglass.mock(minute=3,second=20)
        assert (Sandglass.now() - Sandglass(dt=datetime.now())).total_seconds() - 200 < 1
        Sandglass.unmock()
        assert (Sandglass.now() - Sandglass(dt=datetime.now())).total_seconds() < 1

class Test_ben:
    def test_xx(self):
        now = datetime.now()
        assert isinstance(ben(),Sandglass)
        assert (ben() - now).total_seconds() <1
        assert ben(0).sql == '1970-01-01 08:00:00'#in chinese time zone
        assert ben(86400).sql == '1970-01-02 08:00:00'#in chinese time zone
        #print pytest.mark.xfail((ben('20130101'),ben('2013-01-01')))#20130101 would be assume timestamp
        assert ben('2013,1,1 19:23') == ben('2013-01-01 19:23:00')
        assert ben('19:23').year == now.year
        assert ben('19:23').month == now.month
        assert ben('19:23').day == now.day
        assert ben('19:23').hour == 19
        assert ben('19:23').minute == 23
        assert ben('19:23').second == 0
        assert ben(now)._dt == now
        assert ben('2013-01-01 23','%Y-%m-%d %H') == ben('2013-01-01 23:00')
        assert ben(year=2013,month=2,day=8,hour=7).sql == '2013-02-08 07:00:00'
        assert ben('2013,1,1') == ben('2013-01,01') == ben('2013 1 01')

class Test_cronwalk:
    def test_xx(self):
        c = iter(cronwalk('0 6 * * *',base='2013-02-03'))
        assert next(c).sql == '2013-02-03 06:00:00'
        assert next(c).sql == '2013-02-04 06:00:00'

        c = iter(cronwalk('0 */2 * * *',base='2013-02-03 00:00:00'))
        assert next(c).sql == '2013-02-03 00:00:00'
        assert next(c).sql == '2013-02-03 02:00:00'
        c = iter(cronwalk('0 */2 * * *',base='2013-02-03 00:00:01'))
        assert next(c).sql == '2013-02-03 02:00:00'
        assert next(c).sql == '2013-02-03 04:00:00'

        c = iter(cronwalk('0 23-7/2 * * *',base='2013-02-03 08:30:00'))
        assert next(c).sql == '2013-02-03 23:00:00'
        assert next(c).sql == '2013-02-04 01:00:00'

        with pytest.raises(Exception):
            next(iter(cronwalk('0 0 31 2 *',base='2013-02-03')))

        c = iter(cronwalk('0 11 4 * 3-4',base='2013-02-03 08:30:00'))
        assert next(c).sql == '2013-02-04 11:00:00'
        assert next(c).sql == '2013-02-06 11:00:00'
        assert next(c).sql == '2013-02-07 11:00:00'
        assert next(c).sql == '2013-02-13 11:00:00'

        c = iter(cronwalk('0 23 * * 6',base='2013-02-03 08:30:00'))
        assert next(c).sql == '2013-02-09 23:00:00'
        assert next(c).sql == '2013-02-16 23:00:00'
        assert next(c).sql == '2013-02-23 23:00:00'


class Test_tslice:
    def test_xx(self):
        assert [x.sqldate for x in tslice('day','2013-01-01','2013-01-04')] == ['2013-01-01','2013-01-02','2013-01-03']
        assert [x.sqldate for x in tslice('day','2013-01-04','2013-01-01',step=-1)] == ['2013-01-04','2013-01-03','2013-01-02']
        assert [x.sqldate for x in tslice('day','2013-01-04','2013-01-31',step=10)] == ['2013-01-04','2013-01-14','2013-01-24']
        assert [x.sqldate for x in tslice('day','2013-01-04','2013-01-31',step=3,count=3)] == ['2013-01-04','2013-01-07','2013-01-10']
        assert [x.sqldate for x in tslice('day',count=5)] == [str(date.today() + timedelta(days=i)) for i in range(5)]
        assert [x.sqldate for x in tslice('year',start='2013-01-04',count=2)] == ['2013-01-04','2014-01-04']
        assert [x.sql for x in tslice('minute',start='2013-01-04',count=2)] == ['2013-01-04 00:00:00','2013-01-04 00:01:00']

class Test_timediff:
    def test_xx(self):
        assert timediff('20:00:00',factor=86400,base='19:30:00') == 30*60
        assert timediff('20:00:00',factor=86400,base='21:30:00') == 81000


