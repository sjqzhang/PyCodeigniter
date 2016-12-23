#coding=utf-8
#!/usr/bin/python


import re
import json

class Expr:
    def __init__(self, expr):
        self.op_map = {
            '=': self._equal_,
            '!=': self._not_equal,
            '<>': self._not_equal,
            ' like ': self._like,
            ' in ':self._in
        }
        self.key, self.op, self.val = self.__parser(expr)
        self.func = self.op_map[self.op]

    def __parser(self, expr):
        op = map(lambda x: [expr.find(x), x], filter(lambda x: x in expr, self.op_map.keys()))
        assert len(op) >= 1

        op = min(op)
        return str(expr[:op[0]]).strip().lower(), str(op[1]), str(expr[op[0] + len(op[1]):]).strip().lower()

    def _equal_(self, fst_val, sec_val):
        return fst_val == sec_val

    def _like(self,fst_val,sec_val):
        return fst_val in sec_val

    def _in(self,fst_val,sec_val):
        # return False
        sec_val=re.sub(r'^\[|\]$','',sec_val)
        return fst_val in sec_val.split(',')



    def _not_equal(self, fst_val, sec_val):
        return fst_val != sec_val

    def compute(self, data_dict):
        v=data_dict.get(self.key, '')
        if isinstance(v,unicode):
            v = v.encode('utf-8')
        if isinstance(v,list):
            if '_in' == self.func.__name__:
                return self.val in v
        sec_val = str(v).lower()
        return self.func(self.val, sec_val)


class Matcher:
    def __init__(self, pattern_expr='',**kwargs):
        def tmp(a):
            if isinstance(a.group(0),unicode):
                return ('('+(a.group(0)).encode("utf-8").replace("'",'')+')').decode('utf-8')
            else:
                return ('('+(a.group(0)).replace("'",'')+')').decode('utf-8')
        pattern_expr=re.sub(r'(\w+\s*(=|like|in)\s*[\'](?:[^\']+)[\'])|(\w+\s*(=|like|in)\s*(?:[^\s]+)\s*)',tmp,pattern_expr)
        pattern_expr=pattern_expr.encode('utf-8')
        self.raw_pattern_expr = pattern_expr
        self.postfix_expr_list = self.__translate_to_postfix_expr(pattern_expr)


    def __is_startswith_op(self, pattern_expr):
        if pattern_expr.startswith('('):
            return True, '(', pattern_expr[1:]
        elif pattern_expr.startswith('or'):
            return True, 'or', pattern_expr[2:]
        elif pattern_expr.startswith('and'):
            return True, 'and', pattern_expr[3:]
        else:
            return False, '', pattern_expr

    def __translate_to_postfix_expr(self, pattern_expr):
        postfix_expr_list = []
        tmp_stack = []

        while True:
            pattern_expr = pattern_expr.strip()
            if len(pattern_expr) <= 0:
                break

            is_op, op, pattern_expr = self.__is_startswith_op(pattern_expr)
            if is_op:
                tmp_stack.append(op)
            else:
                idx = pattern_expr.find(')')
                if idx != 0:
                    postfix_expr_list.append(Expr(pattern_expr if idx == -1 else pattern_expr[:idx]))
                pattern_expr = pattern_expr[idx + 1:]

                while True:
                    t = tmp_stack.pop()
                    if t == '(':
                        break
                    postfix_expr_list.append(t)

        while len(tmp_stack) > 0:
            postfix_expr_list.append(tmp_stack.pop())

        # print postfix_expr_list
        return postfix_expr_list


    def calc(self, data_dict):
        tmp_list = []
        for i in range(len(self.postfix_expr_list)):
            op = self.postfix_expr_list[i]
            if isinstance(op, Expr):
                tmp_list.append(op.compute(data_dict))
            else:
                fst_val = tmp_list.pop()
                sec_val = tmp_list.pop()
                tmp_list.append((fst_val and sec_val) if op == 'and' else (fst_val or sec_val))
        return tmp_list[0]

    @classmethod
    def query(self,list_data=[],select='*',where='',order='',group=''):
        '''
        :param data: dict
        :param sql: select columnname1,columnname2,columnname3 where columnname1 like 'xx'
        :return:
        '''
        if isinstance(select,unicode):
            select=select.encode('utf-8')
        cols=map(str.strip, select.split(','))

        if isinstance(where,unicode):
            where=where.encode('utf-8','ignore')
        match=Matcher(where)

        if isinstance(list_data,list):
            rows=list_data
        elif isinstance(list_data,dict):
            rows=[list_data]
        elif isinstance(list_data,unicode):
            rows=json.loads(unicode.encode(list_data,'utf-8','ignore'))
        elif isinstance(list_data,basestring):
            row=json.loads(list_data)
        if where!='':
            rows=filter(lambda row: match.calc(row), rows)

        result=[]

        if select=='*':
            result=rows
        else:
            for row in rows:
                irow={}
                for c in cols:
                    if c not in row.keys():
                        irow[c]=None
                    else:
                        irow[c]=row[c]
                result.append(irow)
        rows=result
        if len(rows)==0:
            return rows

        if order=='':
            return  rows
        orders=order.split(',')



        def icmp(x, y):
            for i, k in enumerate(orders):
                kk=k.split()

                # print len(kk)
                # print kk
                desc = 'asc'
                if len(kk)==2:
                    desc=kk[1]
                fst = x[kk[0]]
                sec = y[kk[0]]

                if cmp(fst, sec) == 0:
                    # return 0
                    continue
                else:
                    if desc == 'desc':
                        return -cmp(fst, sec)
                    else:
                        return cmp(fst, sec)
            return 0


        rows.sort(cmp=icmp)
        return rows


        # list.sort()
        # return sorted(rows,cmp=icmp)




class DictUtil(object):
    def __init__(self,*args,**kwargs):
        self.match=Matcher()

    def query(self,data=[],select='',where='',order='',group=''):
        return self.match.query(data,select=select,where=where,order=order,group=group)







if __name__=='__main__':
    m=Matcher("aa=10 or bb=20")
    # print m.calc({'aa':10})
    # print m.query( json.dumps([{'aa':"你好"}]),"select aa,bb,cc where aa=你好")
    #print m.query( [{'aa':"aa"}],"select aa,bb,cc where aa=xx")
    students = [{'name':'a', 'tag':'y', 'score':18}, {'name':'a', 'tag':'z', 'score':17}, {'name':'w', 'tag':'x', 'score':15,'level':[1,2,3]}]
    # ds=DictRecord(students)
    # print ds.order('name desc').get()

    #m.query(students,"select name where id=xx and")

    import time
    s=time.time()
    m.query(students*100000,'name,tag',where='(name=a and tag=x) or level in 1',order='name desc , tag asc')
    print(time.time()-s)
