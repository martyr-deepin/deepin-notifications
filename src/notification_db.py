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
import sqlite3

class NotificationDB:
    '''
    class docs
    '''
	
    def __init__(self, db_path, create=False):
        '''
        init docs
        '''
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        if create:
            self.cursor.execute('''create table notifications (time text unique, message text) ''')
                
    def add(self, time, message):
        try:
            self.cursor.execute('''insert into notifications values (?, ?)''', (time, message))
            self.conn.commit()
        except Exception, e:
            print "Already in database."
        
    def remove(self, time_id):
        self.cursor.execute('''delete from notifications where time=?''', (time_id,))
        self.conn.commit()
        
    def get_all(self):
        '''
        docs
        '''
        self.cursor.execute('''select * from notifications order by time''')
        return self.cursor.fetchall()
    
    def close(self):
        self.cursor.close()
        self.conn.close()
    
app_data_path = os.path.join(xdg.get_config_dir(), "data")
app_db_path = os.path.join(app_data_path, "notifications.db")

db = None

if not os.path.exists(app_data_path):
    os.makedirs(app_data_path)
if not os.path.exists(app_db_path):
    db = NotificationDB(app_db_path, True)
else:
    db = NotificationDB(app_db_path, False)

if __name__ == "__main__":
    db.add("time1", "message1")
    db.add("time2", "message2")
    db.add("time3", "message3")
    db.add("time4", "message4")
    
    print db.get_all()

    db.remove("time2")
    db.remove("time5")
    
    print db.get_all()
    
    db.close()
