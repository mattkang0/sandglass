================
sandglass
================


安装
------------

可以::

    easy_install sandglass

或者::

    pip install sandglass


概览
--------

**sandglass(沙漏)** 是一个增强的、友好的时间处理库，目的是为了解放程序员的生产力。
在python中有太多处理时间的库，datetime/date/time/calendar等等。需要记的细节太多，选择困难。
而sandglass就是解决这个的青霉素。从各种麻烦的转换中解脱出来。
只需记住 **Sandglass对象** 和 **ben()** 、 **tslice()** 、 **cronwalk()** 这几个主要的api即可。


用法
-----
在sandglass中，核心对象是Sandglass对象。

**ben()** 函数用来便捷获取Sandglass对象.::

    不带参数默认是当前时间
    >>>ben()#shortcut of Sandglass.now()
    参数是时间戳
    >>>ben(timestamp)
    参数是时间字符串
    >>>ben(timestr)
    参数是datetime对象
    >>>ben(datetime)
    参数是Sandglass对象
    >>>ben(Sandglass)
    显式指明格式
    >>>ben('2013-01-01','%Y-%m-%d')
    datetime-like的构造器
    >>>ben(year=2013,month=2,day=8,hour=7)

也就是说，只要把能表达时间的东西塞给ben()就行了。
值得一说的是ben(timestr)中通过一个词法解析的东西，使得timestr可以很灵活。大体规则是，如果缺少年月日信息，则默认用当前时间的年月日；如果缺少时分秒信息，则默认是0::

    >>>ben('2013,1,1') == ben('2013-01,01') == ben('2013 1 01') == ben('2013-01-01 00:00:00')
    True
    >>>ben('2013,1,1 19:23') == ben('2013-01-01 19:23:00')
    True
    >>>now = datetime.now()
    >>>ben('19:23').year == now.year
    True
    >>>now = datetime.now()
    >>>ben('19:23').month == now.month
    True
    >>>now = datetime.now()
    >>>ben('19:23').day == now.day
    True
    >>> ben('19:23').hour,ben('19:23').minute,ben('19:23').second
    (19,23,0)

通过 **Sandglass对象** ，通过这个对象，可以方便的获取各个时间属性和操作::

    >>>sg = ben('2013,1,1 13:14:15')
    >>>sg
    <Sandglass object (2013-01-01 13:14:15)>
    >>>sg.year,sg.month,sg.day,sg.hour,sg.minute,sg.second,sg.microsecond
    (2013, 1, 1, 13, 14, 15, 0)
    >>> sg.timestamp#还能直接获取timestamp
    1357017255.0

    #便捷的获取常用的sql格式
    >>> sg.sql
    '2013-01-01 13:14:15'
    >>> sg.sqldate
    '2013-01-01'
    >>> sg.sqltime
    '13:14:15'

    #进行增量变换(shift是原地操作，而shifted返回一个新的对象)
    >>> sg.shifted(day=1,minute=-2)
    <Sandglass object (2013-01-02 13:12:15)>
    >>> sg.hour=23
    >>> sg
    <Sandglass object (2013-01-01 23:14:15)>

    >>> sg.floor('hour'),sg.ceil('hour')
    (<Sandglass object (2013-01-01 23:00:00)>, <Sandglass object (2013-01-01 23:59:59.999999)>)
    >>> sg.floor('year'),sg.ceil('year')
    (<Sandglass object (2013-01-01 00:00:00)>, <Sandglass object (2013-12-31 23:59:59.999999)>)
    >>> sg.round(30*60)
    <Sandglass object (2013-01-01 23:00:00)>
    >>> sg.roundfloor(30*60)
    <Sandglass object (2013-01-01 23:00:00)>

    #重载符号
    >>>sg3 = Sandglass(year=2013,month=2,day=27,hour=0)
    >>>sg4 = Sandglass(year=2013,month=3,day=1,hour=0)
    >>> sg3==sg4
    False
    >>> sg3<sg4
    True
    >>> sg3>sg4
    False
    >>> sg4-sg3
    datetime.timedelta(2)

    #mock当前时间，这样就测试的时候就不用改时间，直接mock给当前时间加上个偏移量就行了
    #比如我要把时间往后推一天
    >>> ben()
    <Sandglass object (2014-05-06 12:04:07.113000)>
    >>> Sandglass.mock(day=1)
    >>> ben()
    <Sandglass object (2014-05-07 12:04:38.064000)>
    >>> ben()
    <Sandglass object (2014-05-07 12:04:44.319000)>
    >>> Sandglass.unmock()
    >>> ben()
    <Sandglass object (2014-05-06 12:05:19.003000)>

    #其它
    >>> sg
    <Sandglass object (2013-01-01 23:14:15)>
    >>> sg.raw()
    datetime.datetime(2013, 1, 1, 23, 14, 15)
    >>> sg.clone()
    <Sandglass object (2013-01-01 23:14:15)>
    >>> sg.replace(day=2)
    >>> sg
    <Sandglass object (2013-01-02 23:14:15)>
    >>> sg.days_in_month
    31
    >>> sg.is_today()
    False
    >>> sg.is_past_date()
    True
    >>> sg.is_future_date()
    False
    >>> sg.strftime('%Y/%m/%d')
    '2013/01/02'
    >>> Sandglass.strptime('20130203','%Y%m%d')
    <Sandglass object (2013-02-03 00:00:00)>

