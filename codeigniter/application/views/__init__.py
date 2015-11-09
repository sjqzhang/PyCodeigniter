#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'

template='''
<!Doctype html><html xmlns=http://www.w3.org/1999/xhtml><head>
    <meta http-equiv=Content-Type content="text/html;charset=utf-8">

<!-- CSS goes in the document HEAD or added to your external stylesheet -->
<style type="text/css">
table.gridtable {
	font-family: verdana,arial,sans-serif;
	font-size:11px;
	color:#333333;
	border-width: 1px;
	border-color: #666666;
	border-collapse: collapse;
}
table.gridtable th {
	border-width: 1px;
	padding: 8px;
	border-style: solid;
	border-color: #666666;
	background-color: #dedede;
}
table.gridtable td {
	border-width: 1px;
	padding: 8px;
	border-style: solid;
	border-color: #666666;
	background-color: #ffffff;
}
</style>


<title>{{title}}</title>

</head>
<body>

<table class="gridtable">
<tr>
{% for colname  in rows[0] %}
  <th>{{ colname }}</th>
{% endfor %}
</tr>
{% for row in rows %}
  <tr>
      {% for colname  in row %}
    <td>{{ row[colname] }}</td>
       {% endfor %}
  </tr>
 {% endfor %}
</table>



</body>
</html>
'''


template='''
{% for row in rows %}
{% for colname  in row %}{{row[colname]}}       {% endfor %}{% endfor %}
'''