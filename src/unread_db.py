#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang YaoHua
# 
# Author:     Wang YaoHua <mr.asianwang@gmail.com>
# Maintainer: Wang YaoHua <mr.asianwang@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
import xdg
import cPickle
import sqlite3

class UnreadDB:
    '''
    class docs
    '''
	
    def __init__(self, db_path, create=False):
        '''
        init docs
        '''
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        if create:
            self.cursor.execute('''create table unread_notifications 
(id integer primary key autoincrement, time text, message text) ''')
                
    def add(self, time, message):
        message = cPickle.dumps(message)
        try:
            self.cursor.execute('''insert into unread_notifications values (?, ?, ?)''', (None, time, message))
        except Exception, e:
            print e, "UNREAD"
            print "Already in database."
        
    def remove(self, id):
        self.cursor.execute('''delete from unread_notifications where id=?''', (id,))
        
    def get_all(self):
        '''
        docs
        '''
        self.cursor.execute('''select * from unread_notifications order by time desc''')
        result = self.cursor.fetchall()
        
        return [(x[0], x[1], cPickle.loads(str(x[2]))) for x in result]
    
    def commit(self):
        self.conn.commit()
    
    def close(self):
        self.cursor.close()
        self.conn.close()
        
    def clear(self):
        self.cursor.execute('''delete from notifications''')
        
    
app_data_path = os.path.join(xdg.get_config_dir(), "data")
app_unread_db_path = os.path.join(app_data_path, "unread_notifications.db")

unread_db = None

if not os.path.exists(app_data_path):
    os.makedirs(app_data_path)
if not os.path.exists(app_unread_db_path):
    unread_db = UnreadDB(app_unread_db_path, True)
else:
    unread_db = UnreadDB(app_unread_db_path, False)
