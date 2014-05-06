#coding=utf-8
from datetime import datetime

__all__ = ['timeparse']


class _lex(object):
    NUM = 1
    DOT = 2
    def __init__(self,text):
        self.nums       = '0123456789'
        self.whitespace = ' \t\r\n'
        self.charstack  = []
        self.eof        = False
        self.curindex   = 0
        self.textlen    = len(text)
        self.text       = text

    def __iter__(self):
        return self

    def next(self):
        token = None
        state = None
        nums = self.nums
        whitespace = self.whitespace
        while not self.eof:
            if self.charstack:
                nextchar = self.charstack.pop(0)
            else:
                if self.curindex >= self.textlen:
                    self.eof = True
                    break
                nextchar = self.text[self.curindex]
                self.curindex += 1
            if not state:
                token = nextchar
                if nextchar in nums:
                    state = self.NUM
                elif nextchar in whitespace:
                    token = ' '
                    break
                else:
                    break
            elif state == self.NUM:
                if nextchar in nums:
                    token += nextchar
                elif nextchar == '.':
                    token += nextchar
                    state = self.DOT
                else:
                    self.charstack.append(nextchar)
                    break
            elif state == self.DOT:
                if nextchar == '.' or nextchar in nums:
                    token += nextchar
                else:
                    self.charstack.append(nextchar)
                    break
        if token is None:
            raise StopIteration
        return token

    @classmethod
    def split(cls,s):
        return list(cls(s))

class _datetimeholder(object):
    __slots__ = ["year", "month", "day", "hour", "minute", "second", "microsecond" ]
    def __init__(self):
        for attr in self.__slots__:
            setattr(self, attr, None)

class parser(object):
    def parse(self, timestr, default=None, **kwargs):
        default = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        res = self._parse(timestr, **kwargs)
        needreplace = {attr:getattr(res,attr) for attr in res.__slots__ if getattr(res,attr) is not None}
        dt = default.replace(**needreplace)
        return dt

    def _parse(self,timestr,**kwargs):
        holder = _datetimeholder()
        tokens = _lex.split(timestr)
        #print 'tokens',tokens
        len_tokens = len(tokens)
        cur = 0
        while cur < len_tokens:
            tok = tokens[cur]
            try:
                value = float(tok)
            except ValueError:
                value = None
            if cur+1 < len_tokens and tokens[cur+1] == ':':
                holder.hour = int(value)
                cur += 2
                tok = tokens[cur]
                value = float(tok)
                holder.minute = int(value)
                if cur+2 < len_tokens and tokens[cur+1] == ':':
                    cur += 2
                    tok = tokens[cur]
                    holder.second, holder.microsecond = _split_ms(tok)
            elif cur+1 < len_tokens and tokens[cur+1] in ('-',',','/','.',' '):
                holder.year = int(value)
                cur += 2
                if cur < len_tokens:
                    holder.month = int(tokens[cur])
                    cur += 1
                    if cur < len_tokens and tokens[cur]!=':':
                        cur += 1
                        holder.day = int(tokens[cur])
            cur += 1
        return holder

def _split_ms(value):
    if '.' in value:
        second, microsecond = value.split('.')
        return int(second), int(microsecond.ljust(6, '0')[:6])
    return int(value), 0

par = parser()
def timeparse(timestr, **kwargs):
    return par.parse(timestr, **kwargs)


