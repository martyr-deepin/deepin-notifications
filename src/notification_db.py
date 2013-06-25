#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Wang Yaohua
# 
# Author:     Wang Yaohua <mr.asianwang@gmail.com>
# Maintainer: Wang Yaohua <mr.asianwang@gmail.com>
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
import shutil
import sqlite3

def notification2tuple(notification):
    pass


class NotificationDB:
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
            self.cursor.execute('''create table notifications (id integer primary key autoincrement, time text, message text) ''')
                
    def add(self, time, notification):
        notification = cPickle.dumps(notification)
        try:
            self.cursor.execute('''insert into notifications values (?, ?, ?)''', (None, time, notification))
        except Exception, e:
            print e, "DB"
            print "Already in database."
        
    def remove(self, id):
        print "remove", id
        self.cursor.execute('''delete from notifications where id=?''', (id,))
        
    def get_all(self):
        '''
        docs
        '''
        self.cursor.execute('''select * from notifications order by time desc''')
        result = self.cursor.fetchall()
        
        return [(x[0], x[1], cPickle.loads(str(x[2]))) for x in result]
    
    def commit(self):
        self.conn.commit()
    
    def close(self):
        self.cursor.close()
        self.conn.close()
        
    def clear(self):
        self.cursor.execute('''delete from notifications''')
        
    def export_db(self, export_path):
        shutil.copy(self.db_path, export_path)
        
        
    def import_db(self, import_path):
        tmp_conn = sqlite3.connect(import_path)
        tmp_cursor = tmp_conn.cursor()
        
        result = tmp_cursor.execute("select * from notifications")
        for x in result.fetchall():
            self.add(x[0], cPickle.loads(str(x[1])))
        
    
app_data_path = os.path.join(xdg.get_config_dir(), "data")
app_db_path = os.path.join(app_data_path, "notifications.db")

db = None

if not os.path.exists(app_data_path):
    os.makedirs(app_data_path)
if not os.path.exists(app_db_path):
    db = NotificationDB(app_db_path, True)
else:
    db = NotificationDB(app_db_path, False)