**tslice** ,受内置函数xrange启发，用于获取一个时间序列。

格式是::

    tslice(unit,start=None,end=None,step=1,count=None) -> generator of Sandglass object
    unit in ['year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond']

跟xrange一样，step可以是负数。如果start为空，则默认是当前时间。

示例::

    >>>list(tslice('day','2013-01-01','2013-01-04'))
    [<Sandglass object (2013-01-01 00:00:00)>,
    <Sandglass object (2013-01-02 00:00:00)>,
    <Sandglass object (2013-01-03 00:00:00)>]

    >>>list(tslice('day','2013-01-04','2013-01-01',step=-1))
    [<Sandglass object (2013-01-04 00:00:00)>,
    <Sandglass object (2013-01-03 00:00:00)>,
    <Sandglass object (2013-01-02 00:00:00)>]

    >>>list(tslice('day','2013-01-04','2013-01-31',step=3,count=2))
    [<Sandglass object (2013-01-04 00:00:00)>,
    <Sandglass object (2013-01-07 00:00:00)>]

    >>>list(tslice('year',start='2013-01-04',count=2))
    [<Sandglass object (2013-01-04 00:00:00)>,
    <Sandglass object (2014-01-04 00:00:00)>]

    >>>list(tslice('minute',start='2013-01-04',count=2))
    [<Sandglass object (2013-01-04 00:00:00)>,
    <Sandglass object (2013-01-04 00:01:00)>]


**cronwalk** ,用于对crontab表达式进行演算，得到下一个执行的时间。

格式:: 

    cronwalk(expr,base=None)# 如果base为空，默认是当前时间。

示例::

    >>>c = iter(cronwalk('0 6 * * *',base='2013-02-03'))
    >>>next(c)
    <Sandglass object (2013-02-03 06:00:00)>
    >>>next(c)
    <Sandglass object (2013-02-04 06:00:00)>

    >>>c = iter(cronwalk('0 23-7/2 * * *',base='2013-02-03 08:30:00'))
    >>>next(c)
    <Sandglass object (2013-02-03 23:00:00)>
    >>>next(c)
    <Sandglass object (2013-02-04 01:00:00)>

**timediff** ,用于计算距离下个指定时间还有多久，比如有个活动是每天20:00:00开始的，要计算距离活动开始还有多久::

    >>>timediff('20:00:00',factor=86400,base='19:30:00')
    1800
    >>>timediff('20:00:00',factor=86400,base='21:30:00')
    81000


Todo
---------
* Add timezone support

Changelog
---------
**0.0.1**

* Initial release
