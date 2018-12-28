#!/usr/bin/env python
# coding: utf-8
import xmlrpclib
import xlrd

dbname = 'v10_full_equip_2'
username = 'demo@demo.com'
pwd = 'demo'

sock_common = xmlrpclib.ServerProxy ('http://propell.equip-test.co/xmlrpc/common')
sock = xmlrpclib.ServerProxy('http://propell.equip-test.co/xmlrpc/object')
uid = sock_common.login(dbname, username, pwd)

workbook = xlrd.open_workbook('users_import_v2.xlsx')
worksheet = workbook.sheet_by_name('Sheet1')
num_rows = worksheet.nrows - 1
num_cells = worksheet.ncols - 1
curr_row = 0

print "Importing Province..."
count = 0
while curr_row < num_rows:
    curr_row += 1

    row = worksheet.row(curr_row)
    data = {'name': row[0].value, 'login': row[1].value, 'password': row[1].value}
    # print data
    user_id = sock.execute(dbname, uid, pwd, 'res.users', 'search', [('login','=',row[1].value)])
    print ">>>>>>>>>>>>>>>>>",user_id,row[1].value
    if not user_id:
        user_id = sock.execute(dbname, uid, pwd, 'res.users', 'create', data)
    count = count + 1    

    access_group_id = sock.execute(dbname, uid, pwd, 'access.rights.group', 'search', [('name','=',row[15].value)])

    if access_group_id:
        sock.execute(dbname, uid, pwd, 'res.users', 'write', user_id,{'access_rights_id': access_group_id[0]})
    else:
        print "Not found this records",row[15].value
        
    print count,user_id
print "End***************"

