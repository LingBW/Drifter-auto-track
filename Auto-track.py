# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 12:39:03 2015

@author: bling
"""

#import pytz
import time
from datetime import datetime

print 'Automatic run at 19:00 PM(local) everyday.'
q = 0; a = 0
while q<2880:# 24*60
    q+=1
    nowtime = datetime.now()
    etime = nowtime.strftime('%m/%d/%Y %H')
    
    if int(etime[-2:]) == 19:      
        while a<100:
            a+=1
            nowtime = datetime.now()
            etime = nowtime.strftime('%m/%d/%Y %H:%M')
            try:
                execfile('Track.py')
            except:
                print "Error: Can't run 'Track.py'."
                raise
            finally:    
                endtime = datetime.now()
                sleepseconds = (endtime-nowtime).seconds
                sleps = 86400-sleepseconds #24*3600=86400 one day
                print "%d days, at %s"%(a,etime)
                print 'Waiting to run next day...'
                time.sleep(sleps) 
    time.sleep(30) # one minute
