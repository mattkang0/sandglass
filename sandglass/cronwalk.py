#coding=utf-8

__all__ = ['cronwalk']

class Entry(object):
    __slots__ = ('minute','hour','day','month','isoweekday')
    def __getitem__(self,index):
        return getattr(self,self.__slots__[index],None)
    def __setitem__(self,index,value):
        return setattr(self,self.__slots__[index],value)
    def __str__(self):
        return str({attr:getattr(self,attr,None) for attr in self.__slots__})

#from itertools import islice
import re
from sandglass import ben
class cronwalk(object):
    field_range = (
            ('minute',0,59),
            ('hour',0,23),
            ('day',1,31),
            ('month',1,12),
            ('isoweekday',0,6),
        )
    def __init__(self,expr,base=None):
        self.base = ben(base) if base else ben()
        if self.base.second or self.base.microsecond:#minute is min unit
            self.base = self.base.shift(minute=1).floor('minute')#discard second and microsecond
        self.cur = self.base.clone()
        self.entry = Entry()
        self.last_fit_year = self.cur.year
        self.range_len = {
                    'month':12,
                    'day':getattr(self.cur,'days_in_month'),
                    'isoweekday':7,
                    'hour':24,
                    'minute':60,
                }
        tokens = expr.strip().split()
        if len(tokens)!=5:
            raise Exception('invalid expr')
        self.has_day = (tokens[2] != '*')
        self.has_isoweekday = (tokens[4] != '*')
        for i,tok in enumerate(tokens):
            item_list = tok.split(',')
            res = []
            while item_list:
                item = item_list.pop(0)
                mat = re.search(r'^(\d+)-(\d+)(/(.*))?$',str(item).replace('*','{0[1]}-{0[2]}'.format(self.field_range[i])))
                if mat:
                    start,end,_,step = mat.groups()
                    step = step or 1
                    start,end,step = map(int,(start,end,step))
                    _range_start,_range_end = self.field_range[i][1:3]
                    if not _range_start<=start<=_range_end:
                        raise Exception('invalid expr')
                    if not _range_start<=end<=_range_end:
                        raise Exception('invalid expr')
                    if start>end:
                        _rotate = range(_range_start,_range_end+1)
                        _rotate = _rotate[_rotate.index(start):]+\
                                  _rotate[:_rotate.index(end)+1]
                        _list = _rotate[::step]
                    else:
                        _list = range(start,end+1,step)
                    item_list += _list
                else:
                    res.append(int(item))

            self.entry[i] = sorted(res)
        if not self.has_isoweekday:
            self.entry.isoweekday = []
        else:
            if not self.has_day:
                self.entry.day = []
        #print self.entry

    def __iter__(self):
        cur = self.cur
        entry = self.entry
        while 1:
            if cur.year - self.last_fit_year >=2:
                raise Exception('invalid expr')
            subcur = 0
            fields = ('month','day','isoweekday','hour','minute')
            entry_len = len(fields)
            while subcur<entry_len :
                field = fields[subcur]
                if field == 'day':#day and isoweekday is union-like relative
                    _diff = min(self.get_diff(cur.day,entry.day,'day'),self.get_diff(cur.isoweekday,entry.isoweekday,'isoweekday'))
                    subcur += 1
                else:
                    _diff = self.get_diff(getattr(cur,field),getattr(entry,field),field)
                if _diff:
                    old = cur.clone()
                    cur = cur.shifted(**{field:_diff})
                    changed = field
                    for m in ('month','day','hour'):
                        if getattr(cur,m) != getattr(old,m):
                            changed = m
                            break
                    cur = cur.floor(changed)
                    carry = (changed!=field)
                    if carry:#loop again,because of the carry influence the prev element and the element may not satisfy any more
                        break
                subcur += 1

            ok = True
            for k in ('month','hour','minute'):
                if getattr(cur,k) not in getattr(entry,k):
                    ok = False
                    break
            if (cur.day not in entry.day) and (cur.isoweekday not in entry.isoweekday):
                ok = False
            if ok:
                yield cur
                self.last_fit_year = cur.year
                cur = cur.shifted(**{'minute':1})

    def get_diff(self,x,seq,unit):
        if not seq:
            return float('inf')
        range_len = self.range_len[unit]
        for y in seq:
            if y>=x:
                return y-x
        _diff = (seq[0]-x)%range_len
        return _diff

