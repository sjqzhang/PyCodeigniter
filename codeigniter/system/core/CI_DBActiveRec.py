#!/usr/bin/env python
#-*- coding:utf-8 -*-
__author__ = 'writed by linzhonghong modify by xiangzhang'

import re
# import pymysql
# from pymysql import converters
#
# from CI_DB import *





class CI_DBActiveRec():
    ar_select = list()
    ar_distinct = False
    ar_from = list()
    ar_join = list()
    ar_where = list()
    ar_like = list()
    ar_groupby = list()
    ar_having = list()
    ar_keys = list()
    ar_limit = False
    ar_offset = False
    ar_order = False
    ar_orderby = list()
    ar_set = dict()
    ar_wherein = list()
    ar_aliased_tables = list()
    ar_stroe_array = list()

    # Active Record Caching variables
    ar_caching = False
    ar_cache_exists = list()
    ar_cache_select = list()
    ar_cache_from = list()
    ar_cache_join = list()
    ar_cache_where = list()
    ar_cache_like = list()
    ar_cache_groupby = list()
    ar_cache_having = list()
    ar_cache_orderby = list()
    ar_cache_set = list()

    ar_no_escape = list()
    ar_cache_no_escape = list()

    # Private variables
    _protect_identifiers_ = True
    _reserved_identifiers = ['*'] # Identifiers that should NOT be escaped
    _escape_char = '`'
    _random_keyword = ' RAND()'
    _count_string = 'SELECT COUNT(*) AS '

    def __init__(self,**kwargs):
        self._reset_select()
        self._reset_write()
        self.ESCAPE_REGEX = re.compile(r"[\0\n\r\032\'\"\\]")
        #super(CI_DBActiveRec,self).__init__(**kwargs)
        #super(DBActiveRec, self).__init__(cursorclass=cursorclass)

        self.conn=None

        self.db=None
        self.auto_close=None

        # self.app=kwargs['app']
        # if 'conn' in kwargs.keys():
        #     self.conn=kwargs['conn']
        # if 'auto_close' in kwargs.keys():
        #     self.auto_close=kwargs['auto_close']
        # else:
        #     self.auto_close=True

    def query(self,sql,param=tuple()):
        try:
            if self.conn==None:
                self.conn=self.db.get_connection()
                self.auto_close=True
            return self.db.query(sql,param=param,conn=self.conn,auto_commit=self.auto_close)
        finally:
            pass
            # if self.auto_close:
            #     self.db.commit(self.conn)
                # self.conn.close()


        # if self.auto_close:
        #     # self.conn.close()
        #     return self.app.db.query(sql,param=param)
        # else:
        #     return self.app.db.query(sql,param=param,conn=self.conn)

    def __getattr__(self, in_field):
        dynamic_properties = ["find_by_", "delete_by_"]
        query = None

        for idx, prop in enumerate(dynamic_properties):
            if in_field.startswith(prop):
                size_of_query = len(dynamic_properties[idx])
                field = in_field[size_of_query:]
                query = in_field[:size_of_query]
                break
        if query is None:
            raise AttributeError(in_field)
        dynamic_query = {
            "find_by_": lambda value, table='': self._find(field, value, table)
        }[query]
        return dynamic_query

    def _find(self, field, value, table):
        if table == '':
            self.error_msg = 'db must set table'
            return False
        self.from_(table)
        self.where(field, value)
        return self.get()


    def select(self, select='*', escape=None):
        if isinstance(select, str):
            select = select.split(',')
        for val in select:
            val = val.strip()
            if val != '':
                self.ar_select.append(val)
                self.ar_no_escape.append(escape)
                if self.ar_caching:
                    self.ar_cache_select.append(val)
                    self.ar_cache_exists.append('select')
                    self.ar_cache_no_escape.append(escape)
        return self

    def select_max(self, select='', alias=''):
        return self._max_min_avg_sum(select, alias, 'MAX')

    def select_min(self, select='', alias=''):
        return self._max_min_avg_sum(select, alias, 'MIN')

    def select_avg(self, select='', alias=''):
        return self._max_min_avg_sum(select, alias, 'AVG')

    def select_sum(self, select='', alias=''):
        return self._max_min_avg_sum(select, alias, 'SUM')

    def _max_min_avg_sum(self, select='', alias='', _type='MAX'):
        if type(select) != type('') or select == '':
            print('db_invalid_query')
            return
        _type = _type.upper()
        if _type not in ['MAX', 'MIN', 'AVG', 'SUM']:
            print('Invalid function type: %s' % _type)
            return
        if alias == '':
            alias = self._create_alias_from_table(select.strip())
        sql = _type+'('+self._protect_identifiers(select.strip())+') AS '+alias
        self.ar_select.append(sql)

        if self.ar_caching is True:
            self.ar_cache_select.append(sql)
            self.ar_cache_exists.append('select')

        return self

    def _create_alias_from_table(self, item):
        if item.find('.') != -1:
            return item.split('.')[-1]
        return item

    def distinct(self, val=True):
        self.ar_distinct = val if isinstance(val, bool) else True
        return self

    def table(self,from_str):
        return self.from_(from_str)
    def _from(self,from_str):
        return self.from_(from_str)

    def from_(self, from_str):
        if isinstance(from_str, str):
            from_str = from_str.split(',')
        for val in from_str:
            v = val.strip()
            self._track_aliases(v)
            self.ar_from.append(self._protect_identifiers(v, True, None, False))
            if self.ar_caching:
                self.ar_cache_from.append(self._protect_identifiers(v, True, None, False))
                self.ar_cache_exists.append('from')
        return self

    def join_(self, table, cond, _type=''):
        if _type != '':
            _type = _type.strip().upper()
            if _type not in ['LEFT', 'RIGHT', 'OUTER', 'INNER', 'LEFT OUTER', 'RIGHT OUTER']:
                _type = ''
            else:
                _type += ' '
        self._track_aliases(table)

        match = re.match(r'([\w\.]+)([\W\s]+)(.+)', cond)
        if match:
            cond = "%s%s%s" % (self._protect_identifiers(match.group(1)),
                                match.group(2), self._protect_identifiers(match.group(3)))

        _join = _type+'JOIN '+self._protect_identifiers(table, True, None, False)+' ON '+cond
        self.ar_join.append(_join)
        if self.ar_caching is True:
            self.ar_cache_join.append(_join)
            self.ar_cache_exists.append('join')

        return self

    def where(self, key, value=None, escape=True):
        return self._where(key, value, 'AND ', escape)

    def or_where(self, key, value=None, escape=True):
        return self._where(key, value, 'OR ', escape)

    def _where(self, key, value=None, type='AND ', escape=None):
        if not isinstance(key, dict):
            key = {key: value}
        for k, v in key.iteritems():
            prefix = '' if (len(self.ar_where) == 0 and len(self.ar_cache_where) == 0) else type
            if (v is None) and (not self._has_operator(k)):
                k += ' IS NULL'
            if v:
                if escape is True:
                    k = self._protect_identifiers(k, False, escape)
                    v = ' %s'%self.escape(v)
                if not self._has_operator(k):
                    k += ' = '
            else:
                k = self._protect_identifiers(k, False, escape)
            self.ar_where.append('%s%s%s' % (prefix, k, v))
            if self.ar_caching:
                self.ar_cache_where.append('%s%s%s' % (prefix, k, v))
                self.ar_cache_exists.append('where')
        return self

    def where_in(self, key=None, values=None):
        return self._where_in(key, values)

    def or_where_in(self, key=None, values=None):
        return self._where_in(key, values, False, 'OR ')

    def where_not_in(self, key=None, values=None):
        return self._where_in(key, values, True)

    def or_where_not_in(self, key=None, values=None):
        return self._where_in(key, values, True, 'OR ')

    def _where_in(self, key=None, values=None, not_=False, type='AND '):
        if key is None or values is None:
            return
        if not isinstance(values, (list, tuple)):
            values = list(values)
        not_ = ' NOT' if not_ else ''
        for value in values:
            self.ar_wherein.append(self.escape(value))

        prefix = '' if len(self.ar_where)==0 else type
        where_in = prefix + self._escape_identifiers(key) + not_ + " IN (" + ', '.join(self.ar_wherein) + ") "
        self.ar_where.append(where_in)
        if self.ar_caching:
            self.ar_cache_where.append(where_in)
            self.ar_cache_exists.append('where')

        self.ar_wherein = list()
        return self

    def like(self, field, match='', side='both'):
        return self._like(field, match, 'AND ', side)

    def not_like(self, field, match='', side='both'):
        return self._like(field, match, 'AND ', side, 'NOT')

    def or_like(self, field, match='', side='both'):
        return self._like(field, match, 'OR ', side)

    def or_not_like(self, field, match='', side='both'):
        return self._like(field, match, 'OR ', side, 'NOT')

    def _like(self, field, match='', _type='AND ', side='both', not_=''):
        if not isinstance(field, dict):
            field = {field: match}
        for k, v in field.iteritems():
            k = self._protect_identifiers(k)
            prefix = "" if len(self.ar_like)==0 else _type
            # v = self.escape_like_str(v)
            # print(v)
            if side == 'none':
                like_statement = prefix+" %s %s LIKE '%s'" % (k, not_, v)
            elif side == 'before':
                like_statement = prefix+" %s %s LIKE '%%%s'" % (k, not_, v)
            elif side == 'after':
                like_statement = prefix+" %s %s LIKE '%s%%'" % (k, not_, v)
            else:
                like_statement = prefix+" %s %s LIKE '%%%s%%'" % (k, not_, v)

            self.ar_like.append(like_statement)
            if self.ar_caching is True:
                self.ar_cache_like.append(like_statement)
                self.ar_cache_exists.append('like')
        return self

    def group_by(self, by):
        if isinstance(by, str):
            by = by.split(',')
        for val in by:
            val = val.strip()
            if val != '':
                self.ar_groupby.append(self._protect_identifiers(val))
                if self.ar_caching is True:
                    self.ar_cache_groupby.append(self._protect_identifiers(val))
                    self.ar_cache_exists.append('groupby')
        return self

    def having(self, key, value='', escape=True):
        return self._having(key, value, 'AND ', escape)

    def or_having(self, key, value='', escape=True):
        return self._having(key, value, 'OR ', escape)

    def _having(self, key, value='', _type='AND ', escape=True):
        if type(key) != type(dict):
            key = {key: value}
        for k, v in key:
            prefix = '' if len(self.ar_having)==0 else _type
            if escape is True:
                k = self._protect_identifiers(k)
            if not self._has_operator(k):
                k += ' = '
            if v != '':
                v = ' '+self.escape(v)
            self.ar_having.append(prefix+k+v)
            if self.ar_caching is True:
                self.ar_cache_having.append(prefix+k+v)
                self.ar_cache_exists.append('having')
        return self

    def order_by(self, orderby, direction=''):
        if direction.lower() == 'random':
            orderby = ''
            direction = self._random_keyword
        elif direction.strip() != '':
            direction += ' %s'%(direction if direction.strip().upper() in ['ASC', 'DESC'] else 'ASC')

        if orderby.find(',') != -1:
            temp = list()
            for part in orderby.split(','):
                part = part.strip()
                if part in self.ar_aliased_tables:
                    part = self._protect_identifiers(part)
                temp.append(part)
            orderby = ', '.join(temp)
        elif direction != self._random_keyword:
            orderby = self._protect_identifiers(orderby)

        orderby_statement = orderby+direction
        self.ar_orderby.append(orderby_statement)
        if self.ar_caching is True:
            self.ar_cache_orderby.append(orderby_statement)
            self.ar_cache_exists.append('orderby')

        return self

    def limit(self, value, offset=''):
        self.ar_limit = int(value)
        if offset != '':
            self.ar_offset = int(offset)
        return self

    def offset(self, offset):
        self.ar_offset = int(offset)
        return self

    def set_(self, key, value='', escape=True):
        if not isinstance(key, dict):
            key = {key: value}
        for k, v in key.iteritems():
            if escape is False:
                self.ar_set[self._protect_identifiers(k)] = v
            else:
                self.ar_set[self._protect_identifiers(k, False, True)] = self.escape(v)
        return self

    def escape_str(self, string, like = False):
        """
         * Escape String
         *
         * @access  public
         * @param   string
         * @param   bool    whether or not the string will be used in a LIKE condition
         * @return  string
        """

        if isinstance(string, dict):
            for key,val in string.iteritems():
                string[key] = self.escape_str(val, like)
            return string


        # if self._conn:
        #     string = self.mysql_real_escape_string(string)
        # else:
        #     string = ''.join({'"':'\\"', "'":"\\'", "\0":"\\\0", "\\":"\\\\"}.get(c, c) for c in string)

        string = ''.join({'"':'\\"', "'":"\\'", "\0":"\\\0", "\\":"\\\\"}.get(c, c) for c in string)

        # escape LIKE condition wildcards
        if like == True:
            string = string.replace('%', '\\%')
            string = string.replace('_', '\\_')

        return string

    def escape(self, str_):
        if isinstance(str_, str):
            str_ = self.escape_str(str_)
        elif isinstance(str_, bool):
            str_ = str(int(str_))
        elif str_ == '':
            str_ = 'NULL'
        return "'%s'" % str_

    def escape_like_str(self, str_):
        return self.escape_str(str_,True)


    # def escape(self, str_):
    #     if isinstance(str_, basestring):
    #         str_ = converters.escape_str(str_)
    #     elif isinstance(str_, bool):
    #         str_ = converters.escape_bool(str_)
    #     elif str_ == '':
    #         str_ = converters.escape_None(str_)
    #     return str_
    #
    # def escape_like_str(self, str_):
    #     return converters.escape_str(str_)

    def _escape_identifiers(self, item):
        """
        This function escapes column and table names
        @param item:
        """
        if self._escape_char == '':
            return item

        for field in self._reserved_identifiers:
            if item.find('.%s' % field) != -1:
                _str = "%s%s" % (self._escape_char, item.replace('.', '%s.' % self._escape_char))
                # remove duplicates if the user already included the escape
                return re.sub(r'[%s]+'%self._escape_char, self._escape_char, _str)

        if item.find('.') != -1:
            _str = "%s%s%s" % (self._escape_char, item.replace('.', '%s.%s'%(self._escape_char, self._escape_char)),
            self._escape_char)
        else:
            _str = self._escape_char+item+self._escape_char
        # remove duplicates if the user already included the escape
        return re.sub(r'[%s]+'%self._escape_char, self._escape_char, _str)

    def _protect_identifiers(self, item, prefix_single=False, protect_identifiers=None, field_exists=True):
        """

        @param item:
        @param prefix_single:
        @param protect_identifiers:
        @param field_exists:
        """
        if not isinstance(protect_identifiers, bool):
            protect_identifiers = self._protect_identifiers_

        if isinstance(item, dict):
            escaped_dict = dict()
            for k, v in item.iteritems():
                escaped_dict[self._protect_identifiers(k)] = self._protect_identifiers(v)
            return escaped_dict

        # Convert tabs or multiple spaces into single spaces

        # r'(\s*|<|>|!|=|is null|is not null)'
        item = re.sub(r'[\t ]+', ' ', item)
        item = re.sub(r'(\w+)(\s*|<|>|!|=|is null|is not null)', r'\1 \2', item)

        if item.find(' ') != -1:
            alias = item[item.find(' '):]
            item = item[0:item.find(' ')]
        else:
            alias = ''

        if item.find('(') != -1:
            return item+alias

        if item.find('.') != -1:
            parts = item.split('.')
            if parts[0] in self.ar_aliased_tables:
                if protect_identifiers is True:
                    for key, val in enumerate(parts):
                        if val not in self._reserved_identifiers:
                            parts[key] = self._escape_identifiers(val)
                    item = '.'.join(parts)
                return item+alias
            if protect_identifiers is True:
                item = self._escape_identifiers(item)
            return item+alias
        if protect_identifiers is True and item not in self._reserved_identifiers:
            item = self._escape_identifiers(item)
        return item+alias



    def _has_operator(self, str_):
        ret=re.search(r'(\*<|>|!|=|is null|is not null)', str_.strip(), re.IGNORECASE)
        if ret==None or ret.group().strip()=='':
            return False
        return True

    def get(self, table='', limit=None, offset=''):
        if table != '':
            self._track_aliases(table)
            self.from_(table)

        if limit is not None:
            self.limit(limit, offset)

        sql = self._compile_select()
        result = self.query(sql)
        self._reset_select()
        return result

    def to_sql(self, table='', limit=None, offset=''):
        if table != '':
            self._track_aliases(table)
            self.from_(table)

        if limit is not None:
            self.limit(limit, offset)

        sql = self._compile_select()
        return sql

    def to_where(self):
        return self.ar_cache_where


    def insert(self, table='', _set=None):
        self._merge_cache()
        if _set is not None:
            self.set_(_set)

        if len(self.ar_set) == 0:
            self.error_msg = 'insert columns and values are empty'
            return False

        if table == '':
            self.error_msg = 'db must set table'
            return False

        sql = self._insert(self._protect_identifiers(table, True, None, False), self.ar_set.keys(), self.ar_set.values())

        self._reset_write()
        return self.query(sql)


    def insert_safe(self,table='', _set=None):
        if len(_set) == 0:
            self.error_msg = 'insert columns and values are empty'
            return False
        if table == '':
            self.error_msg = 'db must set table'
            return False
        sql= """INSERT INTO %s
                (%s)
                VALUES (%s);
        """ % (
            self._protect_identifiers(table, True, None, False),
            ', '.join(map(lambda x:'`'+str(x)+'`' ,_set.keys())),
            ', '.join(map(lambda x:':'+str(x) ,_set.keys()))
        )
        self._reset_write()
        return self.query(sql,_set)




    def _insert(self, table, keys, values):

        # for i in range(0,len(values)):
        #     values[i]=str(values[i])

        return """INSERT INTO %s
                (%s)
                VALUES (%s);
        """ % (
            table,
            ', '.join(keys),
            ', '.join(values)
        )

    def replace(self, table, _set=None):
        self._merge_cache()
        if _set is not None:
            self.set_(_set)

        if len(self.ar_set) == 0:
            self.error_msg = 'replace columns and values are empty'
            return False

        if table == '':
            self.error_msg = 'db must set table'
            return False

        sql = self._replace(self._protect_identifiers(table, True, None, False), self.ar_set.keys(), self.ar_set.values())
        self._reset_write()
        return self.query(sql)

    def _replace(self, table, keys, values):
        # for i in range(0,len(values)):
        #     values[i]=str(values[i])

        return """REPLACE INTO %s
                (%s)
                VALUES (%s);
        """ % (
            table,
            ', '.join(keys),
            ', '.join(values)
        )

    def update(self, table='', _set=None, where=None, limit=None):
        self._merge_cache()
        if _set is not None:
            self.set_(_set)

        if len(self.ar_set) == 0:
            self.error_msg = 'update columns and values are empty'
            return False

        if table == '':
            self.error_msg = 'db must set table'
            return False

        if where is not None:
            self.where(where)
        if limit is not None:
            self.limit(limit)
        sql = self._update(self._protect_identifiers(table, True, None, False), self.ar_set, self.ar_where, self.ar_orderby, self.ar_limit)
        self._reset_write()
        return self.query(sql)


    def update_safe(self, table='', _set=None, where=None, limit=None):
        if where==None:
            raise Exception('WHERE IS None')
        if isinstance(where,dict):
            sql='''
            UPDATE %s SET %s
            WHERE %s
            '''%(self._protect_identifiers(table, True, None, False),','.join(map(lambda x:'`'+x+'`=:'+x,_set.keys())),
                 ' and '.join(map(lambda x:'`'+x+'`=:'+x,where.keys())),)
            _set.update(where)
            self.query(sql,_set)
        else:
            raise Exception('WHERE must be dict')





    def _update(self, table, values, where, orderby=None, limit=False):
        valstr = []
        for key in values.keys():
            value=values[key]
            valstr.append(key+' = '+value)
        limit = ' LIMIT %s' % limit if limit is not False else ''
        if not isinstance(orderby, (list, tuple)):
            orderby = ''
        else:
            orderby = ' ORDER BY %s' % ', '.join(orderby) if len(orderby)>=1 else ''
        sql = "UPDATE "+table+" SET "+', '.join(valstr)
        where = " WHERE "+' '.join(where) if where != '' and len(where)>=1 else ''
        sql += where
        sql += orderby+limit
        return sql

    def delete(self, table='', where='', limit=None, reset_data=True):
        self._merge_cache()
        if table == '':
            self.error_msg = 'db must set table'
            return False
        elif isinstance(table, (list, tuple)):
            for single_table in table:
                self.delete(single_table, where, limit, False)
            self._reset_write()
            return True
        else:
            table = self._protect_identifiers(table, True, None, False)

        if where != '':
            self.where(where)
        if limit is not None:
            self.limit(limit)

        if len(self.ar_where) == 0 and len(self.ar_wherein) == 0 and len(self.ar_like) == 0:
            self.error_msg = 'db del must use where'
            return False

        sql = self._delete(table, self.ar_where, self.ar_like, self.ar_limit)

        if reset_data:
            self._reset_write()
        return self.query(sql)

    def _delete(self, table, where=None, like=None, limit=False):
        conditions = ''
        if (isinstance(where, (list, tuple)) and len(where) > 0) or (isinstance(like, (list, tuple)) and len(like) > 0):
            conditions = "\nWHERE "
            conditions += "\n".join(self.ar_where)
            if (isinstance(where, (list, tuple)) and len(where) > 0) and (isinstance(like, (list, tuple)) and len(like) > 0):
                conditions += " AND "
            conditions += "\n".join(like)
        limit = ' LIMIT %s' % limit if limit is not False else ''

        return "DELETE FROM "+table+conditions+limit


    def _track_aliases(self, table):
        if isinstance(table, (list, tuple)):
            for t in table:
                self._track_aliases(t)
            return
        if table.find(',') != -1:
            return self._track_aliases(table.split(','))

        if table.find(" ") != -1:
            table = re.sub(r'\s+AS\s+', ' ', table, flags=re.I)
            table = table[table.rfind(" ")].strip()
            if table not in self.ar_aliased_tables:
                self.ar_aliased_tables.append(table)

    def _compile_select(self, select_override=None):
        self._merge_cache()
        if select_override:
            sql = select_override
        else:
            sql = 'SELECT ' if not self.ar_distinct else 'SELECT DISTINCT '
            if len(self.ar_select) == 0:
                sql += '*'
            else:
                for key, val in enumerate(self.ar_select):
                    try:
                        no_escape = self.ar_no_escape[key]
                    except:
                        no_escape = None
                    self.ar_select[key] = self._protect_identifiers(val, False, no_escape)
                sql += ', '.join(self.ar_select)

        if len(self.ar_from) > 0:
            sql += "\nFROM "
            sql += ', '.join(self.ar_from)

        if len(self.ar_join) > 0:
            sql += "\n"
            sql += "\n".join(self.ar_join)

        if len(self.ar_where) > 0:
            sql += "\nWHERE "
            sql += '\n'.join(self.ar_where)

        if len(self.ar_like) > 0:
                    if len(self.ar_where) > 0:
                        sql += "\nAND "
                    else:
                        sql += "\nWHERE "
                    sql += "\n".join(self.ar_like)


        if len(self.ar_groupby) > 0:
            sql += "\nGROUP BY "
            sql += '\n'.join(self.ar_groupby)

        if len(self.ar_having) > 0:
            sql += "\nHAVING "
            sql += '\n'.join(self.ar_having)

        if len(self.ar_orderby) > 0:
            sql += "\nORDER BY "
            sql += '\n'.join(self.ar_orderby)
            if self.ar_order is not False:
                sql += ' DESC' if self.ar_order == 'desc' else ' ASC'

        if type(self.ar_limit) == int:
            sql += "\n"
            sql = self._limit(sql, self.ar_limit, self.ar_offset)

        return sql

    def _limit(self, sql, limit, offset):
        if offset == 0:
            offset = ''
        else:
            offset = "%s, " % offset

        return sql+"LIMIT %s%s"%(offset, limit)

    def _merge_cache(self):
        self.ar_variable = dict()
        if len(self.ar_cache_exists) == 0:
            return
        for val in self.ar_cache_exists:
            ar_variable = 'ar_' + val
            ar_cache_var = 'ar_cache_' + val
            if len(getattr(self, ar_cache_var)) == 0:
                continue
            self.ar_variable.update({ar_cache_var: ar_variable})
        self.ar_no_escape = self.ar_cache_no_escape

    def _reset_select(self):
        self.ar_select = list()
        self.ar_from = list()
        self.ar_join = list()
        self.ar_where = list()
        self.ar_like = list()
        self.ar_groupby = list()
        self.ar_having = list()
        self.orderby = list()
        self.wherein = list()
        self.ar_no_escape = list()
        self.ar_distinct = False
        self.ar_limit = False
        self.ar_offset = False
        self.ar_order = False

    def _reset_write(self):
        self.ar_set = {}
        self.ar_from = list()
        self.ar_where = list()
        self.ar_like = list()
        self.ar_groupby = list()
        self.ar_keys = list()
        self.ar_limit = False
        self.ar_order = False

if __name__ == '__main__':
    db={}
    db['default']={}
    db['default']['host'] = '172.16.132.230';
    db['default']['user'] = 'root';
    db['default']['passwd'] = 'root';
    db['default']['database'] = 'test';
    db['default']['maxconnections'] = 3;
    db['default']['blocking'] = True;
    # dbc = DBActiveRec(**db['default'])
    # res = dbc.select('*').from_('z_task').where({'task_uuid': 'd291425d-8e9f-e90f-8298-0c96d50c7a87', 'task_type':3}).get()
    # print(res
    # res = dbc.select(['task_id', 'task_type', 'task_ip']).where(
    #     {'task_uuid !=': 'd291425d-8e9f-e90f-8298-0c96d50c7a87'}
    # ).get('z_task')
    # print(res
    # print(dbc.select("*").from_("hyrd").limit(200).get())
    # print(dbc.last_query()
